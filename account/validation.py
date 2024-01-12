from django.contrib import messages

from .models import CustomUser


def handle_signup_validation(request, email, username,phone):
    """Validations while creating new users."""
    
    if CustomUser.objects.filter(email=email).first():
        messages.info(request, f'User with this email: {email} already exists')
        return False

    if CustomUser.objects.filter(username=username).first():
        messages.info(request, f'User with this username: {username} already exists')
        return False

    # if password != retype_password:
    #     messages.error(request, 'Passwords did not match!')
    #     return False

    if len(phone) < 10:
        messages.error(request, 'Please enter a valid phone number')
        return False

    return True