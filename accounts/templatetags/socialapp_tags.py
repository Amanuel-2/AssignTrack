from django import template
from django.contrib.sites.shortcuts import get_current_site

from allauth.socialaccount.models import SocialApp

register = template.Library()


@register.filter
def has_social_app(request, provider):
    if not request:
        return False
    site = get_current_site(request)
    return SocialApp.objects.filter(provider=provider, sites=site).exists()
