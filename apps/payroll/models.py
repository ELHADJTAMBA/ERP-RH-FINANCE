from decimal import Decimal
from django.db import models
from core.models import TimeStampedModel

# Taux légaux (Guinée) - paramétrables ici pour rester simples à ajuster.
CNSS_EMPLOYEE_RATE = Decimal("0.05")   # 5% part salariale CNSS (paramétrable)
TAX_BRACKETS = [  # barème simplifié de l'impôt sur salaire (ITS) - à ajuster selon réglementation en vigueur
    (Decimal("1000000"), Decimal("0.00")),
    (Decimal("5000000"), Decimal("0.10")),
    (Decimal("999999999"), Decimal("0.15")),
]


class SalaryGrid(TimeStampedModel):
    """Paramétrage des grilles salariales par poste (2 000 000 à 15 000 000 GNF)."""
    position = models.CharField(max_length=150, unique=True)
    department = models.ForeignKey(
        "organizations.Department", on_delete=models.SET_NULL, null=True, blank=True, related_name="salary_grids"
    )
    min_salary = models.DecimalField(max_digits=14, decimal_places=2)
    max_salary = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="GNF", choices=[("GNF", "GNF"), ("USD", "USD")])

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.position} ({self.min_salary} - {self.max_salary} {self.currency})"


class PayrollRun(TimeStampedModel):
    """Traitement de paie mensuel (lot) — regroupe les bulletins d'une période."""

    class RunStatus(models.TextChoices):
        DRAFT = "DRAFT", "Brouillon"
        VALIDATED = "VALIDATED", "Validé"
        PAID = "PAID", "Payé"

    period_month = models.PositiveSmallIntegerField()
    period_year = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=RunStatus.choices, default=RunStatus.DRAFT)
    generated_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("period_month", "period_year")
        ordering = ["-period_year", "-period_month"]

    def __str__(self):
        return f"Paie {self.period_month:02d}/{self.period_year}"

    @property
    def total_net(self):
        return self.payslips.aggregate(total=models.Sum("net_salary"))["total"] or Decimal("0")


class Payslip(TimeStampedModel):
    """Bulletin de paie individuel — calcul automatisé (base + primes + heures sup - retenues)."""
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name="payslips")
    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="payslips")

    base_salary = models.DecimalField(max_digits=14, decimal_places=2)
    bonuses = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    overtime_rate = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("1.25"),
                                         help_text="Majoration heures sup (ex: 1.25 = +25%)")
    advance_deduction = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="Avances sur salaire")

    # Champs calculés, conservés en base pour l'historique (pas recalculés a posteriori).
    cnss_deduction = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    pdf_file = models.FileField(upload_to="payslips/", null=True, blank=True)

    class Meta:
        unique_together = ("payroll_run", "employee")
        ordering = ["-payroll_run__period_year", "-payroll_run__period_month"]

    def __str__(self):
        return f"Bulletin {self.employee.matricule} - {self.payroll_run}"

    def compute(self, save=True):
        """
        Calcule le salaire brut/net selon la formule:
        brut = base + primes + heures_sup
        net  = brut - CNSS - impôt - avances
        """
        hourly_rate = (self.base_salary / Decimal("173.33"))  # base mensuelle standard ~173h33
        overtime_amount = hourly_rate * self.overtime_hours * self.overtime_rate
        self.gross_salary = self.base_salary + self.bonuses + overtime_amount

        self.cnss_deduction = (self.gross_salary * CNSS_EMPLOYEE_RATE).quantize(Decimal("1"))
        self.tax_deduction = self._compute_tax(self.gross_salary)
        self.net_salary = (
            self.gross_salary - self.cnss_deduction - self.tax_deduction - self.advance_deduction
        ).quantize(Decimal("1"))

        if save:
            self.save()
        return self.net_salary

    @staticmethod
    def _compute_tax(gross_salary):
        """Barème progressif simplifié (à ajuster selon le code des impôts guinéen en vigueur)."""
        tax = Decimal("0")
        previous_bracket = Decimal("0")
        for bracket_limit, rate in TAX_BRACKETS:
            taxable_in_bracket = min(gross_salary, bracket_limit) - previous_bracket
            if taxable_in_bracket > 0:
                tax += taxable_in_bracket * rate
            previous_bracket = bracket_limit
            if gross_salary <= bracket_limit:
                break
        return tax.quantize(Decimal("1"))
