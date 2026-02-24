from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import render
from django.utils import timezone

from assignments.models import Post, Submission
from courses.models import Course
from groups.models import Group


def _role(user):
    if not hasattr(user, "profile"):
        return ""
    return (user.profile.role or "").strip().lower()


def _build_assignment_cards_for_user(user):
    now = timezone.now()
    posts = Post.objects.select_related("author", "course").annotate(
        is_overdue_case=Case(
            When(deadline__lt=now, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by("is_overdue_case", "deadline")
    user_role = _role(user)

    for post in posts:
        post.user_status = post.get_status_for_user(user)
        post.status_class = post.user_status.lower()
        post.can_manage = user_role == "lecturer" and post.author_id == user.id
        user_group_names = list(
            Group.objects.filter(post=post, members=user)
            .order_by("id")
            .values_list("name", flat=True)
        )
        post.user_group = ", ".join(user_group_names) if user_group_names else None
        groups = Group.objects.filter(post=post)
        total_submissions = Submission.objects.filter(post=post).count()
        total_students = sum(group.members.count() for group in groups)
        post.progress = f"{total_submissions}/{total_students}" if total_students else "0/0"
    return posts


def home_view(request):
    role = _role(request.user) if request.user.is_authenticated else ""
    context = {
        "role": role,
    }
    return render(request, "home.html", context)


@login_required
def dashboard_view(request):
    if _role(request.user) != "student":
        return render(request, "dashboard/student_dashboard.html", {"forbidden": True})

    assignments = Post.objects.select_related("course", "author").order_by("deadline")
    submissions = Submission.objects.filter(student=request.user).select_related("post")
    joined_groups = Group.objects.filter(members=request.user).select_related("post")
    enrolled_courses = Course.objects.filter(student=request.user)
    posts = _build_assignment_cards_for_user(request.user)

    submitted_post_ids = {submission.post_id for submission in submissions}
    for assignment in assignments:
        assignment.has_submitted = assignment.id in submitted_post_ids

    upcoming_assignments = [assignment for assignment in assignments if not assignment.is_overdue]
    overdue_assignments = [assignment for assignment in assignments if assignment.is_overdue]
    notifications = [
        f"Assignment '{assignment.title}' is due on {assignment.deadline:%Y-%m-%d %H:%M}"
        for assignment in upcoming_assignments[:5]
    ]

    context = {
        "posts": posts,
        "enrolled_courses": enrolled_courses,
        "joined_groups": joined_groups,
        "upcoming_assignments": upcoming_assignments,
        "overdue_assignments": overdue_assignments,
        "notifications": notifications,
    }
    return render(request, "dashboard/student_dashboard.html", context)


@login_required
def instructor_dashboard_view(request):
    if _role(request.user) != "lecturer":
        return render(request, "dashboard/instructor_dashboard.html", {"forbidden": True})

    my_assignments = Post.objects.filter(author=request.user).select_related("course")
    my_courses = Course.objects.filter(
        lecturer=request.user,
        posts__author=request.user,
    ).distinct().order_by("name")
    submissions = Submission.objects.filter(post__author=request.user).select_related("post", "student")
    groups = Group.objects.filter(post__author=request.user).select_related("post")

    context = {
        "courses": my_courses,
        "assignments": my_assignments,
        "submissions": submissions,
        "groups": groups,
    }
    return render(request, "dashboard/instructor_dashboard.html", context)
