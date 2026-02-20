# AssignTracker Feature Documentation

## Instructor-Only HTML CRUD (Template-Based)

### Purpose
Instructors can edit and delete only their own assignments using server-rendered Django pages.

### Routes
- `GET/POST /api/assignments/<post_id>/edit/` : Edit assignment form (instructor + owner only)
- `GET/POST /api/assignments/<post_id>/delete/` : Delete confirmation (instructor + owner only)

### Security Rules
- User must be authenticated.
- User profile role must be `lecturer`.
- Assignment must belong to the logged-in instructor (`post.author == request.user`).
- Non-instructors or non-owners receive HTTP 403/404 protection.

### Templates
- `myapp/templates/myapp/assignment_edit.html`
- `myapp/templates/myapp/assignment_confirm_delete.html`

### Dashboard Integration
On `dashboard`, assignment cards now show `Edit` and `Delete` links only when:
- user is instructor
- and is the author of that assignment

---

## API CRUD (Instructor Ownership)

### Routes
- `GET/POST /api/assignments/create/` : List/create assignments
- `GET/PATCH/PUT/DELETE /api/assignments/manage/<pk>/` : Retrieve/update/delete assignment

### Ownership Rule
For write operations, queryset is restricted to instructor-owned posts only.

---

## Student Group Generation Logic

When an instructor creates an assignment with:
- `group_type = manual` or `group_type = automatic`
- `max_students_per_group > 0`

the system automatically creates groups based on registered active students:

`number_of_groups = ceil(total_active_students / max_students_per_group)`

### Example
- Active registered students: `15`
- Max students per group: `5`
- Created groups: `3`

For `manual`:
- groups are created for students to choose from

For `automatic`:
- groups are created and students are auto-assigned

---

## Secure Group Join API

### Route
- `POST /api/groups/<group_id>/join/`

### Validations
- authenticated user
- role is `student`
- assignment group type is `manual`
- deadline not passed
- student not already in another group for same assignment
- group not full

### Response
Success:
```json
{
  "success": "Successfully joined group.",
  "member_count": 3
}
```

Error:
```json
{
  "error": "Group is full."
}
```
