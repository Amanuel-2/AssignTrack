from django.db import migrations


def set_empty_roles_to_student(apps, schema_editor):
    Profile = apps.get_model("myapp", "Profile")
    Profile.objects.filter(role__isnull=True).update(role="student")
    Profile.objects.filter(role="").update(role="student")


def reverse_set_empty_roles_to_student(apps, schema_editor):
    # No safe automatic reverse for corrected user role data.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0004_drop_legacy_post_creater_column"),
    ]

    operations = [
        migrations.RunPython(set_empty_roles_to_student, reverse_set_empty_roles_to_student),
    ]
