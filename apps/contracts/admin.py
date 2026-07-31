from django.contrib import admin
from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("employee", "contract_type", "start_date", "end_date", "status")
    list_filter = ("contract_type", "status")
    search_fields = ("employee__matricule", "employee__last_name")
