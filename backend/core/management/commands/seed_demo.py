from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import *
class Command(BaseCommand):
    help="Create Sakhi demo account, courses, opportunities, products and sample SHG data"
    def handle(self,*args,**kwargs):
        user,_=User.objects.get_or_create(username="sakhi_demo",defaults={"email":"demo@sakhi.local"})
        if not user.has_usable_password() or not user.check_password("Sakhi@12345"):
            user.set_password("Sakhi@12345"); user.save()
        Profile.objects.get_or_create(user=user,defaults={"full_name":"Sakhi Demo","location":"Patna, Bihar","skills":["silai","handicraft"]})
        courses=[
          (" सिलाई की बुनियाद","Tailoring","Beginner","माप लेना, कपड़ा काटना और बुनियादी सिलाई सीखें।"),
          ("ब्लाउज डिजाइनिंग","Tailoring","Intermediate","ब्लाउज की फिटिंग और डिजाइन के तरीके।"),
          ("खाद्य उत्पाद पैकेजिंग","Food","Beginner","अचार और पापड़ की सुरक्षित पैकेजिंग।"),
          ("Digital Product Photography","Business","Beginner","Mobile se product photos banana."),
          ("SHG Bookkeeping","Finance","Beginner","Savings, loans aur ledger maintain karna."),
        ]
        for title,cat,level,desc in courses: Course.objects.get_or_create(title=title,defaults={"category":cat,"level":level,"description":desc})
        opps=[
          ("Blouse stitching orders","Local boutique needs blouse stitching support.","Patna","Tailoring",["silai","tailoring"],250,500,"Demo contact: 9000000001"),
          ("Homemade papad production","SHG group order for packaged papad.","Danapur","Food",["cooking","food"],300,700,"Demo contact: 9000000002"),
          ("Embroidered bags","Handmade embroidered bags for a local gift shop.","Patna","Handicraft",["embroidery","handicraft"],400,900,"Demo contact: 9000000003"),
        ]
        for title,desc,loc,cat,skills,lo,hi,contact in opps:
            Opportunity.objects.get_or_create(title=title,defaults={"description":desc,"location":loc,"category":cat,"required_skills":skills,"payment_min":lo,"payment_max":hi,"contact":contact})
        Product.objects.get_or_create(owner=user,name="Handmade embroidered pouch",defaults={"category":"Handicraft","description":"Demo handmade pouch","price":250,"quantity":12})
        group,_=SHGGroup.objects.get_or_create(name="Sakhi Pragati SHG",defaults={"location":"Patna, Bihar","admin":user})
        group.members.add(user)
        self.stdout.write(self.style.SUCCESS("Demo data ready. Login: sakhi_demo / Sakhi@12345"))
