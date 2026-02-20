from math import ceil

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import redirect, render
from django.utils import timezone

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CustomUserCreationForm
from .models import Group, Post, Submission
from .permissions import IsLecturer, IsStudent
from .serializers import JoinGroupChoiceSerializer, PostSerializer, SubmissionSerializer


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
            return redirect("profile")
    else:
        form = CustomUserCreationForm()
    return render(request, "myapp/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("profile")
    else:
        form = AuthenticationForm()
    return render(request, "myapp/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def profile_view(request):
    return render(request, "myapp/profile.html")


@login_required
def dashboard_view(request):
    posts = Post.objects.all()
    for post in posts:
        post.user_status = post.get_status_for_user(request.user)
    return render(request, "myapp/dashboard.html", {"posts": posts})


class PostCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsLecturer]

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        if post.group_type not in ["manual", "automatic"]:
            return
        if not post.max_students_per_group or post.max_students_per_group <= 0:
            return

        students = User.objects.filter(profile__role="student")
        total_students = students.count()
        if total_students == 0:
            return

        number_of_groups = ceil(total_students / post.max_students_per_group)
        groups = []
        for i in range(1, number_of_groups + 1):
            group = Group.objects.create(post=post, name=f"Group {i}")
            groups.append(group)

        if post.group_type == "automatic":
            group_index = 0
            for student in students:
                if group_index >= len(groups):
                    break
                groups[group_index].members.add(student)
                if groups[group_index].members.count() >= post.max_students_per_group:
                    group_index += 1


class SubmissionCreateView(generics.CreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsStudent]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class JoinGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _join_group(self, request, group):
        role = (
            (request.user.profile.role or "").strip().lower()
            if hasattr(request.user, "profile")
            else ""
        )
        if role != "student":
            return Response({"error": "Only students can join groups"}, status=status.HTTP_403_FORBIDDEN)

        post = group.post

        if timezone.now() > post.deadline:
            return Response({"error": "Deadline passed"}, status=status.HTTP_400_BAD_REQUEST)

        if post.group_type == "automatic":
            return Response({"error": "Automatic assignment enabled"}, status=status.HTTP_400_BAD_REQUEST)

        if not post.max_students_per_group or post.max_students_per_group <= 0:
            return Response({"error": "Group size not configured"}, status=status.HTTP_400_BAD_REQUEST)

        if group.members.count() >= post.max_students_per_group:
            return Response({"error": "Group is full"}, status=status.HTTP_400_BAD_REQUEST)

        if Group.objects.filter(post=post, members=request.user).exclude(id=group.id).exists():
            return Response(
                {"error": "You already joined another group for this assignment"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        group.members.add(request.user)
        return Response({"message": "Joined successfully"}, status=status.HTTP_200_OK)

    def post(self, request, group_id):
        try:
            group = Group.objects.select_related("post").get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        return self._join_group(request, group)


class JoinGroupChoiceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        groups = Group.objects.select_related("post").all()
        data = [
            {
                "id": group.id,
                "name": group.name,
                "assignment": group.post.title,
            }
            for group in groups
        ]
        return Response({"groups": data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = JoinGroupChoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.validated_data["group"]
        joiner = JoinGroupView()
        return joiner._join_group(request, group)
