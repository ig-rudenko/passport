from django.contrib import admin

from .models import Service, UserService


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(UserService)
class UserServiceAdmin(admin.ModelAdmin):
    pass
