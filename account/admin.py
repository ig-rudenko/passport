from django.contrib import admin

from .models import User, TempCode


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(TempCode)
class TempCodeAdmin(admin.ModelAdmin):
    pass
