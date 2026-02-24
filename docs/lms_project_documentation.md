# Django LMS Project Documentation

## 1. Project Folder Structure

```text
AssignTrack/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── courses/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── assignments/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── groups/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── api_views.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── dashboard/
│   ├── __init__.py
│   ├── apps.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── myapp/                         # compatibility app (legacy wrappers + shared models)
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── models.py                  # current canonical models
│   ├── forms.py                   # wrappers
│   ├── serializers.py             # wrappers
│   ├── permissions.py             # wrappers
│   ├── views.py                   # wrappers
│   └── api_views.py               # wrappers
├── templates/
│   └── dashboard/
│       ├── instructor_dashboard.html
│       ├── student_dashboard.html
│       └── assignment_create.html
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   └── images/
├── media/
│   ├── assignments/
│   └── submissions/
└── docs/
    ├── assigntracker_features.md
    ├── milestone4_improvements.md
    └── lms_project_documentation.md
```

### App Responsibilities
- `accounts`: registration/login/profile + role-based permission utilities.
- `courses`: course CRUD endpoints.
- `assignments`: assignment CRUD + submission logic + instructor assignment create page.
- `groups`: group join APIs and group selection logic.
- `dashboard`: student/instructor dashboard queries and rendering.
- `myapp`: currently hosts the physical DB models and legacy compatibility imports.

---

## 2. User System

### User Model
The project currently uses Django’s built-in `auth.User`.

### Profile Model
Defined in `myapp/models.py`:

```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
```

### Role System
- Supported roles: `student`, `lecturer`.
- Role values are normalized by `strip().lower()` in permission and view checks.

### Role Check Example
From `accounts/permissions.py`:

```python
class IsRole(BasePermission):
    allowed_role = None
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, "profile"):
            return False
        role = (request.user.profile.role or "").strip().lower()
        return role == self.allowed_role
```

---

## 3. Course System

### Course Model Fields
Defined in `myapp/models.py`:

```python
class Course(models.Model):
    name = models.CharField(max_length=200)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE)
    student = models.ManyToManyField(User, related_name="courses")
```

### Relationships
- One lecturer can own many courses (`Course.lecturer`).
- Many students can be linked to many courses (`Course.student` M2M).

### Course Creation
- Via API endpoint in `courses.views.CourseListCreateView`.
- POST is restricted to lecturer role.

### Lecturer-Specific Filtering
- Instructor dashboard explicitly filters:

```python
my_courses = Course.objects.filter(lecturer=request.user)
```

- Assignment create page for instructor uses demo CS course set:
`_ensure_demo_cs_courses(request.user)` in `assignments/views.py`.

---

## 4. Assignment / Post System

### Post Model
Defined in `myapp/models.py` (`Post` behaves as Assignment):

```python
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    deadline = models.DateTimeField()
    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPE_CHOICES, default='individual')
    max_students_per_group = models.IntegerField(null=True, blank=True)
    course = models.ForeignKey("Course", on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
```

### Relationships
- Assignment -> Lecturer: `Post.author`.
- Assignment -> Course: `Post.course`.

### Submission Model

```python
class Submission(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="submissions")
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'student')
```

### Submission Linkage
- Each submission belongs to:
  - one assignment (`post`)
  - one student (`student`)
  - one group (`group`)
- Uniqueness rule prevents duplicate submissions per student per assignment.

---

## 5. Group System

### Group Model
Defined in `myapp/models.py`:

```python
class Group(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="groups")
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name="assignment_groups", blank=True)
```

### Group Creation Logic
Groups are auto-generated in `assignments/views.py`:
- For `manual` and `automatic` types.
- Group count = `ceil(total_students / max_students_per_group)`.
- For `automatic`, users are auto-assigned to groups.

### Group Join Constraints
Enforced in `groups/api_views.py`:
- only students can join
- manual groups only
- deadline not passed
- cannot join more than one group per assignment
- group capacity enforced

---

## 6. Dashboard Logic

## Instructor Dashboard Query Logic
From `dashboard/views.py`:

```python
my_courses = Course.objects.filter(lecturer=request.user)
my_assignments = Post.objects.filter(author=request.user).select_related("course")
submissions = Submission.objects.filter(post__author=request.user).select_related("post", "student")
groups = Group.objects.filter(post__author=request.user).select_related("post")
```

