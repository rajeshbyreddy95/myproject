from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, LandRequest,  LandRequestHistory

admin.site.register(CustomUser)
admin.site.register(LandRequest)
admin.site.register(LandRequestHistory)
