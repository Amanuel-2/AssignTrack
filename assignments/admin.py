from django.contrib import admin

from myapp.models import Post, Submission


@admin.register(Post)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "course", "deadline", "group_type")
    list_filter = ("group_type",)
    search_fields = ("title", "author__username")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("post", "student", "submitted_at")
    search_fields = ("post__title", "student__username")

