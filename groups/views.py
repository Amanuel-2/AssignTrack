from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from groups.serializers import JoinGroupChoiceSerializer
from groups.models import Group


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
        data = [{"id": group.id, "name": group.name, "assignment": group.post.title} for group in groups]
        return Response({"groups": data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = JoinGroupChoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.validated_data["group"]
        joiner = JoinGroupView()
        return joiner._join_group(request, group)
