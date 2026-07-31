from django.db import models
from core.models import TimeStampedModel


# ---------------------------------------------------------------------------
# A. Gestion Administrative du Personnel
# ---------------------------------------------------------------------------

class Employee(TimeStampedModel):
    """Fiche individuelle complète (base des 132 employés)."""

    class Category(models.TextChoices):
        CONAKRY = "CONAKRY", "Conakry"
        SITE = "SITE", "Site"
        GARAGE = "GARAGE", "Garage"
        OPERATEUR = "OPERATEUR", "Opérateur"

    class Gender(models.TextChoices):
        M = "M", "Masculin"
        F = "F", "Féminin"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Actif"
        INACTIVE = "INACTIVE", "Inactif"
        SUSPENDED = "SUSPENDED", "Suspendu"
        TERMINATED = "TERMINATED", "Sorti des effectifs"

    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, related_name="employee_profile",
        null=True, blank=True,
        help_text="Compte de connexion associé (pour l'auto-service employé)."
    )
    matricule = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    birth_date = models.DateField()
    national_id = models.CharField(max_length=50, blank=True, help_text="N° carte d'identité / passeport")
    phone = models.CharField(max_length=20, blank=True)
    personal_email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    site = models.ForeignKey("organizations.Site", on_delete=models.PROTECT, related_name="employees")
    department = models.ForeignKey("organizations.Department", on_delete=models.PROTECT, related_name="employees")
    category = models.CharField(max_length=20, choices=Category.choices)
    position = models.CharField(max_length=150, help_text="Poste occupé")
    hire_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    manager = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="direct_reports"
    )

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.matricule} - {self.last_name} {self.first_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


def employee_document_path(instance, filename):
    return f"employees/{instance.employee.matricule}/documents/{instance.doc_type}/{filename}"


class EmployeeDocument(TimeStampedModel):
    """Archivage numérique des documents (CV, diplômes, certificats médicaux, casier judiciaire)."""

    class DocType(models.TextChoices):
        CV = "CV", "CV"
        DIPLOMA = "DIPLOMA", "Diplôme"
        MEDICAL_CERT = "MEDICAL_CERT", "Certificat médical"
        CRIMINAL_RECORD = "CRIMINAL_RECORD", "Casier judiciaire"
        ID_CARD = "ID_CARD", "Pièce d'identité"
        OTHER = "OTHER", "Autre"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    title = models.CharField(max_length=150)
    file = models.FileField(upload_to=employee_document_path)
    expiry_date = models.DateField(null=True, blank=True, help_text="Pour les documents avec date de validité")
    uploaded_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee.matricule} - {self.get_doc_type_display()} - {self.title}"


class Assignment(TimeStampedModel):
    """Historique des affectations et mutations entre sites/départements."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="assignments")
    previous_site = models.ForeignKey(
        "organizations.Site", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    new_site = models.ForeignKey("organizations.Site", on_delete=models.PROTECT, related_name="+")
    previous_department = models.ForeignKey(
        "organizations.Department", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    new_department = models.ForeignKey("organizations.Department", on_delete=models.PROTECT, related_name="+")
    effective_date = models.DateField()
    reason = models.TextField(blank=True)
    decided_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-effective_date"]

    def __str__(self):
        return f"{self.employee.matricule} -> {self.new_site.name} ({self.effective_date})"


# ---------------------------------------------------------------------------
# D. Gestion de la Formation et des Compétences
# ---------------------------------------------------------------------------

class Skill(TimeStampedModel):
    """Cartographie des compétences par poste."""
    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class EmployeeSkill(TimeStampedModel):
    class Level(models.TextChoices):
        BEGINNER = "BEGINNER", "Débutant"
        INTERMEDIATE = "INTERMEDIATE", "Intermédiaire"
        ADVANCED = "ADVANCED", "Avancé"
        EXPERT = "EXPERT", "Expert"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=Level.choices)

    class Meta:
        unique_together = ("employee", "skill")

    def __str__(self):
        return f"{self.employee.matricule} - {self.skill.name} ({self.level})"


class Training(TimeStampedModel):
    """Plan de formation annuel avec budget associé, formations obligatoires HSSE/conduite/maintenance."""

    class TrainingType(models.TextChoices):
        DRIVING = "DRIVING", "Conduite"
        HSSE = "HSSE", "HSSE"
        MAINTENANCE = "MAINTENANCE", "Maintenance"
        MANAGEMENT = "MANAGEMENT", "Management"
        OTHER = "OTHER", "Autre"

    title = models.CharField(max_length=200)
    training_type = models.CharField(max_length=20, choices=TrainingType.choices)
    is_mandatory = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    provider = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.title


class EmployeeTraining(TimeStampedModel):
    class ResultStatus(models.TextChoices):
        PLANNED = "PLANNED", "Planifiée"
        IN_PROGRESS = "IN_PROGRESS", "En cours"
        COMPLETED = "COMPLETED", "Complétée"
        FAILED = "FAILED", "Échec"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="trainings")
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name="participants")
    status = models.CharField(max_length=20, choices=ResultStatus.choices, default=ResultStatus.PLANNED)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ("employee", "training")

    def __str__(self):
        return f"{self.employee.matricule} - {self.training.title}"


class Certification(TimeStampedModel):
    """Gestion des habilitations et certifications (permis de conduire, CACES, etc.)."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=150, help_text="Ex: Permis de conduire catégorie C, CACES R482")
    issued_by = models.CharField(max_length=150, blank=True)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["expiry_date"]

    def __str__(self):
        return f"{self.employee.matricule} - {self.name}"


