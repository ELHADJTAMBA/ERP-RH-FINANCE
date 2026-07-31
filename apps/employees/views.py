from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated

from core.base import AuditLoggingModelViewSet
from core.permissions import IsRHOrAbove, IsOwnerOrRHOrAbove
from .models import (
    Employee, EmployeeDocument, Assignment, Skill, EmployeeSkill,
    Training, EmployeeTraining, Certification, PerformanceReview,
    EPIDistribution, SafetyIncident, MedicalVisit,
    JobOffer, Candidate, JobApplication, Onboarding,
)
from .serializers import (
    EmployeeSerializer, EmployeeListSerializer, EmployeeDocumentSerializer,
    AssignmentSerializer, SkillSerializer, EmployeeSkillSerializer,
    TrainingSerializer, EmployeeTrainingSerializer, CertificationSerializer,
    PerformanceReviewSerializer, EPIDistributionSerializer, SafetyIncidentSerializer,
    MedicalVisitSerializer, JobOfferSerializer, CandidateSerializer,
    JobApplicationSerializer, OnboardingSerializer,
)


# --- A. Administration du personnel -----------------------------------------

class EmployeeViewSet(AuditLoggingModelViewSet):
    queryset = Employee.objects.select_related("site", "department", "manager", "user").all()
    permission_classes = [IsOwnerOrRHOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["site", "department", "category", "status"]
    search_fields = ["matricule", "first_name", "last_name", "position"]
    ordering_fields = ["hire_date", "last_name"]

    def get_serializer_class(self):
        return EmployeeListSerializer if self.action == "list" else EmployeeSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        # Un employé simple ne voit que sa propre fiche.
        if user.role == "EMPLOYE":
            return qs.filter(user=user)
        return qs


class EmployeeDocumentViewSet(AuditLoggingModelViewSet):
    queryset = EmployeeDocument.objects.select_related("employee").all()
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsOwnerOrRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "doc_type"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == "EMPLOYE":
            return qs.filter(employee__user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
        self._log("CREATE", serializer.instance)


class AssignmentViewSet(AuditLoggingModelViewSet):
    queryset = Assignment.objects.select_related("employee", "new_site", "new_department").all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "new_site"]

    def perform_create(self, serializer):
        instance = serializer.save(decided_by=self.request.user)
        # Met à jour la fiche employé avec la nouvelle affectation.
        instance.employee.site = instance.new_site
        instance.employee.department = instance.new_department
        instance.employee.save(update_fields=["site", "department"])
        self._log("CREATE", instance)


# --- D. Formation et compétences --------------------------------------------

class SkillViewSet(AuditLoggingModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsRHOrAbove]


class EmployeeSkillViewSet(AuditLoggingModelViewSet):
    queryset = EmployeeSkill.objects.select_related("employee", "skill").all()
    serializer_class = EmployeeSkillSerializer
    permission_classes = [IsRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "skill"]


class TrainingViewSet(AuditLoggingModelViewSet):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    permission_classes = [IsRHOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["training_type", "is_mandatory"]
    search_fields = ["title"]


class EmployeeTrainingViewSet(AuditLoggingModelViewSet):
    queryset = EmployeeTraining.objects.select_related("employee", "training").all()
    serializer_class = EmployeeTrainingSerializer
    permission_classes = [IsRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "training", "status"]


class CertificationViewSet(AuditLoggingModelViewSet):
    queryset = Certification.objects.select_related("employee").all()
    serializer_class = CertificationSerializer
    permission_classes = [IsRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee"]


class PerformanceReviewViewSet(AuditLoggingModelViewSet):
    queryset = PerformanceReview.objects.select_related("employee", "reviewer").all()
    serializer_class = PerformanceReviewSerializer
    permission_classes = [IsOwnerOrRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "period_year"]

    def perform_create(self, serializer):
        instance = serializer.save(reviewer=self.request.user)
        self._log("CREATE", instance)


# --- E. HSSE -----------------------------------------------------------------

class EPIDistributionViewSet(AuditLoggingModelViewSet):
    queryset = EPIDistribution.objects.select_related("employee").all()
    serializer_class = EPIDistributionSerializer
    permission_classes = [IsRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee"]


class SafetyIncidentViewSet(AuditLoggingModelViewSet):
    """Les employés peuvent déclarer un incident (create), RH gère le suivi."""
    queryset = SafetyIncident.objects.select_related("employee", "site").all()
    serializer_class = SafetyIncidentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["site", "severity", "status"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == "EMPLOYE":
            return qs.filter(employee__user=self.request.user)
        return qs

    def perform_create(self, serializer):
        instance = serializer.save(reported_by=self.request.user)
        self._log("CREATE", instance)


class MedicalVisitViewSet(AuditLoggingModelViewSet):
    queryset = MedicalVisit.objects.select_related("employee").all()
    serializer_class = MedicalVisitSerializer
    permission_classes = [IsRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "visit_type"]


# --- F. Recrutement et intégration -------------------------------------------

class JobOfferViewSet(AuditLoggingModelViewSet):
    queryset = JobOffer.objects.select_related("department", "site").all()
    serializer_class = JobOfferSerializer
    permission_classes = [IsRHOrAbove]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["status", "department", "site"]
    search_fields = ["title"]


class CandidateViewSet(AuditLoggingModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsRHOrAbove]
    filter_backends = [SearchFilter]
    search_fields = ["first_name", "last_name", "email"]


class JobApplicationViewSet(AuditLoggingModelViewSet):
    queryset = JobApplication.objects.select_related("job_offer", "candidate").all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["job_offer", "status"]

    def perform_create(self, serializer):
        instance = serializer.save(reviewed_by=self.request.user)
        self._log("CREATE", instance)


class OnboardingViewSet(AuditLoggingModelViewSet):
    queryset = Onboarding.objects.select_related("employee").all()
    serializer_class = OnboardingSerializer
    permission_classes = [IsRHOrAbove]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "status"]
