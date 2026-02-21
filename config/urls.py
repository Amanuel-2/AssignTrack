"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.http import JsonResponse


def api_root(request):
    return JsonResponse(
        {
            "message": "AssignTrack API",
            "endpoints": {
                "accounts": "/api/accounts/",
                "courses": "/api/courses/",
                "assignments": "/api/assignments/",
                "groups": "/api/groups/",
                "legacy": "/api/dashboard/",
            },
        }
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/', api_root, name='api_root'),
    path('api/accounts/', include('accounts.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/assignments/', include('assignments.urls')),
    path('api/groups/', include('groups.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('api/', include('myapp.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
