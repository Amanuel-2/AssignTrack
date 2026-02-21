from django import forms

from assignments.models import Post, Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["file"]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "course",
            "title",
            "content",
            "deadline",
            "attachment",
            "group_type",
            "max_students_per_group",
        ]
        widgets = {
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
