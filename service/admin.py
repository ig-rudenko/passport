from django.contrib import admin

from .models import AgentService, UserService, CustomSecret


@admin.register(AgentService)
class ServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(UserService)
class UserServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(CustomSecret)
class CustomSecretAdmin(admin.ModelAdmin):
    pass
