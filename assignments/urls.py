from django.urls import path

from assignments.views import (
    PostCreateView,
    PostDetailView,
    SubmissionCreateView,
    assignment_delete_view,
    assignment_detail_view,
    assignment_edit_view,
    group_submission_detail_view,
    assignment_review_view,
    teacher_dashboard
)

urlpatterns = [
    path("", PostCreateView.as_view(), name="assignment_list_create"),
    path("create/", PostCreateView.as_view(), name="assignment_create"),
    path("manage/<int:pk>/", PostDetailView.as_view(), name="assignment_api_detail"),
    path("<int:post_id>/", assignment_detail_view, name="assignment_detail"),
    path("<int:post_id>/edit/", assignment_edit_view, name="assignment_edit"),
    path("<int:post_id>/delete/", assignment_delete_view, name="assignment_delete"),
    path("submit/", SubmissionCreateView.as_view(), name="assignment_submit"),
    path("teacher/dashboard/", teacher_dashboard, name="teacher_dashboard"),
    path("manage/<int:pk>/review/", assignment_review_view, name="assignment_review"),
    path("manage/<int:post_id>/groups/<int:group_id>/", group_submission_detail_view, name="group_submission_detail"),

]
