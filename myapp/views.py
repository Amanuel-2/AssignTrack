from accounts.views import login_view, logout_view, profile_view, register_view
from assignments.views import (
    PostCreateView,
    PostDetailView,
    SubmissionCreateView,
    assignment_delete_view,
    assignment_detail_view,
    assignment_edit_view,
)
from dashboard.views import dashboard_view
from groups.views import JoinGroupChoiceView, JoinGroupView

__all__ = [
    "register_view",
    "login_view",
    "logout_view",
    "profile_view",
    "dashboard_view",
    "PostCreateView",
    "PostDetailView",
    "SubmissionCreateView",
    "JoinGroupView",
    "JoinGroupChoiceView",
    "assignment_detail_view",
    "assignment_edit_view",
    "assignment_delete_view",
]

