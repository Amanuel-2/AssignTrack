# AssignTrack

AssignTrack is a Django learning management system focused on assignment workflows with role-based access for students and lecturers.

## Current Stack

- Python + Django
- Django REST Framework
- django-allauth (including Google provider)
- SQLite (default)

## Implemented Apps

- `accounts`: registration, login/logout, profile, role profile (`student` or `lecturer`)
- `courses`: course API CRUD endpoints
- `assignments`: assignment API + template views for detail/edit/delete + submission flow
- `groups`: group listing and join endpoints for manual group assignments
- `dashboard`: general dashboard + student/instructor dashboards

## Data Model (Current)

Core models are split across apps and use legacy-compatible DB table names:

- `accounts.Profile` (`myapp_profile`)
- `courses.Course` (`myapp_course`)
- `assignments.Post` (`myapp_post`) for assignments
- `assignments.Submission` (`myapp_submission`)
- `groups.Group` (`myapp_group`, M2M table `myapp_group_members`)

## Key Features

- Role-based behavior via profile role checks (`student`, `lecturer`)
- Instructor assignment creation with support for:
  - `individual`
  - `manual` groups
  - `automatic` groups
- Auto group generation when creating manual/automatic assignments
- Student submission workflow with duplicate-submission protection
- Manual group join constraints:
  - only students
  - only before deadline
  - only one group per assignment
  - no over-capacity joins
- Instructor-only assignment edit/delete (owner scoped)
- Dashboard status/progress indicators and overdue-aware ordering

## URL Map

### Main routes

- `GET /admin/`
- `GET /api/` API root JSON
- `GET /dashboard/`
- `GET /dashboard/student/`
- `GET /dashboard/instructor/`
- `GET|POST /dashboard/instructor/assignments/create/`

### Account routes

- `GET|POST /api/accounts/register/`
- `GET|POST /api/accounts/login/`
- `GET /api/accounts/logout/`
- `GET /api/accounts/profile/`

Allauth routes are also mounted at:

- `/accounts/`

### Course API

- `GET|POST /api/courses/`
- `GET|PUT|PATCH|DELETE /api/courses/<id>/`

### Assignment API + pages

- `GET|POST /api/assignments/`
- `GET|POST /api/assignments/create/`
- `GET|PUT|PATCH|DELETE /api/assignments/manage/<id>/`
- `GET|POST /api/assignments/<post_id>/` (detail + submission page)
- `GET|POST /api/assignments/<post_id>/edit/`
- `GET|POST /api/assignments/<post_id>/delete/`
- `POST /api/assignments/submit/` (API submission)

### Group endpoints

- `GET|POST /api/groups/join/` (list choices + join via payload)
- `POST /api/groups/<group_id>/join/`

## Permissions (Current Behavior)

- Global DRF default: authenticated users only
- Lecturers can create/update/delete courses
- Lecturers can create/manage assignments
- Students can submit assignments
- Group joins are restricted to students and manual-group assignments

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Run migrations.
4. Create a superuser (optional).
5. Start the server.

Example commands:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install django djangorestframework django-allauth pillow
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:

- App: <http://127.0.0.1:8000/dashboard/>
- API root: <http://127.0.0.1:8000/api/>
- Admin: <http://127.0.0.1:8000/admin/>

## Media and Static

- Media uploads are stored in `media/`
- Static assets are loaded from `static/`

Configured in `config/settings.py` with:

- `MEDIA_URL = '/media/'`
- `MEDIA_ROOT = BASE_DIR / 'media'`
- `STATIC_URL = 'static/'`
- `STATICFILES_DIRS = [BASE_DIR / 'static']`

## Notes

- This repository currently has no `requirements.txt`/`pyproject.toml`; dependency install command above reflects what is used in code.
- The codebase references legacy `myapp_*` database tables for compatibility.
