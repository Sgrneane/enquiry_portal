from django.shortcuts import redirect
from django.urls import reverse


#decorators to check whether user is already logged in or not.
def authentication_not_required(view_func,):
    def wrapper(request, *args,**kwargs):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        #if user is already logged in, redirect to the respective dashboard
        redirect_url = reverse(f'management:user_dashboard')
        
        return redirect(redirect_url)
    
    return wrapper


#decorators to verify whether user types is admin or not
def is_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role == 2:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('account:login')
    return wrapper
def is_employee(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role == 2 or request.user.role == 1:
            return view_func(request, *args, **kwargs)
        else:
            return "Permission denied. You are not an admin."
    return wrapper


#decorator to verify whether user type is superadmin or not
def is_superadmin(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role == 1:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('account:login')
    return wrapper


#decorators to check whether user is normal user or not
def is_user(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role == 3:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('account:login')
    return wrapper