### Instructor Dashboard Context
- `courses`
- `assignments`
- `submissions`
- `groups`

## Student Dashboard Query Logic
From `dashboard/views.py`:

```python
assignments = Post.objects.select_related("course", "author").annotate(
    is_overdue_case=Case(
        When(deadline__lt=now, then=Value(1)),
        default=Value(0),
        output_field=IntegerField(),
    )
).order_by("is_overdue_case", "deadline")
```

Plus:
- `submissions = Submission.objects.filter(student=request.user)`
- `joined_groups = Group.objects.filter(members=request.user)`
- `notifications` generated from nearest upcoming deadlines.

### Student Dashboard Context
- `joined_groups`
- `upcoming_assignments`
- `overdue_assignments`
- `notifications`

---

## 7. Permissions

### Custom Permission Classes
Defined in `accounts/permissions.py`:
- `IsRole`
- `IsLecturer`
- `IsStudent`

### Enforcement Strategy
- DRF views use permission classes (`permission_classes = [IsLecturer]`, etc.).
- Template views additionally perform explicit role checks:
  - `_is_lecturer(user)` in `assignments/views.py`
  - submission POST blocked for non-students (`HttpResponseForbidden`).

---

## 8. URL Structure

## Main URL Configuration
`config/urls.py`:

```python
path('api/accounts/', include('accounts.urls'))
path('api/courses/', include('courses.urls'))
path('api/assignments/', include('assignments.urls'))
path('api/groups/', include('groups.urls'))
path('dashboard/', include('dashboard.urls'))
path('api/', include('myapp.urls'))  # legacy/compat endpoints
```

## App-Level Endpoints (Examples)
- Accounts:
  - `GET/POST /api/accounts/register/`
  - `GET/POST /api/accounts/login/`
- Courses:
  - `GET/POST /api/courses/`
  - `GET/PUT/PATCH/DELETE /api/courses/<id>/`
- Assignments:
  - `GET/POST /api/assignments/`
  - `GET/PATCH/DELETE /api/assignments/manage/<id>/`
  - `GET/POST /api/assignments/<post_id>/` (detail + submit via template view)
- Groups:
  - `POST /api/groups/<group_id>/join/`
  - `GET/POST /api/groups/join/`
- Dashboards:
  - `/dashboard/student/`
  - `/dashboard/instructor/`
  - `/dashboard/instructor/assignments/create/`

---

## 9. Database Relationships (Text ER Diagram)

```text
auth_user (Django User)
  1 --- 1  Profile
  1 --- *  Course (as lecturer)
  * --- *  Course (as student via Course.student)
  1 --- *  Post (as author/lecturer)
  * --- *  Group (via Group.members)
  1 --- *  Submission (as student)

Course
  1 --- *  Post

Post
  1 --- *  Group
  1 --- *  Submission

Group
  1 --- *  Submission

Submission
  belongs to one Post
  belongs to one Group
  belongs to one User (student)
  UNIQUE(post, student)
```

---

## 10. Current Known Issues and Inconsistencies

1. **Model ownership is not fully split yet**
- Although architecture is modular, physical models are still defined in `myapp/models.py`.
- New apps currently import/re-export these models.

2. **Legacy route overlap**
- Both modular endpoints and legacy `myapp` endpoints are active under `/api/`.
- This can create duplicate URL patterns and maintenance overhead.

3. **Course model naming inconsistency**
- `Course.student` is a ManyToMany field but singularly named (`student`).
- Prefer renaming to `students` in a future migration for clarity.

4. **Instructor dashboard courses**
- Current query is correctly scoped:
  `Course.objects.filter(lecturer=request.user)`.
- If all courses appear, verify that template is using `courses` from `instructor_dashboard_view` and not the legacy `/api/dashboard/` flow.

5. **Allauth deprecation warnings in settings**
- `ACCOUNT_AUTHENTICATION_METHOD` and `ACCOUNT_EMAIL_REQUIRED` are deprecated and should be migrated to new keys.

---

## 11. Recommended Next Refactor Phase

- Move canonical model definitions from `myapp/models.py` into:
  - `accounts/models.py`
  - `courses/models.py`
  - `assignments/models.py`
  - `groups/models.py`
- Add migration plan with data-safe model moves.
- Remove `myapp` compatibility wrappers once all imports and URLs are fully migrated.
