from accounts.models import Profile


def user_role(request):
    if not request.user.is_authenticated:
        return {"current_user_role": ""}

    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"role": "student"},
    )
    return {"current_user_role": (profile.role or "").strip().lower()}
