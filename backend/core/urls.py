from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
router=DefaultRouter()
router.register("courses",CourseViewSet,basename="courses")
router.register("opportunities",OpportunityViewSet,basename="opportunities")
router.register("products",ProductViewSet,basename="products")
router.register("groups",GroupViewSet,basename="groups")
router.register("transactions",TransactionViewSet,basename="transactions")
urlpatterns=[
 path("auth/register/",RegisterView.as_view()),
 path("profile/",profile_view),
 path("skills/",skills_view),
 path("enrollments/",EnrollmentView.as_view()),
 path("products/ai-description/",describe_product),
 path("pricing/",pricing),
 path("voice/intent/",voice_intent),
 path("finance/summary/",financial_summary),
 path("groups/<int:group_id>/members/",members_view),
 path("",include(router.urls)),
]
