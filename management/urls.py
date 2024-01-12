from django.urls import path
from . import views, api

app_name='management'


urlpatterns = [
    path('', views.index, name='index'),
    path('user-dashboard',views.user_dashboard,name='user_dashboard'),
    path('anonymous-complain',views.anonymous_complain,name='anonymous_complain'),
    path('all-complains',views.all_complains,name='all_complains'),
    path('create-complain',views.create_complain,name='create_complain'),
    path('complain-view/<int:id>',views.view_complain,name='view_complain'),
    path('category-list',views.category_list,name='category_list'),
    path('create-category',views.create_category,name='create_category'),
    path('create-category/<int:id>',views.create_category,name='edit_category'),
    path('create-sub-category',views.create_sub_category, name='create_sub_category'),
     path('edit-sub-category/<int:id>',views.create_sub_category, name='edit_sub_category'),
    path('delete-category/<int:id>',views.delete_category,name='delete_category'),
    path('delete-sub-category/<int:id>',views.delete_sub_category,name='delete_sub_category'),
    path('create-communication/<int:id>',views.create_communication,name='create_communication'),
    path('response/<int:id>',views.response, name="response"),
    path('management/complaint/<int:complain_id>', api.ComplainDetails.as_view(), name='complaint_details'),
    path('search',views.search_complain,name='search_complain'),
    path('send-mail', views.send_mail_celery, name="send_mail"),
    path('create-FAQ', views.create_faq, name="create_faq"),
    path('faqs-list', views.all_faqs, name="all_faqs"),
    path('index-faqs', views.index_faq, name="index_faq"),
    path('index-categories', views.index_categories, name="index_categories"),
    path('pdf',views.pdf_view,name='pdf')
]