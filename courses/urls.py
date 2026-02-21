from django.urls import path

from courses.views import CourseDetailView, CourseListCreateView

urlpatterns = [
    path("", CourseListCreateView.as_view(), name="course_list_create"),
    path("<int:pk>/", CourseDetailView.as_view(), name="course_detail"),
]

