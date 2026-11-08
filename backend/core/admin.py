from django.contrib import admin
from .models import *
admin.site.register([Profile,SkillAssessment,Course,Enrollment,Opportunity,OpportunityInquiry,Product,SHGGroup,Transaction])
