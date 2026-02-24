from django.urls import path

from assignments.views import instructor_assignment_create_view
from dashboard.views import assignment_groups_overview_view, dashboard_view, instructor_dashboard_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("instructor/", instructor_dashboard_view, name="instructor_dashboard"),
    path("instructor/assignments/create/", instructor_assignment_create_view, name="instructor_assignment_create"),
    path("instructor/groups/<int:post_id>/", assignment_groups_overview_view, name="assignment_groups_overview"),
]
