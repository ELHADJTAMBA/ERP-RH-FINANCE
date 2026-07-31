from rest_framework import serializers
from .models import (
    Employee, EmployeeDocument, Assignment, Skill, EmployeeSkill,
    Training, EmployeeTraining, Certification, PerformanceReview,
    EPIDistribution, SafetyIncident, MedicalVisit,
    JobOffer, Candidate, JobApplication, Onboarding,
)


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    site_name = serializers.CharField(source="site.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Employee
        fields = "__all__"


class EmployeeListSerializer(serializers.ModelSerializer):
    """Version allégée pour les listes (performance)."""
    full_name = serializers.CharField(read_only=True)
    site_name = serializers.CharField(source="site.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Employee
        fields = ("id", "matricule", "full_name", "position", "category",
                   "site_name", "department_name", "status", "hire_date")


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = "__all__"
        read_only_fields = ("uploaded_by",)


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = "__all__"
        read_only_fields = ("decided_by",)


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class EmployeeSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)

    class Meta:
        model = EmployeeSkill
        fields = "__all__"


class TrainingSerializer(serializers.ModelSerializer):
    participant_count = serializers.IntegerField(source="participants.count", read_only=True)

    class Meta:
        model = Training
        fields = "__all__"


class EmployeeTrainingSerializer(serializers.ModelSerializer):
    training_title = serializers.CharField(source="training.title", read_only=True)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)

    class Meta:
        model = EmployeeTraining
        fields = "__all__"


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = "__all__"


class PerformanceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceReview
        fields = "__all__"
        read_only_fields = ("reviewer",)


class EPIDistributionSerializer(serializers.ModelSerializer):
    total_cost = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = EPIDistribution
        fields = "__all__"


class SafetyIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyIncident
        fields = "__all__"
        read_only_fields = ("reported_by",)


class MedicalVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalVisit
        fields = "__all__"


class JobOfferSerializer(serializers.ModelSerializer):
    application_count = serializers.IntegerField(source="applications.count", read_only=True)

    class Meta:
        model = JobOffer
        fields = "__all__"


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = "__all__"


class JobApplicationSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source="candidate.__str__", read_only=True)
    job_title = serializers.CharField(source="job_offer.title", read_only=True)

    class Meta:
        model = JobApplication
        fields = "__all__"
        read_only_fields = ("reviewed_by",)


class OnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Onboarding
        fields = "__all__"
