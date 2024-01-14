from django.shortcuts import render,HttpResponse,get_object_or_404,get_list_or_404,redirect
from django.db.models import Count
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import ComplainCategory,ComplainSubCategory, AnonymousUser,Complain, Communication, Response, FAQ
from account.models import CustomUser
from .forms import AnonymousForm,ComplainCategoryForm,ComplainSubCategoryForm, FAQForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from account.decorators import authentication_not_required,is_admin,is_superadmin,is_user, is_employee
from django.contrib.auth.decorators import login_required
from .tasks import send_notification_mail
from .choices import purpose

# Create your views here.
def index(request):
    total_counts=Complain.objects.count()
    plant_health_count=Complain.objects.filter(complain_category__english_name='Plant Health').count()
    animal_health_count=Complain.objects.filter(complain_category__english_name='Animal Health').count()
    food_safety_count=Complain.objects.filter(complain_category__english_name='Food Safety').count()
    others_count=Complain.objects.filter(complain_category__english_name='Others').count()
    context={
        'total_counts':total_counts,
        'plant_health_count': plant_health_count,
        'animal_health_count':animal_health_count,
        'food_safety_count':food_safety_count,
        'others_count':others_count,

    }
    return render(request,'management/index.html',context)

def user_dashboard(request):
    user=request.user
    if user.role==3:
        total_complains=Complain.objects.filter(created_by=user).count()
        plant_health_count=Complain.objects.filter(Q(complain_category__english_name='Plant Health') &
                                                        Q(created_by=user)).count()
        animal_health_count=Complain.objects.filter(Q(complain_category__english_name='Animal Health') &
                                                           Q(created_by=user)).count()
        food_safety_count=Complain.objects.filter(Q(complain_category__english_name='Food Safety') &
                                           Q(created_by=user)).count()
        others_count=Complain.objects.filter(Q(complain_category__english_name='Others') &
                                             Q(created_by=user)).count()
        pending_complains_count=Complain.objects.filter(Q(complain_status=1) &
                                                        Q(created_by=user)).count()
        processing_complains_count=Complain.objects.filter(Q(complain_status=2) &
                                                           Q(created_by=user)).count()
        responded_complains_count=Complain.objects.filter(Q(complain_status=3) &
                                                          Q(created_by=user)).count()
        rejected_complains_count=Complain.objects.filter(Q(complain_status=4) &
                                                         Q(created_by=user)).count()
    else:
        total_complains=Complain.objects.count()
        plant_health_count=Complain.objects.filter(complain_category__english_name='Plant Health').count()
        animal_health_count=Complain.objects.filter(complain_category__english_name='Animal Health').count()
        food_safety_count=Complain.objects.filter(complain_category__english_name='Food Safety').count()
        others_count=Complain.objects.filter(complain_category__english_name='Others').count()
        pending_complains_count=Complain.objects.filter(complain_status=1).count()
        processing_complains_count=Complain.objects.filter(complain_status=2).count()
        responded_complains_count=Complain.objects.filter(complain_status=3).count()
        rejected_complains_count=Complain.objects.filter(complain_status=4).count()
    context={
        'total_complains':total_complains,
        'plant_health_count': plant_health_count,
        'animal_health_count':animal_health_count,
        'food_safety_count':food_safety_count,
        'others_count':others_count,
        'pending_complains_count':pending_complains_count,
        'processing_complains_count':processing_complains_count,
        'responded_complains_count':responded_complains_count,
        'rejected_complains_count':rejected_complains_count,

    }
    return render(request,'dashboard.html',context)

#Category and Broad category related Views.
def category_list(request):
    sub_categories=ComplainSubCategory.objects.all()
    categories = ComplainCategory.objects.all()
    context={
        'categories':categories,
        'sub_categories': sub_categories
    }
    return render(request,'management/category_list.html',context)
