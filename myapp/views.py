from math import ceil

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Case, IntegerField, Value, When

from rest_framework import generics, permissions, status
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CustomUserCreationForm, PostForm, SubmissionForm
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
    now = timezone.now()
    posts = Post.objects.select_related("author", "course").annotate(
        is_overdue_case=Case(
            When(deadline__lt=now, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by("is_overdue_case", "deadline")
    user_role = (
        (request.user.profile.role or "").strip().lower()
        if hasattr(request.user, "profile")
        else ""
    )

    for post in posts:
        post.user_status = post.get_status_for_user(request.user)
        post.status_class = post.user_status.lower()
        post.can_manage = user_role == "lecturer" and post.author_id == request.user.id
        try:
            group = Group.objects.get(post=post, members=request.user)
            post.user_group = group.name
        except Group.DoesNotExist:
            post.user_group = None
        groups = Group.objects.filter(post=post)
        total_submissions = Submission.objects.filter(post=post).count()
        total_students = sum(group.members.count() for group in groups)
        post.progress = f"{total_submissions}/{total_students}" if total_students else "0/0"
    return render(request, "myapp/dashboard.html", {"posts": posts})


def _is_lecturer(user):
    if not user.is_authenticated or not hasattr(user, "profile"):
        return False
    return (user.profile.role or "").strip().lower() == "lecturer"


class PostCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsLecturer]

    def get_queryset(self):
        if self.request.method in SAFE_METHODS:
            return Post.objects.all()
        return Post.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        if post.group_type not in ["manual", "automatic"]:
            return
        if not post.max_students_per_group or post.max_students_per_group <= 0:
            return

        students = User.objects.filter(
            profile__role="student",
            is_active=True,
        ).distinct()
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


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsLecturer]

    def get_queryset(self):
        if self.request.method in SAFE_METHODS:
            return Post.objects.all()
        return Post.objects.filter(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


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



@login_required
def assignment_detail_view(request, post_id):
    user = request.user
    post = get_object_or_404(Post.objects.select_related("author", "course"), id=post_id)
    user_role = (
        (user.profile.role or "").strip().lower()
        if hasattr(user, "profile")
        else ""
    )

    user_group = Group.objects.filter(post=post, members=user).first()
    submission = Submission.objects.filter(post=post, student=user).first()
    can_submit = user_role == "student"
    submit_error = None
    groups = Group.objects.none()

    if user_role != "student":
        submit_error = "Only students can submit assignments."

    if post.group_type == "manual":
        groups = post.groups.prefetch_related("members").all()
        if user_role == "student" and user_group is None:
            can_submit = False
            submit_error = "Join a group first before submitting."
    elif post.group_type == "automatic" and user_role == "student" and user_group is None:
        can_submit = False
        submit_error = "You are not assigned to an automatic group yet."

    if request.method == "POST":
        if user_role != "student":
            return HttpResponseForbidden("Only students can submit assignments.")
        if submission:
            return redirect("assignment_detail", post_id=post.id)
        if not can_submit:
            form = SubmissionForm()
        else:
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                new_submission = form.save(commit=False)
                new_submission.post = post
                new_submission.student = user

                if post.group_type == "individual":
                    individual_group, _ = Group.objects.get_or_create(
                        post=post,
                        name=f"{user.username}-individual",
                    )
                    if not individual_group.members.filter(id=user.id).exists():
                        individual_group.members.add(user)
                    new_submission.group = individual_group
                    user_group = individual_group
                else:
                    new_submission.group = user_group

                new_submission.save()
                return redirect("assignment_detail", post_id=post.id)
    else:
        form = SubmissionForm()

    return render(request, "myapp/assignment_detail.html", {
        "post": post,
        "group": user_group,
        "groups": groups,
        "submission": submission,
        "form": form,
        "can_submit": can_submit and not submission,
        "submit_error": submit_error,
    })


@login_required
def assignment_edit_view(request, post_id):
    if not _is_lecturer(request.user):
        return HttpResponseForbidden("Only instructors can edit assignments.")

    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("assignment_detail", post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "myapp/assignment_edit.html", {"form": form, "post": post})


@login_required
def assignment_delete_view(request, post_id):
    if not _is_lecturer(request.user):
        return HttpResponseForbidden("Only instructors can delete assignments.")

    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == "POST":
        post.delete()
        return redirect("dashboard")

    return render(request, "myapp/assignment_confirm_delete.html", {"post": post})
