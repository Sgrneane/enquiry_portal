from django.contrib import admin
from .models import Complain,ComplainCategory,ComplainSubCategory,Communication,Response,AnonymousUser
# Register your models here.
admin.site.register(Complain)
admin.site.register(ComplainCategory)
admin.site.register(ComplainSubCategory)
admin.site.register(AnonymousUser)
admin.site.register(Communication)
admin.site.register(Response)