from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsLecturer
from courses.models import Course
from courses.serializers import CourseSerializer


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsLecturer()]
        return [IsAuthenticated()]


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsLecturer()]
        return [IsAuthenticated()]
