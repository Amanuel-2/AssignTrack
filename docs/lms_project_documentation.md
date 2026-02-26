# AssignTrack Technical Documentation

## 1. Repository Structure

```text
AssignTrack/
├── manage.py
├── requirements.txt
├── build.sh
├── render.yaml
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── mongodb.py
├── accounts/
├── courses/
├── assignments/
├── groups/
├── dashboard/
├── templates/
├── static/
├── media/
└── docs/
```

## 2. Domain Model Summary

### `accounts.Profile` (`myapp_profile`)
- `user` (OneToOne to Django User)
- `role` (`student` or `lecturer`)
- `bio`
- `profile_picture`

### `courses.Course` (`myapp_course`)
- `name`
- `lecturer` (FK User)
- `student` (M2M User)

### `assignments.Post` (`myapp_post`)
- `author` (FK User)
- `title`, `content`, `deadline`
- `attachment`
- `group_type` (`individual`, `manual`, `automatic`)
- `max_students_per_group`
- `course` (FK Course, nullable)

### `groups.Group` (`myapp_group`)
- `post` (FK Post)
- `name`
- `members` (M2M User through `myapp_group_members`)

### `assignments.Submission` (`myapp_submission`)
- `post` (FK Post)
- `group` (FK Group)
- `student` (FK User)
- `file`, optional links
- `submitted_at`
- unique constraint: (`post`, `student`)

## 3. Auth and Role Architecture

- Django auth User is canonical identity.
- Role is stored in `accounts.Profile.role`.
- Role checks are used by both DRF permissions and template views.
- Signals/context safeguards ensure profile creation for authenticated users where needed.

## 4. API and Template Routing

Defined from `config/urls.py` and app URL files.

### Accounts
- `/api/accounts/register/`
- `/api/accounts/login/`
- `/api/accounts/logout/`
- `/api/accounts/profile/`

### Courses
- `/api/courses/`
- `/api/courses/<id>/`

### Assignments
- `/api/assignments/`
- `/api/assignments/create/`
- `/api/assignments/manage/<id>/`
- `/api/assignments/<post_id>/`
- `/api/assignments/<post_id>/edit/`
- `/api/assignments/<post_id>/delete/`
- `/api/assignments/manage/<id>/review/`
- `/api/assignments/manage/<post_id>/groups/<group_id>/`

### Groups
- `/api/groups/join/`
- `/api/groups/<group_id>/join/`

### Dashboards
- `/dashboard/`
- `/dashboard/instructor/`
- `/dashboard/instructor/assignments/create/`

## 5. Assignment Lifecycle

1. Lecturer creates assignment.
2. If group type is manual/automatic, groups are generated.
3. Student joins group (manual) or is auto-assigned (automatic).
4. Student submits once per assignment.
5. Lecturer reviews by individual/group mode.

## 6. Permission Matrix

- Anonymous: public pages only.
- Student:
  - can submit assignments
  - can join manual groups
  - cannot create/edit/delete assignments
- Lecturer:
  - can create/manage own assignments
  - can review own assignment submissions
  - can access instructor dashboard

## 7. Deployment and Runtime

### Production settings
- environment-driven `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `SECURE_PROXY_SSL_HEADER`
- secure cookies/redirect when not debug

### Static/media
- WhiteNoise static storage
- `collectstatic` in build
- media served by Django config path for current setup

### Render
- Build command should run migrations and collectstatic (`bash build.sh`).
- Start command should run gunicorn bound to `$PORT`.

## 8. MongoDB Atlas (Optional)

`config/mongodb.py` provides:
- `get_mongo_client()`
- `get_mongo_db()`

Environment variables:
- `MONGODB_URI`
- `MONGODB_DB_NAME`

Use Mongo for secondary/non-ORM data. Keep relational DB for Django models.

## 9. Known Gaps

- allauth settings use deprecated keys and should be migrated.
- mixed API + template routes under `/api/` can be confusing naming-wise.
- `Course.student` field naming is singular though it is M2M.

## 10. Maintenance Checklist

- run `python manage.py check`
- run migrations before deploy
- validate `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`
- verify Google SocialApp configuration when enabling OAuth login
