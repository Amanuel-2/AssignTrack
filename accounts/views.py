from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from accounts.forms import CustomUserCreationForm
from accounts.models import Profile
from assignments.models import Post, Submission
from courses.models import Course
from groups.models import Group


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
    role = (request.user.profile.role or "").strip().lower() if hasattr(request.user, "profile") else ""
    context = {"role": role}

    if role == "student":
        assignments = Post.objects.select_related("course", "author").order_by("deadline")
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

        context.update(
            {
                "enrolled_courses": enrolled_courses,
                "joined_groups": joined_groups,
                "upcoming_assignments": upcoming_assignments,
                "overdue_assignments": overdue_assignments,
                "notifications": notifications,
            }
        )
    elif role == "lecturer":
        context.update(
            {
                "assignments": Post.objects.filter(author=request.user).select_related("course"),
                "courses": Course.objects.filter(
                    lecturer=request.user,
                    posts__author=request.user,
                ).distinct().order_by("name"),
                "submissions": Submission.objects.filter(post__author=request.user).select_related("post", "student"),
                "groups": Group.objects.filter(post__author=request.user).select_related("post"),
            }
        )

    return render(request, "myapp/profile.html", context)


@login_required
@require_POST
def upload_profile_picture_view(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"role": "student"},
    )
    image = request.FILES.get("profile_picture")
    if image:
        profile.profile_picture = image
        profile.save(update_fields=["profile_picture"])
    return redirect(request.POST.get("next") or "dashboard")
