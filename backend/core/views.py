import uuid
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.utils.timezone import localdate
from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import *
from .serializers import *
from .ai import assess_skill, product_description, assistant_reply

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

@api_view(["GET","PATCH"])
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "GET": return Response(ProfileSerializer(profile).data)
    serializer = ProfileSerializer(profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True); serializer.save()
    return Response(serializer.data)

@api_view(["POST","GET"])
def skills_view(request):
    if request.method == "GET":
        return Response(SkillAssessmentSerializer(SkillAssessment.objects.filter(user=request.user).order_by("-created_at"), many=True).data)
    statement = request.data.get("statement","").strip()
    if not statement: return Response({"error":"Please describe your skills."}, status=400)
    result = assess_skill(statement)
    item = SkillAssessment.objects.create(user=request.user, statement=statement, result=result)
    return Response(SkillAssessmentSerializer(item).data, status=201)

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    @action(detail=True, methods=["post"])
    def enroll(self, request, pk=None):
        course = self.get_object()
        enrollment, _ = Enrollment.objects.get_or_create(user=request.user, course=course)
        return Response(EnrollmentSerializer(enrollment).data)

class EnrollmentView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    def get_queryset(self): return Enrollment.objects.filter(user=self.request.user)

class OpportunityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    def get_queryset(self):
        qs = super().get_queryset()
        location = self.request.query_params.get("location")
        category = self.request.query_params.get("category")
        if location: qs = qs.filter(location__icontains=location)
        if category: qs = qs.filter(category__icontains=category)
        return qs
    @action(detail=True, methods=["post"])
    def inquire(self, request, pk=None):
        item = self.get_object()
        inquiry = OpportunityInquiry.objects.create(opportunity=item,user=request.user,message=request.data.get("message",""))
        return Response({"status":"inquiry_submitted","id":inquiry.id},status=201)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    def get_queryset(self):
        if self.request.query_params.get("mine") == "1": return Product.objects.filter(owner=self.request.user)
        return Product.objects.all()
    def perform_create(self, serializer): serializer.save(owner=self.request.user)

@api_view(["POST"])
def describe_product(request):
    name=request.data.get("name","Handmade product"); category=request.data.get("category","handicraft")
    lang=request.data.get("language","en")
    return Response({"description":product_description(name,category,lang),"keywords":[category,"handmade","local","gift"]})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pricing(request):
    try:
        material=Decimal(str(request.data.get("material",0))); labour=Decimal(str(request.data.get("labour",0)))
        packaging=Decimal(str(request.data.get("packaging",0))); other=Decimal(str(request.data.get("other",0)))
        margin=Decimal(str(request.data.get("margin",30)))
        if min(material,labour,packaging,other,margin) < 0 or margin > 500: raise ValueError()
        cost=material+labour+packaging+other
        profit=(cost*margin/100).quantize(Decimal("0.01"))
        return Response({"total_cost":str(cost),"profit":str(profit),"selling_price":str(cost+profit),"margin_percent":str(margin)})
    except Exception: return Response({"error":"Enter valid non-negative costs and a reasonable margin."},status=400)

class GroupViewSet(viewsets.ModelViewSet):
    serializer_class=SHGGroupSerializer
    def get_queryset(self): return SHGGroup.objects.filter(members=self.request.user) | SHGGroup.objects.filter(admin=self.request.user)
    def perform_create(self, serializer):
        group=serializer.save(admin=self.request.user); group.members.add(self.request.user)
    @action(detail=True,methods=["post"])
    def add_member(self,request,pk=None):
        group=self.get_object()
        if group.admin != request.user: return Response({"error":"Only group admin can add members."},status=403)
        username=request.data.get("username","")
        try: member=User.objects.get(username=username)
        except User.DoesNotExist: return Response({"error":"Member not found."},status=404)
        group.members.add(member); return Response({"status":"member_added"})

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class=TransactionSerializer
    def get_queryset(self):
        return Transaction.objects.filter(group__members=self.request.user).select_related("member","recorded_by","group")
    @action(detail=False,methods=["post"])
    def create_confirmed(self,request):
        data=request.data
        group_id=data.get("group"); member_id=data.get("member"); key=data.get("idempotency_key")
        if not key: return Response({"error":"Confirmation key required."},status=400)
        try:
            group=SHGGroup.objects.get(id=group_id,members=request.user)
            member=User.objects.get(id=member_id)
            if not group.members.filter(id=member.id).exists(): raise ValueError()
            amount=Decimal(str(data.get("amount")))
            if amount <= 0: raise ValueError()
        except Exception: return Response({"error":"Invalid group, member, or amount."},status=400)
        if Transaction.objects.filter(idempotency_key=key).exists():
            existing=Transaction.objects.get(idempotency_key=key)
            return Response(TransactionSerializer(existing).data)
        with transaction.atomic():
            item=Transaction.objects.create(group=group,member=member,recorded_by=request.user,
                transaction_type=data.get("transaction_type","saving"),amount=amount,
                date=data.get("date") or localdate(),description=data.get("description",""),
                idempotency_key=key)
        return Response(TransactionSerializer(item).data,status=201)

@api_view(["POST"])
def voice_intent(request):
    text=request.data.get("text","").strip()
    if not text: return Response({"error":"Text is required."},status=400)
    return Response(assistant_reply(text))

@api_view(["GET"])
def financial_summary(request):
    group_id=request.query_params.get("group")
    groups=SHGGroup.objects.filter(members=request.user)
    if group_id: groups=groups.filter(id=group_id)
    tx=Transaction.objects.filter(group__in=groups)
    def total(types):
        return tx.filter(transaction_type__in=types).aggregate(v=Sum("amount"))["v"] or Decimal("0")
    savings=total(["saving"]); loans=total(["loan"]); repayments=total(["repayment"])
    return Response({"total_savings":str(savings),"total_loans_issued":str(loans),
      "total_repayments":str(repayments),"outstanding_loans":str(loans-repayments),
      "total_income":str(total(["income"])),"total_expenses":str(total(["expense","withdrawal"]))})

@api_view(["GET"])
def members_view(request, group_id):
    try: group=SHGGroup.objects.get(id=group_id,members=request.user)
    except SHGGroup.DoesNotExist: return Response({"error":"Group not found"},status=404)
    return Response([{"id":u.id,"username":u.username,"full_name":getattr(getattr(u,"profile",None),"full_name","")} for u in group.members.all()])
