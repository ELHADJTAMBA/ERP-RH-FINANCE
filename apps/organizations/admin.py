from django.contrib import admin
from .models import Site, Department


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "site_type", "is_active")
    list_filter = ("site_type", "is_active")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "site", "manager", "is_active")
    list_filter = ("site", "is_active")
