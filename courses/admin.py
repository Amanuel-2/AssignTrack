from django.contrib import admin

from myapp.models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "lecturer")
    search_fields = ("name", "lecturer__username")