@is_superadmin
def create_category(request,id=None):
    sub_categories=ComplainSubCategory.objects.all()
    if id:
        category=ComplainCategory.objects.get(id=id)
    else:
        category=None
    if request.method =='POST':
        form=ComplainCategoryForm(request.POST)
        if id:
            #for editing Purpose
            category=ComplainCategory.objects.get(id=id)
            english_name=form.data['english_name']
            nepali_name= form.data['nepali_name']
            category.english_name=english_name
            category.nepali_name=nepali_name
            category.save()
            messages.info(request,"Category Updated Successfully")
            return redirect(reverse('management:category_list'))
        else:
            if form.is_valid():
                english_name=form.cleaned_data['english_name']
                nepali_name= form.cleaned_data['nepali_name']
                complain_category,created=ComplainCategory.objects.get_or_create(
                    english_name=english_name,
                    nepali_name=nepali_name,
                )
            
                return redirect('management:category_list')
            else:
                messages.error(request,"please fill the form correctly.")
                return redirect(reverse('management:create_category'))
    else:
        context={
            'sub_categories':sub_categories,
            'category':category,
        }
        return render(request,'management/add_category.html',context)
@is_superadmin
def create_sub_category(request,id=None):
    categories=ComplainCategory.objects.all()
    if id:
        sub_category=ComplainSubCategory.objects.get(id=id)
    else:
        sub_category=None
    context={
        'categories':categories,
        'sub_category':sub_category
    }
    if request.method=='POST':
        form=ComplainSubCategoryForm(request.POST)
        if id:
            sub_category=ComplainSubCategory.objects.get(id=id)
            english_name=form.data['english_name']
            nepali_name=form.data['nepali_name']
            sub_category.english_name=english_name
            sub_category.nepali_name=nepali_name
            sub_category.save()
            messages.info(request,"Sub Category has been Updated Successfully.")
            return redirect(reverse('management:category_list'))
        else:
            if form.is_valid():
                sub_category_name=form.cleaned_data['english_name']
                nepali_name=form.cleaned_data['nepali_name']
                ComplainSubCategory.objects.create(
                    english_name=sub_category_name,
                    nepali_name=nepali_name,
                )
                messages.info(request,"Sub Category has been created Successfully.")
                return redirect('management:category_list')
            else:
                messages.error(request,'Please fill all fields to create subcategory.')
                return redirect(reverse('management:add_subcategory'))
    else:
        return render(request,'management/add_subcategory.html',context)
@is_superadmin
def delete_category(request,id):
    category=ComplainCategory.objects.get(id=id)
    category.delete()
    messages.info(request,"Category has been deleted Successfully.")
    return redirect(reverse('management:category_list'))
@is_superadmin
def delete_sub_category(request,id):
    sub_category=ComplainSubCategory.objects.get(id=id)
    sub_category.delete()
    messages.info(request,"Sub Category has been deleted Successfully.")
    return redirect(reverse('management:category_list'))

