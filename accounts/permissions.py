from rest_framework.permissions import BasePermission


class IsRole(BasePermission):
    allowed_role = None

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, "profile"):
            return False
        role = (request.user.profile.role or "").strip().lower()
        return role == self.allowed_role


class IsLecturer(IsRole):
    allowed_role = "lecturer"


class IsStudent(IsRole):
    allowed_role = "student"

