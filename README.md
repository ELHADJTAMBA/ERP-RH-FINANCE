# Backend SIRH & Gestion Financière

Backend Django REST Framework construit à partir du cahier des charges.

## Démarrage rapide

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # ajuster si besoin (PostgreSQL, secret key...)
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

L'API est alors disponible sur http://localhost:8000/api/
L'admin Django sur http://localhost:8000/admin/

## Authentification

```
POST /api/auth/login/     {"email": "...", "password": "..."}  -> {access, refresh, user}
POST /api/auth/refresh/   {"refresh": "..."}                    -> {access}
POST /api/auth/logout/    {"refresh": "..."}                    -> déconnexion (blacklist)
```

Ajouter le header `Authorization: Bearer <access>` sur toutes les autres requêtes.

## Modules / endpoints principaux

| App | Préfixe | Contenu |
|---|---|---|
| users | /api/users/ | comptes, rôles, /me/ |
| organizations | /api/sites/, /api/departments/ | sites & départements |
| employees | /api/employees/, /api/employee-documents/, /api/assignments/, /api/skills/, /api/trainings/, /api/certifications/, /api/performance-reviews/, /api/epi-distributions/, /api/safety-incidents/, /api/medical-visits/, /api/job-offers/, /api/candidates/, /api/job-applications/, /api/onboardings/ | RH complet |
| contracts | /api/contracts/ (+ /expiring_soon/) | CDI/CDD/Stage |
| attendance | /api/work-schedules/, /api/attendances/ | pointage & horaires |
| leave_management | /api/leave-types/, /api/leave-requests/ (+ /approve/, /reject/) | congés |
| payroll | /api/salary-grids/, /api/payroll-runs/ (+ /generate_payslips/, /validate_run/), /api/payslips/ | paie |
| accounting | /api/accounts/, /api/journal-entries/, /api/budgets/, /api/suppliers/, /api/purchase-requests/, /api/purchase-orders/, /api/bank-accounts/, /api/treasury-forecasts/, /api/fixed-assets/, /api/invoices/ | finance |
| dashboard | /api/dashboard/hr/, /finance/, /operations/, /hsse/ | KPIs |

## Rôles (voir core/permissions.py)

SUPER_ADMIN, DG_DGA, RH_HSSE, COMPTABLE, RESP_OPERATIONNEL, EMPLOYE

## Points à valider avant production

- **Barème fiscal / CNSS** dans `apps/payroll/models.py` : valeurs indicatives à faire vérifier auprès de votre comptable / de la réglementation guinéenne en vigueur.
- Générer le **PDF des bulletins de paie** (actuellement le champ `pdf_file` est prévu mais la génération n'est pas implémentée — à ajouter avec `xhtml2pdf` ou `weasyprint`).
- Ajouter un **plan de sauvegarde automatique quotidien** et un **PRA** au niveau infrastructure (hors code applicatif).
- Ajouter le **chiffrement au niveau applicatif** pour les champs les plus sensibles si votre hébergeur ne chiffre pas déjà le disque/la base.
- Activer HTTPS et l'authentification multi-facteurs en production.