class PerformanceReview(TimeStampedModel):
    """Évaluation des performances et entretiens annuels."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="performance_reviews")
    reviewer = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    review_date = models.DateField()
    period_year = models.PositiveIntegerField()
    score = models.DecimalField(max_digits=5, decimal_places=2, help_text="Note globale /20")
    strengths = models.TextField(blank=True)
    improvement_areas = models.TextField(blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ["-review_date"]
        unique_together = ("employee", "period_year")

    def __str__(self):
        return f"{self.employee.matricule} - Évaluation {self.period_year}"


# ---------------------------------------------------------------------------
# E. Gestion HSSE (Hygiène, Santé, Sécurité, Environnement)
# ---------------------------------------------------------------------------

class EPIDistribution(TimeStampedModel):
    """Suivi des EPI (Équipements de Protection Individuelle) distribués par employé."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="epi_distributions")
    item_name = models.CharField(max_length=150, help_text="Ex: Casque, chaussures de sécurité, gants")
    quantity = models.PositiveIntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    distribution_date = models.DateField()
    renewal_due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-distribution_date"]

    def __str__(self):
        return f"{self.employee.matricule} - {self.item_name} x{self.quantity}"

    @property
    def total_cost(self):
        return self.quantity * self.unit_cost


class SafetyIncident(TimeStampedModel):
    """Registre des accidents de travail et incidents."""

    class Severity(models.TextChoices):
        MINOR = "MINOR", "Mineur"
        MODERATE = "MODERATE", "Modéré"
        SEVERE = "SEVERE", "Grave"
        FATAL = "FATAL", "Mortel"

    class IncidentStatus(models.TextChoices):
        REPORTED = "REPORTED", "Déclaré"
        UNDER_INVESTIGATION = "UNDER_INVESTIGATION", "En cours d'investigation"
        CLOSED = "CLOSED", "Clôturé"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="safety_incidents")
    site = models.ForeignKey("organizations.Site", on_delete=models.PROTECT)
    incident_date = models.DateTimeField()
    severity = models.CharField(max_length=20, choices=Severity.choices)
    description = models.TextField()
    corrective_actions = models.TextField(blank=True)
    status = models.CharField(max_length=25, choices=IncidentStatus.choices, default=IncidentStatus.REPORTED)
    reported_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, related_name="+")

    class Meta:
        ordering = ["-incident_date"]

    def __str__(self):
        return f"Incident {self.get_severity_display()} - {self.employee.matricule} ({self.incident_date:%Y-%m-%d})"


class MedicalVisit(TimeStampedModel):
    """Gestion des visites médicales obligatoires."""

    class VisitType(models.TextChoices):
        HIRING = "HIRING", "Visite d'embauche"
        PERIODIC = "PERIODIC", "Visite périodique"
        RETURN_TO_WORK = "RETURN_TO_WORK", "Visite de reprise"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="medical_visits")
    visit_type = models.CharField(max_length=20, choices=VisitType.choices)
    visit_date = models.DateField()
    next_visit_date = models.DateField(null=True, blank=True)
    fit_for_duty = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-visit_date"]

    def __str__(self):
        return f"{self.employee.matricule} - {self.get_visit_type_display()} ({self.visit_date})"


# ---------------------------------------------------------------------------
# F. Recrutement et Intégration
# ---------------------------------------------------------------------------

class JobOffer(TimeStampedModel):
    class OfferStatus(models.TextChoices):
        OPEN = "OPEN", "Ouverte"
        CLOSED = "CLOSED", "Clôturée"
        CANCELLED = "CANCELLED", "Annulée"

    title = models.CharField(max_length=200)
    department = models.ForeignKey("organizations.Department", on_delete=models.PROTECT)
    site = models.ForeignKey("organizations.Site", on_delete=models.PROTECT)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=OfferStatus.choices, default=OfferStatus.OPEN)
    published_date = models.DateField()
    closing_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-published_date"]

    def __str__(self):
        return self.title


class Candidate(TimeStampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    cv_file = models.FileField(upload_to="recruitment/cvs/", null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class JobApplication(TimeStampedModel):
    """Workflow de validation du processus de recrutement + planification des entretiens."""

    class ApplicationStatus(models.TextChoices):
        RECEIVED = "RECEIVED", "Reçue"
        SHORTLISTED = "SHORTLISTED", "Présélectionnée"
        INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED", "Entretien planifié"
        OFFER_MADE = "OFFER_MADE", "Offre transmise"
        HIRED = "HIRED", "Recruté(e)"
        REJECTED = "REJECTED", "Rejetée"

    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=25, choices=ApplicationStatus.choices, default=ApplicationStatus.RECEIVED)
    interview_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("job_offer", "candidate")

    def __str__(self):
        return f"{self.candidate} -> {self.job_offer.title} ({self.status})"


class Onboarding(TimeStampedModel):
    """Onboarding des nouveaux employés + suivi de la période d'essai."""

    class OnboardingStatus(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "En cours"
        COMPLETED = "COMPLETED", "Terminé"

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="onboarding")
    checklist_completed = models.BooleanField(default=False)
    trial_period_end_date = models.DateField(null=True, blank=True)
    trial_period_validated = models.BooleanField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=OnboardingStatus.choices, default=OnboardingStatus.IN_PROGRESS)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Intégration - {self.employee.matricule}"
