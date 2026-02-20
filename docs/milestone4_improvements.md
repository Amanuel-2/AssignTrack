# Milestone 4 Improvements

## 1) Course + Instructor Visibility

Implemented display of:
- Course name
- Instructor name

Shown on:
- Dashboard assignment cards
- Assignment detail page

Data source:
- `Post.course`
- `Post.author`

Files:
- `myapp/models.py` (added `Post.course`)
- `myapp/templates/myapp/dashboard.html`
- `myapp/templates/myapp/assignment_detail.html`

---

## 2) Prevent Lecturers from Submitting

Server-side enforcement:
- `assignment_detail_view` returns `403` on POST if role is not student.

Template enforcement:
- Submission form is shown only when student submission is allowed.

Files:
- `myapp/views.py`
- `myapp/templates/myapp/assignment_detail.html`

---

## 3) File Download Fix

Download links use:
- `{{ post.attachment.url }}`
- `{{ submission.file.url }}`

Media config confirmed:
- `MEDIA_URL = '/media/'`
- `MEDIA_ROOT = BASE_DIR / 'media'`

Files:
- `config/settings.py`
- `myapp/templates/myapp/assignment_detail.html`

---

## 4) Dashboard Sorting Logic

Assignments are sorted by:
1. Active first (not overdue)
2. Closest deadline first
3. Overdue at bottom

Implemented with `Case/When` annotation.

File:
- `myapp/views.py` (`dashboard_view`)

---

## 5) Status Badges

Status is now rendered as colored badge classes:
- `submitted` (green)
- `pending` (orange)
- `overdue` (red)

Files:
- `myapp/views.py` (sets `status_class`)
- `myapp/templates/myapp/dashboard.html`
- `myapp/templates/myapp/assignment_detail.html`

---

## 6) Global CSS Styling

Added full UI styling:
- Card layout
- Buttons
- Badges
- Group containers
- Disabled states
- Responsive behavior

Files:
- `myapp/static/css/style.css`
- `myapp/templates/base.html` (loads stylesheet)

---

## Additional Validations

Kept and/or enforced:
- No duplicate submissions (`SubmissionSerializer` + model unique constraint)
- No joining multiple groups per assignment (`join_group_api`)
- No joining full group (`join_group_api`)
- No submission without group for manual/automatic (`SubmissionSerializer` + detail-view checks)

Files:
- `myapp/serializers.py`
- `myapp/api_views.py`
- `myapp/views.py`
