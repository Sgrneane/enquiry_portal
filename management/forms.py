from django import forms
from django.core.validators import RegexValidator
from .models import ComplainCategory,ComplainSubCategory,Complain, FAQ
from .choices import status,purpose

#Category and Broad category related Form
class ComplainCategoryForm(forms.ModelForm):
    class Meta:
        model=ComplainCategory
        fields=['english_name','nepali_name']
class ComplainSubCategoryForm(forms.ModelForm):
    class Meta:
        model=ComplainSubCategory
        fields='__all__'
class FAQForm(forms.ModelForm):
    class Meta:
        model=FAQ
        fields='__all__'
    

#Anonymous Form
class AnonymousForm(forms.Form):
    first_name=forms.CharField(max_length=50, required=True)
    last_name=forms.CharField(max_length=50, required=True)
    phone_number= forms.CharField(
        max_length=10,required=True,
        validators=[
            RegexValidator(r'^\d{10}$', 'Phone number must be 10 digits')
        ]
    )
    person_address=forms.CharField(max_length=60,required=True)
    complain_title= forms.CharField(max_length=200,required=True)
    complain_description= forms.CharField(max_length=2000,required=True)
    enquiry_address=forms.CharField(max_length=200,required=True)
    complain_image=forms.ImageField(required=False)

class ComplainForm(forms.ModelForm):
    class meta:
        fields=['broad_category', 'complain_title','complain_description','province','municipality','district']

