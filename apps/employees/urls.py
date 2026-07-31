from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeViewSet, EmployeeDocumentViewSet, AssignmentViewSet,
    SkillViewSet, EmployeeSkillViewSet, TrainingViewSet, EmployeeTrainingViewSet,
    CertificationViewSet, PerformanceReviewViewSet,
    EPIDistributionViewSet, SafetyIncidentViewSet, MedicalVisitViewSet,
    JobOfferViewSet, CandidateViewSet, JobApplicationViewSet, OnboardingViewSet,
)

router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")
router.register("employee-documents", EmployeeDocumentViewSet, basename="employee-document")
router.register("assignments", AssignmentViewSet, basename="assignment")
router.register("skills", SkillViewSet, basename="skill")
router.register("employee-skills", EmployeeSkillViewSet, basename="employee-skill")
router.register("trainings", TrainingViewSet, basename="training")
router.register("employee-trainings", EmployeeTrainingViewSet, basename="employee-training")
router.register("certifications", CertificationViewSet, basename="certification")
router.register("performance-reviews", PerformanceReviewViewSet, basename="performance-review")
router.register("epi-distributions", EPIDistributionViewSet, basename="epi-distribution")
router.register("safety-incidents", SafetyIncidentViewSet, basename="safety-incident")
router.register("medical-visits", MedicalVisitViewSet, basename="medical-visit")
router.register("job-offers", JobOfferViewSet, basename="job-offer")
router.register("candidates", CandidateViewSet, basename="candidate")
router.register("job-applications", JobApplicationViewSet, basename="job-application")
router.register("onboardings", OnboardingViewSet, basename="onboarding")

urlpatterns = router.urls
