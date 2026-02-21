from django.contrib import admin

from myapp.models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "post")
    filter_horizontal = ("members",)

