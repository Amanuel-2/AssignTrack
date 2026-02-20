from django.urls import path
from .views import (
    JoinGroupChoiceView,
    PostCreateView,
    PostDetailView,
    SubmissionCreateView,
    assignment_delete_view,
    assignment_detail_view,
    assignment_edit_view,
    dashboard_view,
    login_view,
    logout_view,
    profile_view,
    register_view,
)

from django.conf import settings
from django.conf.urls.static import static
from .api_views import join_group_api

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("assignments/<int:post_id>/", assignment_detail_view, name="assignment_detail"),
    path("assignments/<int:post_id>/edit/", assignment_edit_view, name="assignment_edit"),
    path("assignments/<int:post_id>/delete/", assignment_delete_view, name="assignment_delete"),

    path("assignments/create/", PostCreateView.as_view()),
    path("assignments/manage/<int:pk>/", PostDetailView.as_view(), name="assignment_api_detail"),
    path("groups/join/", JoinGroupChoiceView.as_view()),
    path("groups/<int:group_id>/join/", join_group_api, name="join_group_api"),
    path("submit/", SubmissionCreateView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
