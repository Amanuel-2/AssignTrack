pip install -r requirements.txt.# AssignTrack Feature Guide

## Assignment Workflows

### Instructor capabilities

- Create assignments from dashboard page and API.
- Edit/delete only assignments they own.
- Review assignment submissions by individual or by group.
- Inspect group-level submission detail pages.

### Student capabilities

- View assignment details and deadline status.
- Join manual groups (when allowed).
- Submit assignment files/links.
- Track upcoming/overdue items in dashboard/profile views.

## Assignment Types

- `individual`: one-person submissions
- `manual`: instructor defines group size; students choose a group
- `automatic`: groups are generated and students are auto-assigned

Group generation for manual/automatic uses:

`ceil(total_active_students / max_students_per_group)`

## Permission and Ownership Rules

- User must be authenticated for protected flows.
- Lecturer-only actions are guarded by role checks.
- Assignment edit/delete/review requires lecturer ownership.
- Group join is student-only and limited to manual assignments.

## Group Join Validation (`POST /api/groups/<group_id>/join/`)

Validation order:
- user is authenticated
- user role is `student`
- assignment deadline has not passed
- assignment type is `manual`
- user is not already in another group for the same assignment
- target group is not full

Success response includes `member_count`.

## Submission Integrity

- Duplicate submission prevention via model uniqueness (`post`, `student`).
- Non-students are blocked from posting submissions.
- For manual/automatic group assignments, students must belong to an eligible group before submitting.

## Dashboard Behavior

Student dashboard/profile:
- upcoming assignments
- overdue assignments
- joined groups
- submission status badges

Instructor dashboard:
- owned courses
- owned assignments
- submissions for owned assignments
- groups tied to owned assignments

## UI/Template Notes

- `templates/base.html`: global nav and layout shell
- `templates/myapp/`: auth/profile and assignment pages
- `templates/dashboard/`: student/instructor dashboard pages
- `templates/assignments/`: review and group submission detail pages

## Deployment-Related Behavior

- Static files served with WhiteNoise in production.
- Gunicorn serves `config.wsgi:application`.
- Database uses `DATABASE_URL` when present.
- Google provider login link appears only when SocialApp is configured for the current site.
