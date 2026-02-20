from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=(
            ("student", "Student"),
            ("lecturer", "Instructor"),
        ),
        required=True,
    )

    class Meta:
        model = User
        fields = ["username", "email", "role", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        role = self.cleaned_data["role"]
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={"role": "student"},
            )
            profile.role = role
            profile.save(update_fields=["role"])
        return user
