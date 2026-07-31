from django.contrib import admin
from . import models

admin.site.register(models.Account)
admin.site.register(models.JournalEntry)
admin.site.register(models.Budget)
admin.site.register(models.Supplier)
admin.site.register(models.PurchaseRequest)
admin.site.register(models.PurchaseOrder)
admin.site.register(models.BankAccount)
admin.site.register(models.TreasuryForecast)
admin.site.register(models.FixedAsset)
admin.site.register(models.Invoice)
