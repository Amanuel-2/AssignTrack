from math import ceil

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import SAFE_METHODS

from accounts.permissions import IsLecturer, IsStudent
from assignments.forms import PostForm, SubmissionForm
from assignments.models import Post, Submission
from assignments.serializers import AssignmentSerializer, SubmissionSerializer
from courses.models import Course
from groups.models import Group
from accounts.models import Profile

def _is_lecturer(user):
    if not user.is_authenticated or not hasattr(user, "profile"):
        return False
    return (user.profile.role or "").strip().lower() == "lecturer"


DEMO_CS_COURSES = [
    "Introduction to Computer Science",
    "Data Structures",
    "Algorithms",
    "Database Systems",
    "Operating Systems",
    "Computer Networks",
    "Software Engineering",
    "Web Development",
]


def _ensure_demo_cs_courses(lecturer):
    for name in DEMO_CS_COURSES:
        Course.objects.get_or_create(name=name, lecturer=lecturer)
    return Course.objects.filter(lecturer=lecturer, name__in=DEMO_CS_COURSES).order_by("name")


def _create_groups_for_post(post):
    if post.group_type not in ["manual", "automatic"]:
        return
    if not post.max_students_per_group or post.max_students_per_group <= 0:
        return

    students = User.objects.filter(profile__role="student", is_active=True).distinct()
    total_students = students.count()
    if total_students == 0:
        return

    number_of_groups = ceil(total_students / post.max_students_per_group)
    groups = [Group.objects.create(post=post, name=f"Group {i}") for i in range(1, number_of_groups + 1)]

    if post.group_type == "automatic":
        group_index = 0
        for student in students:
            if group_index >= len(groups):
                break
            groups[group_index].members.add(student)
            if groups[group_index].members.count() >= post.max_students_per_group:
                group_index += 1


class PostCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsLecturer]

    def get_queryset(self):
        if self.request.method in SAFE_METHODS:
            return Post.objects.all()
        return Post.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        _create_groups_for_post(post)


@login_required
def instructor_assignment_create_view(request):
    if not _is_lecturer(request.user):
        return HttpResponseForbidden("Only instructors can create assignments.")

    allowed_courses = _ensure_demo_cs_courses(request.user)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        form.fields["course"].queryset = allowed_courses
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            _create_groups_for_post(post)
            return redirect("instructor_dashboard")
    else:
        form = PostForm()
        form.fields["course"].queryset = allowed_courses

    return render(request, "dashboard/assignment_create.html", {"form": form})


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = AssignmentSerializer
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


@login_required
def assignment_detail_view(request, post_id):
    user = request.user
    post = get_object_or_404(Post.objects.select_related("author", "course"), id=post_id)
    user_role = ((user.profile.role or "").strip().lower() if hasattr(user, "profile") else "")

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
                    individual_group, _ = Group.objects.get_or_create(post=post, name=f"{user.username}-individual")
                    if not individual_group.members.filter(id=user.id).exists():
                        individual_group.members.add(user)
                    new_submission.group = individual_group
                else:
                    new_submission.group = user_group

                new_submission.save()
                return redirect("assignment_detail", post_id=post.id)
    else:
        form = SubmissionForm()

    return render(
        request,
        "myapp/assignment_detail.html",
        {
            "post": post,
            "group": user_group,
            "groups": groups,
            "submission": submission,
            "form": form,
            "can_submit": can_submit and not submission,
            "submit_error": submit_error,
        },
    )


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

@login_required
def assignment_review_view(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Only lecturers
    if not _is_lecturer(request.user):
        return HttpResponseForbidden("Only instructors can access this page.")

    # Only the author (owner)
    if post.author != request.user:
        return HttpResponseForbidden("You do not own this assignment.")

    context = {
        "assignment": post,
    }

    # --------------------------------
    # INDIVIDUAL ASSIGNMENT
    # --------------------------------
    if post.group_type == "individual":

        students = User.objects.filter(
            profile__role="student",
            is_active=True
        )

        review_data = []

        for student in students:
            submission = Submission.objects.filter(
                post=post,
                student=student
            ).first()

            review_data.append({
                "student": student,
                "submitted": submission is not None,
                "submission": submission,
            })

        context["mode"] = "individual"
        context["review_data"] = review_data

    # --------------------------------
    # GROUP ASSIGNMENT (manual/automatic)
    # --------------------------------
    else:

        groups = Group.objects.filter(
            post=post
        ).prefetch_related("members")

        group_review_data = []

        for group in groups:
            submission = Submission.objects.filter(
                post=post,
                group=group
            ).first()

            group_review_data.append({
                "group": group,
                "members": group.members.all(),
                "submitted": submission is not None,
                "submission": submission,
            })

        context["mode"] = "group"
        context["review_data"] = group_review_data

    return render(
        request,
        "assignments/assignment_review.html",  
        context
    )

@login_required
def teacher_dashboard(request):
    if not _is_lecturer(request.user):
        return HttpResponseForbidden("Only instructors can access this page.")

    assignments = Post.objects.filter(author=request.user)

    return render(
        request,
        "assignments/teacher_dashboard.html",
        {"assignments": assignments}
    )