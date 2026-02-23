from django.urls import path

from assignments.views import instructor_assignment_create_view
from dashboard.views import dashboard_view, instructor_dashboard_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("instructor/", instructor_dashboard_view, name="instructor_dashboard"),
    path("instructor/assignments/create/", instructor_assignment_create_view, name="instructor_assignment_create"),
]
