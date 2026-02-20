from rest_framework.permissions import BasePermission


class IsLecturer(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        if not hasattr(request.user, "profile"):
            return False
        role = (request.user.profile.role or "").strip().lower()
        return role == "lecturer"

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not hasattr(request.user, "profile"):
            return False
        role = (request.user.profile.role or "").strip().lower()
        return role == "student"

    
