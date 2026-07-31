from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "username", "role", "is_verified", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_verified")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)
    fieldsets = UserAdmin.fieldsets + (
        ("Informations SIRH", {"fields": ("phone", "role", "is_verified")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informations SIRH", {"fields": ("email", "phone", "role")}),
    )
