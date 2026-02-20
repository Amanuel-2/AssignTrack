from rest_framework import serializers
from .models import Course,Submission,Post,Group
from django.contrib.auth.models import User
from django.utils import timezone

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ("author", "created_at")

    def validate(self, data):
        request = self.context.get('request')

        #Only lecturer can create assignment
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

    
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class JoinGroupChoiceSerializer(serializers.Serializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = "__all__"

    def validate(self, data):
        request = self.context.get('request')
        post = data['post']
        group = data.get("group")

        # Only students can submit
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication is required.")
        role = (
            (request.user.profile.role or "").strip().lower()
            if hasattr(request.user, "profile")
            else ""
        )
        if role != "student":
            raise serializers.ValidationError("Only students can submit.")

        # Check deadline
        if timezone.now() > post.deadline:
            raise serializers.ValidationError("Deadline has passed.")

        if Submission.objects.filter(post=post, student=request.user).exists():
            raise serializers.ValidationError("You already submitted this assignment.")

        if post.group_type in ("manual", "automatic"):
            if group is None:
                raise serializers.ValidationError("A group is required for this assignment.")
            if group.post_id != post.id:
                raise serializers.ValidationError("Selected group does not belong to this assignment.")
            if not group.members.filter(id=request.user.id).exists():
                raise serializers.ValidationError("You must join your group before submitting.")

        return data

