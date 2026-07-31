from django.contrib import admin
from .models import SalaryGrid, PayrollRun, Payslip

admin.site.register(SalaryGrid)
admin.site.register(PayrollRun)
admin.site.register(Payslip)
