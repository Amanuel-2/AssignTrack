from django.utils import timezone
from rest_framework import serializers

from assignments.models import Post, Submission
from groups.models import Group


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ("author", "created_at")

    def validate(self, data):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication is required.")

        role = (
            (request.user.profile.role or "").strip().lower()
            if hasattr(request.user, "profile")
            else ""
        )
        if role != "lecturer":
            raise serializers.ValidationError("Only lecturers can create assignments.")
        return data


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = "__all__"
        extra_kwargs = {
            "file": {"required": False, "allow_null": True},
            "submission_link": {"required": False, "allow_null": True, "allow_blank": True},
            "supporting_link": {"required": False, "allow_null": True, "allow_blank": True},
        }

    def validate(self, data):
        request = self.context.get("request")
        post = data["post"]
        group = data.get("group")
        file_value = data.get("file")
        submission_link = data.get("submission_link")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication is required.")

        role = (
            (request.user.profile.role or "").strip().lower()
            if hasattr(request.user, "profile")
            else ""
        )
        if role != "student":
            raise serializers.ValidationError("Only students can submit.")

        if timezone.now() > post.deadline:
            raise serializers.ValidationError("Deadline has passed.")

        if Submission.objects.filter(post=post, student=request.user).exists():
            raise serializers.ValidationError("You already submitted this assignment.")

        if not file_value and not submission_link:
            raise serializers.ValidationError("Provide at least a file or a submission link.")

        if post.group_type in ("manual", "automatic"):
            if group is None:
                raise serializers.ValidationError("A group is required for this assignment.")
            if group.post_id != post.id:
                raise serializers.ValidationError("Selected group does not belong to this assignment.")
            if not group.members.filter(id=request.user.id).exists():
                raise serializers.ValidationError("You must join your group before submitting.")

        return data
