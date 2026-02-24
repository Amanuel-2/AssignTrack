from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Post(models.Model):
    GROUP_TYPE_CHOICES = (
        ("individual", "Individual"),
        ("manual", "Manual Group"),
        ("automatic", "Automatic Group"),
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    deadline = models.DateTimeField(help_text="Submission deadline")
    attachment = models.FileField(upload_to="assignments/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPE_CHOICES, default="individual")
    max_students_per_group = models.IntegerField(null=True, blank=True)
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )

    class Meta:
        db_table = "myapp_post"

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        return self.deadline and timezone.now() > self.deadline

    def get_status_for_user(self, user):
        if not user.is_authenticated:
            return "Unknown"

        has_submitted = self.submissions.filter(student=user).exists()
        if has_submitted:
            return "Submitted"
        if self.deadline and timezone.now() > self.deadline:
            return "Overdue"
        return "Pending"


class Submission(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="submissions")
    group = models.ForeignKey("groups.Group", on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to="submissions/")
    submission_link = models.URLField(blank=True, null=True)
    supporting_link = models.URLField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "myapp_submission"
        unique_together = ("post", "student")

    def __str__(self):
        return f"{self.student.username} - {self.post.title}"
