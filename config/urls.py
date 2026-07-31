"""
Point d'entrée unique de l'API. Chaque app expose son propre urls.py
(routeur DRF), inclus ici sous le préfixe /api/.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("apps.authentication.urls")),
    path("api/", include("apps.users.urls")),
    path("api/", include("apps.organizations.urls")),
    path("api/", include("apps.employees.urls")),
    path("api/", include("apps.contracts.urls")),
    path("api/", include("apps.attendance.urls")),
    path("api/", include("apps.leave_management.urls")),
    path("api/", include("apps.payroll.urls")),
    path("api/", include("apps.accounting.urls")),
    path("api/", include("apps.dashboard.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
