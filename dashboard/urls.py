from django.urls import path

from dashboard.views import dashboard_view, instructor_dashboard_view, student_dashboard_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("student/", student_dashboard_view, name="student_dashboard"),
    path("instructor/", instructor_dashboard_view, name="instructor_dashboard"),
]
