from django.urls import path
from . import views

app_name='account'
urlpatterns = [
    path('login/',views.login_user, name='login'),
    path('signup/',views.signup, name='signup'),
    path('all-user',views.all_user,name='all_user'),
    path('admin_user',views.admin_users,name='admin_user'),
    path('create-admin',views.create_admin,name='create_admin'),
    path('edit-admin/<int:id>',views.edit_user,name='edit_user'),
    path('user/<int:id>',views.view_user,name='view_user'),
    path('user/delete-user/<int:id>',views.delete_user,name='delete_user'),
    path('change_password',views.change_password,name='change_password'),
    path('my-account',views.my_account, name='my_account'),
    path('logout/',views.logout_user, name='logout_user'),
]