from decimal import Decimal
from django.db import models
from core.models import TimeStampedModel

CURRENCY_CHOICES = [("GNF", "GNF"), ("USD", "USD")]


# ---------------------------------------------------------------------------
# A. Comptabilité Générale
# ---------------------------------------------------------------------------

class Account(TimeStampedModel):
    """Plan comptable paramétrable."""

    class AccountType(models.TextChoices):
        ASSET = "ASSET", "Actif"
        LIABILITY = "LIABILITY", "Passif"
        EXPENSE = "EXPENSE", "Charge"
        REVENUE = "REVENUE", "Produit"
        EQUITY = "EQUITY", "Capitaux propres"

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=10, choices=AccountType.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def balance(self):
        agg = self.entries.aggregate(debit=models.Sum("debit"), credit=models.Sum("credit"))
        return (agg["debit"] or Decimal("0")) - (agg["credit"] or Decimal("0"))


class JournalEntry(TimeStampedModel):
    """Saisie des écritures comptables (entrées/sorties) — Grand livre / Journal."""
    date = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="entries")
    label = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="GNF")
    reference = models.CharField(max_length=100, blank=True)
    reconciled = models.BooleanField(default=False, help_text="Rapprochement bancaire")
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["date", "account"])]

    def __str__(self):
        return f"{self.date} - {self.account.code} - {self.label}"


# ---------------------------------------------------------------------------
# B. Suivi Budgétaire et Analytique
# ---------------------------------------------------------------------------

class Budget(TimeStampedModel):
    """Élaboration des budgets mensuels par poste de dépense + suivi réalisations vs prévisions."""
    department = models.ForeignKey("organizations.Department", on_delete=models.CASCADE, related_name="budgets")
    category = models.CharField(max_length=150, help_text="Poste de dépense: carburant, maintenance, salaires...")
    month = models.PositiveSmallIntegerField()
    year = models.PositiveIntegerField()
    planned_amount = models.DecimalField(max_digits=16, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        unique_together = ("department", "category", "month", "year")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.department.name} - {self.category} ({self.month}/{self.year})"

    @property
    def variance(self):
        return self.actual_amount - self.planned_amount

    @property
    def is_over_budget(self):
        """Alerte de dépassement budgétaire (exigence explicite)."""
        return self.actual_amount > self.planned_amount


# ---------------------------------------------------------------------------
# C. Gestion des Achats et Fournisseurs
# ---------------------------------------------------------------------------

class Supplier(TimeStampedModel):
    class Category(models.TextChoices):
        FUEL = "FUEL", "Carburant"
        TIRES = "TIRES", "Pneus"
        MAINTENANCE = "MAINTENANCE", "Maintenance"
        PPE = "PPE", "EPI"
        OTHER = "OTHER", "Autre"

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=15, choices=Category.choices)
    contact_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, help_text="Évaluation /5")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PurchaseRequest(TimeStampedModel):
    """Demande d'achat + workflow de validation."""

    class RequestStatus(models.TextChoices):
        PENDING = "PENDING", "En attente"
        APPROVED = "APPROVED", "Approuvée"
        REJECTED = "REJECTED", "Rejetée"

    requested_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, related_name="+")
    department = models.ForeignKey("organizations.Department", on_delete=models.CASCADE)
    description = models.TextField()
    estimated_amount = models.DecimalField(max_digits=16, decimal_places=2)
    status = models.CharField(max_length=10, choices=RequestStatus.choices, default=RequestStatus.PENDING)
    approved_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Demande #{self.pk} - {self.department.name}"


class PurchaseOrder(TimeStampedModel):
    """Bons de commande et suivi des livraisons."""

    class OrderStatus(models.TextChoices):
        ISSUED = "ISSUED", "Émis"
        DELIVERED = "DELIVERED", "Livré"
        INVOICED = "INVOICED", "Facturé"
        PAID = "PAID", "Payé"
        CANCELLED = "CANCELLED", "Annulé"

    purchase_request = models.ForeignKey(
        PurchaseRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="orders")
    order_date = models.DateField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="GNF")
    status = models.CharField(max_length=10, choices=OrderStatus.choices, default=OrderStatus.ISSUED)
    payment_due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-order_date"]

    def __str__(self):
        return f"BC-{self.pk} - {self.supplier.name}"


