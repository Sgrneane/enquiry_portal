from django.shortcuts import render, HttpResponse,redirect,get_list_or_404, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage,EmailMultiAlternatives,send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import get_user_model
from social_core.exceptions import AuthAlreadyAssociated
from .models import CustomUser
from .decorators import is_admin,is_superadmin,is_user, authentication_not_required
from .forms import SignupForm, EditUserForm
from .validation import handle_signup_validation
from .choices import COUNTRY_CHOICES


def signup(request):
    """For creating regular users."""
    countries=COUNTRY_CHOICES
    context={
          "countries": countries
    }
    if request.method=='POST':
        form = SignupForm(request.POST)
        
        if form.is_valid():
            nationality=request.POST.get('nationality',None)
            print(nationality)
            email = form.cleaned_data['email'].lower()
            username = form.cleaned_data['username']
            phone = str(form.cleaned_data['phone_number'])
            # password = form.cleaned_data['password']
            form.cleaned_data['role']=3
            if not handle_signup_validation(request, email, username, phone):
                return redirect('account:signup')
            User = get_user_model()
            User.objects.create_user(**form.cleaned_data,nationality=nationality)
            return redirect(reverse('account:login'))
        else:
            messages.error(request, 'User not created! Please fill the form with correct data!')
    else:
        form = SignupForm()
    return render(request, 'account/signup.html',context)

@authentication_not_required
def login_user(request):
    if(request.method == 'POST'):
        email=request.POST['email']
        password=request.POST['password']
        try:
            user=authenticate(request,username=email, password=password)
            if user is not None:
                login(request,user)
                return redirect(reverse('management:user_dashboard'))
            else:
                messages.error(request, 'Incorrect Username or Password!')
                return redirect('account:login')
        except AuthAlreadyAssociated:
            # Handle the case where the Google account is already associated with another account
            return redirect(reverse('management:user_dashboard'))
    else:
        return render(request,'account/login.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect(reverse('management:index'))
@is_superadmin
def all_user(request):
    users=CustomUser.objects.filter(role=3)
    admin_users=CustomUser.objects.exclude(role = 3)
    context={
        'users': users,
        'admin_users': admin_users,
    }
    return render(request,'account/all_users.html',context)
@is_superadmin
def admin_users(request):
    admin_users=CustomUser.objects.exclude(role = 1)
    context={
        'admin_users': admin_users,
    }
    return render(request,'account/admin_userlist.html',context)
def view_user(request,id):
    user=get_object_or_404(CustomUser, id=id)
    context={
        'user': user
    }
    return render(request,'account/view_profile.html',context)
@is_superadmin
def create_admin(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']      
            email = form.cleaned_data['email']
            address=form.cleaned_data['address']
            username = form.cleaned_data['username']
            phone = str(form.cleaned_data['phone_number'])
            role=form.cleaned_data['role']
            password = form.cleaned_data['password']  
            if not handle_signup_validation(request, email, username,phone):
                return redirect('account:create_admin')
            User = get_user_model()
            User.objects.create_user(  
                **form.cleaned_data
                )
            return redirect(reverse('account:all_user'))
        else:
            messages.error(request, 'User not created! Please fill the form with correct data!')

    return render(request,'account/create_admin.html')

@is_superadmin
def edit_user(request,id):
    context={}
    user = get_object_or_404(CustomUser, id=id) if id else None
    user_form = SignupForm(instance=user)
    context={
            'form':user_form
        }
    
    if request.user.id != user.id and request.user.role != 1:  
        messages.error(request, 'Cannot Access!')
        return redirect('management:dashboard')
    
    if request.method == 'POST':
        form=EditUserForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']      
            email = form.cleaned_data['email']
            address=form.cleaned_data['address']
            username = form.cleaned_data['username']
            phone_number = str(form.cleaned_data['phone_number'])
            role = int(request.POST.get('role',None))
            if CustomUser.objects.exclude(id=user.id).filter(username=username).first():
                messages.info(request, f'User with this username "{username}" already exists')
                return redirect('account:edit_user', id=user.id)
        
            if CustomUser.objects.exclude(id=user.id).filter(email=email).first():
                messages.info(request, f'User with this email "{email}" already exists')
                return redirect('account:edit_user', id=user.id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.username=username
            user.phone_number=phone_number
            user.address=address
            user.role=role
            user.password=make_password(form.cleaned_data['password'])
            user.save()
            update_session_auth_hash(request, user) 
            messages.info(request,"User updated Sucessfully.")
            return redirect(reverse('account:all_user'))
        else:
            messages.error(request, "Please fill the form with correct data")
    return render(request, 'account/create_admin.html', context)

def my_account(request):
    return render(request,'account/my_account.html')
@is_superadmin
def delete_user(request, id):
    user=get_object_or_404(CustomUser,id=id)
    user.delete()
    return redirect(reverse('account:all_user'))

def change_password(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('password')
        retype_new_password = request.POST.get('retype_password')
        
        if current_password == '' or new_password == '' or retype_new_password == '':
            messages.error(request, "Please fill all the fields")
            return redirect('account:change_password')
        
        if not user.check_password(current_password):
            messages.error(request, "Incorrect Current Password")
            return redirect('account:change_password')
            
        if new_password != retype_new_password:
            messages.error(request, "New Passwords didn't match")
            return redirect('account:change_password')
        
        if current_password == new_password:
            messages.error(request, "New Password should not be same as Current Password!")
            return redirect('account:change_password')
        
        user.set_password(new_password)
        user.save()
        #update_session_auth_hash(request, user_object) #user is not logged out after changing password
        messages.success(request, "Password Changed Successfully! Login with new password")
        return redirect('account:login')
        
    context = {'user': user}
    return render(request, 'account/change_password.html', context)
"""
def admin_can_change_password(request,id):
    user_to_change_password = get_object_or_404(CustomUser, id=id)
    if request.method == 'POST':
        new_password = request.POST.get('password')
        retype_new_password = request.POST.get('retype_password')
        if new_password != retype_new_password:
            messages.error(request, "New Passwords didn't match")
            return redirect('account:admin_can_change_password',id=id)
        user_to_change_password.set_password(new_password)
        user_to_change_password.save()
        update_session_auth_hash(request, user_to_change_password)
        messages.success(request, "Password Changed Successfully!")
        return redirect('main:all_user')
    context = {'user': user_to_change_password}
    return render(request, 'account/admin_can_change_password.html', context)

def forget_password(request):
    if request.method=='POST':
        user_email=request.POST.get('user_email')
        subject="Hello Prasashan OTP alert!!"
        message=f"Please use given OTP to reset your password."
        msg = EmailMessage(subject,message, to=(user_email))
        msg.send()
        return HttpResponse("Email for OTP sent successfully.")

    return render(request,'account/forget-password.html')

# def generate_otp():
#     otp = ''.join(random.choices('0123456789', k=6))
#     return otp
    
# def otp_verify(request):
#     subject = 'Your OTP Code'
#     message = f'Your OTP code is:'
#     recipient_list = 

#     send_mail(subject, message,recipient_list)

def index(request):
    return render(request, 'account/create_admin.html')"""
