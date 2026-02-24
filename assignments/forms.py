from django import forms

from assignments.models import Post, Submission


class SubmissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow either file or link; enforce "at least one" in clean().
        self.fields["file"].required = False
        self.fields["submission_link"].required = False

    def clean(self):
        cleaned_data = super().clean()
        file_value = cleaned_data.get("file")
        link_value = cleaned_data.get("submission_link")
        if not file_value and not link_value:
            raise forms.ValidationError("Please provide a file or a submission link.")
        return cleaned_data

    class Meta:
        model = Submission
        fields = ["file", "submission_link"]
        widgets = {
            "submission_link": forms.URLInput(attrs={"placeholder": "https://example.com/main-submission"}),
        }


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
