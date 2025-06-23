from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.
class User(models.Model):
    USER_TYPE_CHOICES = [
        ('Patient', 'Patient'),
        ('Doctor', 'Doctor'),
    ]
    
    name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    mobile = models.BigIntegerField()
    password = models.CharField(max_length=128)  # Increased length for hashed password
    usertype = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default="Patient")
    profile = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    def __str__(self):
        return self.name

    

# Doctor Profile model
class Add(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_profiles')
    dname = models.CharField(max_length=30)
    dmobile = models.BigIntegerField()
    dexperience = models.IntegerField()
    department = models.CharField(max_length=50, default='')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    follow_up_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    emergency_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    dprofile = models.ImageField(upload_to='doctor_profiles/', null=True, blank=True)

    def __str__(self):
        return f"{self.dname} - {self.department}"

    

# Choices for Appointment model
DOCTOR_CHOICES = [
    ('Dr. Smith', 'Dr. Smith'),
    ('Dr. Johnson', 'Dr. Johnson'),
    ('Dr. Williams', 'Dr. Williams'),
    ('Dr. Brown', 'Dr. Brown'),
    ('Dr. Jones', 'Dr. Jones'),
]

DEPARTMENT_CHOICES = [
    ('Cardiology', 'Cardiology'),
    ('Neurology', 'Neurology'),
    ('Pediatrics', 'Pediatrics'),
    ('Orthopedics', 'Orthopedics'),
    ('Dermatology', 'Dermatology'),
]

# models.py
class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    doctor = models.ForeignKey(Add,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    age = models.IntegerField()
    date_of_birth = models.DateField()
    address = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, default='Pending')
    


    def __str__(self):
        return self.name

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
        ('razorpay', 'Razorpay')
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded')
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} - {self.amount} ({self.status})"

# Add the Doctor model after the User model
