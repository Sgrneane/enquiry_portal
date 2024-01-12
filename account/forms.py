from django import forms
from .models import CustomUser


class SignupForm(forms.ModelForm):         
            
    class Meta:
        model=CustomUser
        fields=['first_name','last_name','username','email','address','phone_number','role','password']

class EditUserForm(forms.Form):
    first_name=forms.CharField()
    last_name=forms.CharField()
    username=forms.CharField()
    email=forms.EmailField()
    phone_number=forms.CharField()
    address=forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)