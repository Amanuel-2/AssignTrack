from rest_framework import serializers

from myapp.models import Post, Submission


class DashboardAssignmentSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "title", "deadline", "group_type", "status"]

    def get_status(self, obj):
        user = self.context.get("user")
        if not user:
            return "Unknown"
        has_submission = Submission.objects.filter(post=obj, student=user).exists()
        if has_submission:
            return "Submitted"
        return "Overdue" if obj.is_overdue else "Pending"

