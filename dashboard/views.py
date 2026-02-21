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
    user_role = _role(request.user)

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


@login_required
def student_dashboard_view(request):
    if _role(request.user) != "student":
        return render(request, "dashboard/student_dashboard.html", {"forbidden": True})

    now = timezone.now()
    assignments = Post.objects.select_related("course", "author").annotate(
        is_overdue_case=Case(
            When(deadline__lt=now, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by("is_overdue_case", "deadline")

    submissions = Submission.objects.filter(student=request.user).select_related("post")
    joined_groups = Group.objects.filter(members=request.user).select_related("post")
    enrolled_courses = Course.objects.filter(student=request.user)

    submitted_post_ids = {s.post_id for s in submissions}
    for assignment in assignments:
        assignment.has_submitted = assignment.id in submitted_post_ids

    upcoming_assignments = [a for a in assignments if not a.is_overdue]
    overdue_assignments = [a for a in assignments if a.is_overdue]
    notifications = [
        f"Assignment '{a.title}' is due on {a.deadline:%Y-%m-%d %H:%M}"
        for a in upcoming_assignments[:5]
    ]

    context = {
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

    my_courses = Course.objects.filter(lecturer=request.user)
    my_assignments = Post.objects.filter(author=request.user).select_related("course")
    submissions = Submission.objects.filter(post__author=request.user).select_related("post", "student")
    groups = Group.objects.filter(post__author=request.user).select_related("post")

    context = {
        "courses": my_courses,
        "assignments": my_assignments,
        "submissions": submissions,
        "groups": groups,
    }
    return render(request, "dashboard/instructor_dashboard.html", context)