# ---------------------------------------------------------------------------
# D. Gestion de Trésorerie
# ---------------------------------------------------------------------------

class BankAccount(TimeStampedModel):
    bank_name = models.CharField(max_length=150, default="NSIA Banque Guinée")
    account_number = models.CharField(max_length=50, unique=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="GNF")
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"


class TreasuryForecast(TimeStampedModel):
    """Prévisions de trésorerie mensuelle (encaissements/décaissements)."""
    month = models.PositiveSmallIntegerField()
    year = models.PositiveIntegerField()
    expected_inflow = models.DecimalField(max_digits=18, decimal_places=2, default=0, help_text="Encaissements attendus (revenus transport)")
    expected_outflow = models.DecimalField(max_digits=18, decimal_places=2, default=0, help_text="Décaissements attendus (salaires, fournisseurs, charges)")
    actual_inflow = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    actual_outflow = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        unique_together = ("month", "year")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"Prévision trésorerie {self.month}/{self.year}"

    @property
    def net_forecast(self):
        return self.expected_inflow - self.expected_outflow


# ---------------------------------------------------------------------------
# E. Gestion des Immobilisations
# ---------------------------------------------------------------------------

class FixedAsset(TimeStampedModel):
    """Registre des camions et équipements (30 960 000 000 GNF) + amortissement."""

    class AssetCategory(models.TextChoices):
        TRUCK = "TRUCK", "Camion"
        EQUIPMENT = "EQUIPMENT", "Équipement"
        VEHICLE = "VEHICLE", "Véhicule léger"
        OTHER = "OTHER", "Autre"

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=15, choices=AssetCategory.choices)
    registration_number = models.CharField(max_length=50, blank=True, help_text="Immatriculation, pour les camions")
    site = models.ForeignKey("organizations.Site", on_delete=models.SET_NULL, null=True, blank=True)
    acquisition_date = models.DateField()
    acquisition_value = models.DecimalField(max_digits=18, decimal_places=2)
    useful_life_months = models.PositiveIntegerField(help_text="Durée d'amortissement en mois")
    accumulated_depreciation = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.registration_number})" if self.registration_number else self.name

    @property
    def monthly_depreciation(self):
        """Amortissement linéaire mensuel."""
        if not self.useful_life_months:
            return Decimal("0")
        return (self.acquisition_value / self.useful_life_months).quantize(Decimal("1"))

    @property
    def net_book_value(self):
        """Valeur nette comptable = valeur d'acquisition - amortissements cumulés."""
        return max(self.acquisition_value - self.accumulated_depreciation, Decimal("0"))

    def apply_monthly_depreciation(self, save=True):
        """À appeler une fois par mois (tâche planifiée) pour chaque immobilisation active."""
        remaining = self.acquisition_value - self.accumulated_depreciation
        increment = min(self.monthly_depreciation, remaining)
        self.accumulated_depreciation += increment
        if save:
            self.save(update_fields=["accumulated_depreciation"])
        return increment


# ---------------------------------------------------------------------------
# F. Facturation et Revenus
# ---------------------------------------------------------------------------

class Invoice(TimeStampedModel):
    """Facturation du transport de minerai + suivi des paiements clients."""

    class InvoiceStatus(models.TextChoices):
        UNPAID = "UNPAID", "Non payée"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partiellement payée"
        PAID = "PAID", "Payée"
        OVERDUE = "OVERDUE", "En retard"

    client_name = models.CharField(max_length=200)
    invoice_number = models.CharField(max_length=50, unique=True)
    tonnage = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Tonnes de minerai transportées")
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=15, choices=InvoiceStatus.choices, default=InvoiceStatus.UNPAID)
    last_reminder_sent = models.DateField(null=True, blank=True, help_text="Gestion des relances automatiques")

    class Meta:
        ordering = ["-issue_date"]

    def __str__(self):
        return f"{self.invoice_number} - {self.client_name}"

    @property
    def balance_due(self):
        return self.amount - self.amount_paid
