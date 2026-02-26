# Milestone 4 Improvements (Updated)

This document summarizes the functional improvements delivered around assignment workflow, permissions, and production deployment hardening.

## 1. Instructor Assignment Management

Implemented instructor-only controls for:
- assignment create
- assignment edit
- assignment delete
- assignment review (owner-scoped)

Impact:
- prevents non-lecturer mutation of assignment records
- limits instructor management access to owned assignments

## 2. Group Workflow Strengthening

Implemented and/or reinforced:
- automatic group generation for `manual` and `automatic` assignment types
- group capacity control using `max_students_per_group`
- student-only join rules
- duplicate membership guard for same assignment

Impact:
- predictable group provisioning
- reduced invalid join states

## 3. Submission Safety Rules

Implemented:
- one submission per student per assignment (model uniqueness)
- role guard: non-students cannot submit
- group-required submission logic for non-individual assignments

Impact:
- cleaner grading/review data
- reduced duplicate and invalid submissions

## 4. Dashboard and Review Visibility

Implemented:
- instructor dashboard summaries for courses, assignments, submissions, groups
- student dashboard summaries for upcoming/overdue/submission status
- assignment review mode separation:
  - individual assignment review
  - group assignment review

Impact:
- faster operational visibility for both roles

## 5. Authentication and Stability Fixes

Implemented:
- profile creation safeguards to reduce missing-profile runtime failures
- conditional Google login rendering when SocialApp is configured

Impact:
- fewer auth-page 500 errors in production

## 6. Deployment Hardening (Render)

Implemented:
- dependency pinning including `gunicorn`, `whitenoise`, `dj-database-url`, `psycopg`
- production static handling with WhiteNoise
- environment-driven settings for hosts/csrf/security
- Render blueprint/build workflow support (`render.yaml`, `build.sh`)

Impact:
- reproducible deploys and fewer startup/runtime misconfigurations

## 7. Optional MongoDB Integration

Implemented:
- `config/mongodb.py` helper using `pymongo`
- settings/env placeholders for `MONGODB_URI` and `MONGODB_DB_NAME`

Impact:
- enables secondary document-store use cases without changing Django ORM backend

## 8. Follow-up Actions

- migrate deprecated allauth settings to the current keys
- standardize naming for mixed API/template routes
- add automated tests for login/profile and group join edge cases
