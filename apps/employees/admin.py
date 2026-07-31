from django.contrib import admin
from . import models

admin.site.register(models.Employee)
admin.site.register(models.EmployeeDocument)
admin.site.register(models.Assignment)
admin.site.register(models.Skill)
admin.site.register(models.EmployeeSkill)
admin.site.register(models.Training)
admin.site.register(models.EmployeeTraining)
admin.site.register(models.Certification)
admin.site.register(models.PerformanceReview)
admin.site.register(models.EPIDistribution)
admin.site.register(models.SafetyIncident)
admin.site.register(models.MedicalVisit)
admin.site.register(models.JobOffer)
admin.site.register(models.Candidate)
admin.site.register(models.JobApplication)
admin.site.register(models.Onboarding)
