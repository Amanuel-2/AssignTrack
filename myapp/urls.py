from django.urls import path
from .views import register_view,login_view,logout_view,profile_view,PostCreateView,SubmissionCreateView,JoinGroupView,JoinGroupChoiceView
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("register/",register_view  , name="register"),
    path("login/", login_view, name="login"),
    path("logout/",logout_view,name='logout'),
    path("profile/",profile_view,name="profile"),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('assignments/create/', PostCreateView.as_view()),
    path('groups/<int:group_id>/join/', JoinGroupView.as_view()),
    path('groups/join/', JoinGroupChoiceView.as_view()),
    path('submit/', SubmissionCreateView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
