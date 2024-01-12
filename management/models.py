from django.db import models
from account.models import CustomUser
import hashlib
import shortuuid
from django.core.validators import FileExtensionValidator,MaxLengthValidator,MaxValueValidator
from .choices import status,purpose

# Create your models here.    
class ComplainCategory(models.Model):
    english_name=models.CharField(max_length=60,unique=True)
    nepali_name=models.CharField(max_length=200,null=True)
    
    def __str__(self):
        return self.english_name

class ComplainSubCategory(models.Model):
    english_name=models.CharField(max_length=60,unique=True)
    nepali_name=models.CharField(max_length=100, null=True)
    def __str__(self):
        return self.english_name



class AnonymousUser(models.Model):
    """Personal Information"""
    first_name=models.CharField(max_length=50,default='abc')
    last_name=models.CharField(max_length=50,null=True)
    phone_number=models.CharField(max_length=13)
    address=models.CharField(max_length=50,null=True)

    def __str__(self):
        return self.first_name
class Complain(models.Model):
    ticket_no=models.CharField(max_length=22, unique=True)
    complain_category = models.ForeignKey(ComplainCategory,on_delete=models.CASCADE,related_name='related_complain',null=True)
    complain_sub_category=models.ForeignKey(ComplainSubCategory,on_delete=models.CASCADE,null=True,related_name='complain_sub_category')
    complain_title=models.CharField(max_length=300)
    complain_description=models.TextField()
    complain_image=models.ImageField()
    address=models.CharField(max_length=200,null=True)
    complain_status=models.PositiveBigIntegerField(choices=status,default=1)
    purpose=models.PositiveBigIntegerField(choices=purpose,default=None)
    is_anonymous=models.OneToOneField(AnonymousUser, null=True, on_delete=models.CASCADE)
    created_by=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name='user_complains')
    
    assigned_by=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name='assigned_complain')
    assigned_to=models.ManyToManyField(CustomUser,related_name='is_available',default=None)
    assigned_date=models.DateTimeField(blank=True,null=True)
    created_date=models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.complain_title
    def save(self, *args, **kwargs):
        if not self.ticket_no:
            unique_id = shortuuid.uuid()
            complain_count=Complain.objects.count()
            digits_only = ''.join(filter(str.isdigit, unique_id))
            complain_category_id = self.complain_category.id if self.complain_category else 'NA'
            self.ticket_no = f'DFTQC-C{complain_category_id}-{str(complain_count)+digits_only[:4]}'

        super(Complain, self).save(*args, **kwargs)
    def get_status(self):
        if self.complain_status == 1:
            return 'Pending'
        elif self.complain_status == 3:
            return 'Responded'
        elif self.complain_status == 4:
            return "Rejected"
        else:
            return 'Processing'
        

    def get_purpose(self):
        if self.purpose == 1:
            return 'Export'
        elif self.purpose == 2:
            return 'Import'
        elif self.purpose == 3:
            return 'Domestic'
        elif self.purpose == 4:
            return 'Regulations'
        else:
            return 'Others'
    class Meta:
        ordering=['-id']
class Communication(models.Model):
    complain = models.ForeignKey(Complain,on_delete=models.CASCADE,related_name='complain_communication')
    communication_creator=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='creator',default=None)
    message=models.TextField(null=True)
    image=models.ImageField(null=True)

class Response(models.Model):
    created_by=models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True)
    response_description=models.TextField()
    complain=models.ForeignKey(Complain,on_delete=models.CASCADE,related_name='response')
    response_image=models.ImageField(null=True)


class FAQ(models.Model):
    question=models.TextField()
    answer=models.TextField()
    