#Anonymous Complain related views
def anonymous_complain(request):  
    complain_category=ComplainCategory.objects.all()
    complain_purpose=purpose
    context={
            'complain_category': complain_category,
            'complain_purpose':complain_purpose,
            } 
    if request.method == 'POST':
        form=AnonymousForm(request.POST,request.FILES)
        if form.is_valid():
            person_first_name=form.cleaned_data['first_name']
            person_last_name=form.cleaned_data['last_name']
            person_phone_number=form.cleaned_data['phone_number']
            person_address=form.cleaned_data['person_address']
            complain_title=form.cleaned_data['complain_title']
            address=form.cleaned_data['enquiry_address']
            
            enquiry_category=int(request.POST.get('complain_category',None))
            enquiry_object_instance=ComplainCategory.objects.get(id=enquiry_category)
            complain_description=form.cleaned_data['complain_description']
            complain_image=form.cleaned_data['complain_image']
            enquiry_purpose=int(request.POST.get('purpose',None))
            anonymous_object={
            "first_name":person_first_name,
            "last_name": person_last_name,
            "phone_number":person_phone_number,
            "address":person_address
            }
            complain={
                "complain_category":enquiry_object_instance,
                "address":address,
                "complain_title": complain_title,
                "purpose":enquiry_purpose,
                "complain_description":complain_description,
                "complain_image": complain_image,
            }
            user_info=AnonymousUser.objects.create(**anonymous_object)
            complain_obj=Complain.objects.create(is_anonymous=user_info,**complain)
            mail_context={
                'complain_obj':complain_obj,
            }
            admin_users=CustomUser.objects.filter(role =1)
            email_lists=[admin_user.email for admin_user in admin_users]
            html_content = render_to_string('management/mail_template.html',mail_context)
            try:
                for email in email_lists:
                    send_notification_mail.delay(email,html_content)
                messages.info(request,f"<strong>Success!</strong> Your Complain has been registered successfully.<br> Save and search the complain token <Strong>{complain_obj.ticket_no}</strong> for further information.")
            finally:
                return redirect(reverse('management:index'))
        else:
            additional_context={
                'form':form,
                'errors':form.errors
            }
            context.update(additional_context)
            print(form.errors)
            return render(request,"management/anonymous_complain.html",context)
    else:
        return render(request,'management/anonymous_complain.html',context)

@is_user
def create_complain(request):
    user=request.user
    complain_category=ComplainCategory.objects.all()
    complain_purpose=purpose
    context={
            'complain_category': complain_category,
            'complain_purpose':complain_purpose,
            }
    if request.method == 'POST':
        complain_category=int(request.POST.get('complain_category',None))
        complain_title=request.POST.get('complain_title',None)
        complain_address=request.POST.get('address',None)
        complain_description=request.POST.get('complain_description',None)
        complain_image=request.FILES.get('complain_image',None)
        complain_category_instance = ComplainCategory.objects.get(id=complain_category)
        complain_purpose=int(request.POST.get('purpose',None))
        complain={
            "complain_category":complain_category_instance,
            "complain_title": complain_title,
            "complain_description":complain_description,
            "purpose":complain_purpose,
            "complain_image":complain_image,
            "address":complain_address
        }
        complain_obj=Complain.objects.create(created_by=user,**complain)
        mail_context={
                'complain_obj':complain_obj,
            }
        admin_users=CustomUser.objects.filter(role =1)
        email_lists=[admin_user.email for admin_user in admin_users]
        html_content = render_to_string('management/mail_template.html',mail_context)
        try:
            for email in email_lists:
                send_notification_mail.delay(email,html_content)
        finally:
            return redirect(reverse('management:all_complains'))
    return render(request,'management/create_complain.html',context)

@login_required
def all_complains(request):
    user=request.user
    if user.role == 1:
        complains=Complain.objects.all()
        pending_complains=Complain.objects.filter(complain_status = 1)
        processing_complains=Complain.objects.filter(complain_status=2)
        responded_complains=Complain.objects.filter(complain_status=3)
    if user.role == 2:
        complains=Complain.objects.filter(assigned_to = user)
        pending_complains=Complain.objects.filter(assigned_to = user,complain_status=1 )
        processing_complains=Complain.objects.filter(assigned_to = user, complain_status=2)
        responded_complains=Complain.objects.filter(assigned_to = user,complain_status=3)
    if user.role == 3:
        complains=Complain.objects.filter(created_by=user)
        pending_complains=Complain.objects.filter(created_by=user,complain_status=1)
        processing_complains=Complain.objects.filter(created_by = user, complain_status=2)
        responded_complains=Complain.objects.filter(created_by = user,complain_status=3)
    context={
        'complains':complains,
        'pending_complains':pending_complains,
        'processing_complains': processing_complains,
        'responded_complains': responded_complains
    }
    return render(request,'management/complain_list.html',context)

