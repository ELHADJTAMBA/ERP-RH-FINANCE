from rest_framework import serializers
from .models import (
    Account, JournalEntry, Budget, Supplier, PurchaseRequest, PurchaseOrder,
    BankAccount, TreasuryForecast, FixedAsset, Invoice,
)


class AccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = Account
        fields = "__all__"


class JournalEntrySerializer(serializers.ModelSerializer):
    account_code = serializers.CharField(source="account.code", read_only=True)
    account_name = serializers.CharField(source="account.name", read_only=True)

    class Meta:
        model = JournalEntry
        fields = "__all__"
        read_only_fields = ("created_by",)


class BudgetSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    variance = serializers.DecimalField(max_digits=16, decimal_places=2, read_only=True)
    is_over_budget = serializers.BooleanField(read_only=True)

    class Meta:
        model = Budget
        fields = "__all__"


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class PurchaseRequestSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = "__all__"
        read_only_fields = ("requested_by", "approved_by", "approved_at", "status")


class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = "__all__"


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = "__all__"


class TreasuryForecastSerializer(serializers.ModelSerializer):
    net_forecast = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = TreasuryForecast
        fields = "__all__"


class FixedAssetSerializer(serializers.ModelSerializer):
    monthly_depreciation = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    net_book_value = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = FixedAsset
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    balance_due = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = "__all__"
