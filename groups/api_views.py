from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from groups.models import Group


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_group_api(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    post = group.post
    user = request.user

    role = (
        (user.profile.role or "").strip().lower()
        if hasattr(user, "profile")
        else ""
    )
    if role != "student":
        return Response(
            {"error": "Only students can join groups."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if post.deadline and timezone.now() > post.deadline:
        return Response(
            {"error": "Deadline passed."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if post.group_type != "manual":
        return Response(
            {"error": "Joining not allowed for this assignment."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    existing_group = Group.objects.filter(post=post, members=user).first()
    if existing_group:
        if existing_group.id == group.id:
            return Response(
                {
                    "success": "You are already in this group.",
                    "member_count": group.members.count(),
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "You are already in a group."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if post.max_students_per_group and group.members.count() >= post.max_students_per_group:
        return Response(
            {"error": "Group is full."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    group.members.add(user)
    return Response(
        {"success": "Successfully joined group.", "member_count": group.members.count()}
    )
