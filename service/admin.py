from django.contrib import admin

from .models import User, Service, UserService, TempCode


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(UserService)
class UserServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(TempCode)
class TempCodeAdmin(admin.ModelAdmin):
    pass
