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

        return data

