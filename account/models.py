from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from . import choices

class CustomUser(AbstractUser):
    username = models.CharField(max_length=255,unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15, null=True, 
        validators=[
            RegexValidator(r'^\d{10}$', 'Phone number must be 10 digits')
        ]
    )
    nationality = models.CharField(max_length=2, choices=choices.COUNTRY_CHOICES,default="NP")
    address=models.CharField(max_length=100,null=True)
    created_date=models.DateTimeField(auto_now_add=True)
    USER=3
    SUPERADMIN=1
    COMPLAIN_REVIEWER=2
    ROLE_CHOICES=(
        (USER,'USER'),
        (SUPERADMIN,'SUPERADMIN'),
        (COMPLAIN_REVIEWER,'COMPLAIN REVIEWER')
    )
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES, blank=True, default=3
    )
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username',]

    def __str__(self) -> str:
        return self.email
    
    def role_name(self):
        if self.role==1:
            return 'Superadmin'
        elif self.role==2:
            return 'Enquiry Reviewer'
        elif self.role==3:
            return 'User'