@login_required
def view_complain(request,id):
    complain=get_object_or_404(Complain,id=id)
    complain_sub_categories=ComplainSubCategory.objects.all()
    complain_reviewers=get_list_or_404(CustomUser, role=2)
    context={
        'complain_sub_categories':complain_sub_categories,
        'complain':complain,
        'complain_reviewers':complain_reviewers,
    }
    if request.method=='POST':
        if 'forward_button' in request.POST:
            admin_message=request.POST.get('admin_message',None)
            assigned_to=request.POST.getlist('assigned_to')
            image=request.FILES.get('communication_image',None)
            if not complain.complain_category:
                complain_category=int(request.POST.get('complain_category',None))
                complain_sub_category=int(request.POST.get('complain_sub_category',None))
                complain_category_instance=ComplainCategory.objects.get(id=complain_category)
                complain_sub_category_instance=ComplainSubCategory.objects.get(id=complain_sub_category)
                complain.complain_category=complain_category_instance
                complain.complain_sub_category=complain_sub_category_instance
            customuser_instances=CustomUser.objects.filter(id__in=assigned_to)
            complain.assigned_to.set(customuser_instances)
            complain.assigned_by=request.user
            complain.complain_status=2
            
            complain.assigned_date=timezone.now()
            if admin_message:
                Communication.objects.create(
                    complain=complain,
                    communication_creator=request.user,
                    message=admin_message,
                    image=image
                )
            complain.save()
            return redirect('management:view_complain',id=complain.id)
    return render(request,'management/view_complain.html',context)


@is_employee
def create_communication(request,id):
    complain=get_object_or_404(Complain,id=id)
    if request.method =='POST':
        message=request.POST.get('communication_message')
        image=request.FILES.get('communication_image',None)
        data={
            'complain':complain,
            'communication_creator': request.user,
            'message':message,
            'image':image
        }
        Communication.objects.create(**data)
        # mail_context={
        #     'complain_obj':complain,
        # }
        # admin_users=CustomUser.objects.filter(role =1)
        # html_content = render_to_string('management/mail_template.html',mail_context)
        # send_notification_mail.delay(communication_to.email,html_content)
        return redirect("management:view_complain",id=complain.id)
@is_superadmin  
def response(request,id):
    user=request.user
    complain=Complain.objects.get(id=id)
    if request.method=='POST':
        message=request.POST.get('response_message',None)
        image=request.FILES.get('response_image',None)
        if 'reject' in request.POST:
            complain.complain_status = 4
            complain.save()
        if 'response' in request.POST:
            complain.complain_status = 3
            complain.save()
        Response.objects.create(
                created_by=user,
                response_description=message,
                complain=complain,
                response_image=image,
            )
        return redirect(reverse('management:all_complains'))
    return redirect(reverse('management:all_complains'))

def search_complain(request):
    if request.method=='POST':
        search=request.POST['search']
        try:
            complain=Complain.objects.get(ticket_no=search)
        except ObjectDoesNotExist:
            complain = None
        if complain:
            context={
                'complain':complain
            }
            return render(request,'management/search.html',context)
        else:
            messages.info(request,f"<strong>Sorry!</strong> Complain with this ticket number({search}) doesn't exist.")
            return redirect(reverse('management:index'))
        
def index_categories(request):
    sub_categories=ComplainSubCategory.objects.all()
    categories = ComplainCategory.objects.all()
    context={
        'categories':categories,
        'sub_categories': sub_categories
    }
    return render(request,'management/index_categories.html',context)  

def all_faqs(request):
    faqs=FAQ.objects.all()
    context={
        'faqs':faqs
    }
    return render(request,'management/faqs_list.html',context)
def index_faq(request):
    faqs=FAQ.objects.all()
    context={
        'faqs':faqs
    }
    return render(request,'management/index_faq.html',context)
def create_faq(request):
    if request.method=='POST':
        form=FAQForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('management:all_faqs'))
        else:
            messages.info(request,'Please fill form correctly')
            return redirect(reverse('management:create_faq'))
    
    return render(request,'management/create_faq.html')
        