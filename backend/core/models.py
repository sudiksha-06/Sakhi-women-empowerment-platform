from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=120, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    location = models.CharField(max_length=160, blank=True)
    education = models.CharField(max_length=120, blank=True)
    skills = models.JSONField(default=list, blank=True)
    interests = models.JSONField(default=list, blank=True)
    availability = models.CharField(max_length=120, blank=True)
    language = models.CharField(max_length=8, default="hi")

class SkillAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    statement = models.TextField()
    result = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class Course(models.Model):
    LEVELS = [("Beginner","Beginner"),("Intermediate","Intermediate"),("Advanced","Advanced")]
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=80)
    level = models.CharField(max_length=20, choices=LEVELS, default="Beginner")
    description = models.TextField()
    language = models.CharField(max_length=10, default="hi")
    duration_minutes = models.PositiveIntegerField(default=30)

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress = models.PositiveSmallIntegerField(default=0)
    completed = models.BooleanField(default=False)
    class Meta:
        unique_together = ("user","course")

class Opportunity(models.Model):
    title = models.CharField(max_length=160)
    description = models.TextField()
    location = models.CharField(max_length=160)
    category = models.CharField(max_length=80)
    required_skills = models.JSONField(default=list)
    payment_min = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_max = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    contact = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class OpportunityInquiry(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SHGGroup(models.Model):
    name = models.CharField(max_length=160)
    location = models.CharField(max_length=160, blank=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="managed_groups")
    members = models.ManyToManyField(User, related_name="shg_groups", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    TYPES = [("saving","Saving"),("loan","Loan issued"),("repayment","Loan repayment"),("withdrawal","Withdrawal"),("income","Income"),("expense","Expense")]
    group = models.ForeignKey(SHGGroup, on_delete=models.CASCADE, related_name="transactions")
    member = models.ForeignKey(User, on_delete=models.PROTECT, related_name="shg_transactions")
    recorded_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="recorded_transactions")
    transaction_type = models.CharField(max_length=20, choices=TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    idempotency_key = models.CharField(max_length=80, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
