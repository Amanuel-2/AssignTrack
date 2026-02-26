from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile


@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance, defaults={"role": "student"})


@receiver(user_logged_in)
def ensure_profile_on_login(sender, request, user, **kwargs):
    Profile.objects.get_or_create(user=user, defaults={"role": "student"})
