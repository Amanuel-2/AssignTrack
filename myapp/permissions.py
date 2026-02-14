from requests import request
from rest_framework.permissions import BasePermission


class IsLecturer(BasePermission):
    def has_permission(self, request, view):
        # Allow GET so browsable API can load
        if request.method == "GET":
            return True

        # Only allow POST for authenticated teachers
        return (
            request.user.is_authenticated and
            hasattr(request.user, "profile") and
            request.user.profile.role == "lecturer"
        )

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "profile") and request.user.profile.role == 'student'

    