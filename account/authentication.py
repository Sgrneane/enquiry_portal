from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import CustomUser

#Authenticating Users by both email and username
class EmailOrPhoneBackend(ModelBackend):
    def get_user(self, user_id):
        CustomUser=get_user_model()
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
    def authenticate(self, request, username=None, password=None,**kwargs):
        CustomUser=get_user_model()
        try:
            user = CustomUser.objects.get(
                Q(username__iexact=username)| Q(email__iexact=username) | Q(phone_number__iexact= username))
            if user.check_password(password):
                return user
            return None
        except (CustomUser.DoesNotExist, CustomUser.MultipleObjectsReturned):
            return None
    
