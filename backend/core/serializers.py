from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, SkillAssessment, Course, Enrollment, Opportunity, OpportunityInquiry, Product, SHGGroup, Transaction

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = User
        fields = ("username","email","password","full_name")
    def create(self, validated):
        full_name = validated.pop("full_name", "")
        user = User.objects.create_user(**validated)
        Profile.objects.create(user=user, full_name=full_name)
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ("user",)

class SkillAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillAssessment
        fields = ("id","statement","result","created_at")
        read_only_fields = ("id","result","created_at")

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"

class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    class Meta:
        model = Enrollment
        fields = ("id","course","course_title","progress","completed")

class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.username", read_only=True)
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("owner",)

class SHGGroupSerializer(serializers.ModelSerializer):
    member_names = serializers.SerializerMethodField()
    class Meta:
        model = SHGGroup
        fields = ("id","name","location","admin","members","member_names","created_at")
        read_only_fields = ("admin",)
    def get_member_names(self, obj):
        return list(obj.members.values_list("username", flat=True))

class TransactionSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.username", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.username", read_only=True)
    class Meta:
        model = Transaction
        fields = ("id","group","member","member_name","recorded_by_name","transaction_type","amount","date","description","idempotency_key","created_at")
        read_only_fields = ("id","recorded_by","created_at")
