# AssignTrack

AssignTrack is a Django-based assignment management platform with role-based workflows for `student` and `lecturer` users.

## Overview

AssignTrack provides:
- API endpoints for core resources (`accounts`, `courses`, `assignments`, `groups`)
- Template-based pages for login, profile, dashboards, assignment detail/review flows
- Role-aware permissions and ownership checks
- Render-ready deployment configuration

## Tech Stack

- Python 3.12+
- Django 6
- Django REST Framework
- django-allauth (including Google provider)
- WhiteNoise (static files in production)
- Gunicorn (WSGI server)
- PostgreSQL (recommended on Render via `DATABASE_URL`)
- SQLite (local fallback)
- Optional: MongoDB Atlas via `pymongo`

## Project Apps

- `accounts`: registration/login/logout/profile and role profile
- `courses`: course API CRUD
- `assignments`: assignment API + detail/edit/delete/review template workflows
- `groups`: group join APIs and group choice page
- `dashboard`: student/instructor dashboard pages
- `config`: settings, URL routing, WSGI/ASGI, Mongo helper

## Local Development

### 1) Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 2) Open

- Home: `http://127.0.0.1:8000/`
- API root: `http://127.0.0.1:8000/api/`
- Admin: `http://127.0.0.1:8000/admin/`
- Login: `http://127.0.0.1:8000/api/accounts/login/`

## Production Deployment (Render)

This repository includes:
- `build.sh`
- `render.yaml`

### Required Render settings

- Build Command: `bash build.sh`
- Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

### Required environment variables

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS` (example: `assigntrack-pcez.onrender.com`)
- `CSRF_TRUSTED_ORIGINS` (example: `https://assigntrack-pcez.onrender.com`)
- `DATABASE_URL` (Render PostgreSQL connection string)

### Optional environment variables

- `MONGODB_URI` (MongoDB Atlas URI)
- `MONGODB_DB_NAME` (default: `assigntrack`)

## Routes (High-Level)

### Core

- `GET /`
- `GET /admin/`
- `GET /api/`
- `GET /dashboard/`
- `GET /dashboard/instructor/`

### Accounts

- `GET|POST /api/accounts/register/`
- `GET|POST /api/accounts/login/`
- `GET /api/accounts/logout/`
- `GET /api/accounts/profile/`
- `POST /api/accounts/profile/picture/`

### Courses

- `GET|POST /api/courses/`
- `GET|PUT|PATCH|DELETE /api/courses/<id>/`

### Assignments

- `GET|POST /api/assignments/`
- `GET|POST /api/assignments/create/`
- `GET|PUT|PATCH|DELETE /api/assignments/manage/<id>/`
- `GET|POST /api/assignments/<post_id>/`
- `GET|POST /api/assignments/<post_id>/edit/`
- `GET|POST /api/assignments/<post_id>/delete/`
- `POST /api/assignments/submit/`
- `GET /api/assignments/manage/<id>/review/`
- `GET /api/assignments/manage/<post_id>/groups/<group_id>/`

### Groups

- `GET|POST /api/groups/join/`
- `POST /api/groups/<group_id>/join/`

## Authentication Notes

- Profile role values are `student` and `lecturer`.
- Login and profile flows rely on profile records; code now safeguards missing profile creation.
- Google login button is conditionally rendered only when SocialApp is configured for the current Django site.

## Optional MongoDB Usage

Use `config/mongodb.py`:

```python
from config.mongodb import get_mongo_db

db = get_mongo_db()
db.events.insert_one({"event": "example"})
```

Mongo is secondary storage. Core Django auth/models remain on the relational DB.

## Troubleshooting

### 500 on login page

- Confirm latest commit is deployed.
- Ensure migrations ran (`bash build.sh` includes migrate).
- Check Render runtime traceback after reproducing.
- If using Google login, configure SocialApp in Django admin for your site.

### Static files missing

- Ensure `collectstatic` runs during build.
- Verify WhiteNoise settings in `config/settings.py`.

## License

Internal/educational project unless otherwise specified.
