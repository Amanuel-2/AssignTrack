from django.urls import path
from .views import register_view,login_view,logout_view,profile_view,PostCreateView,SubmissionCreateView,JoinGroupView,JoinGroupChoiceView,assignment_detail_view
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("register/",register_view  , name="register"),
    path("login/", login_view, name="login"),
    path("logout/",logout_view,name='logout'),
    path("profile/",profile_view,name="profile"),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('assignment/<int:post_id>/',assignment_detail_view,name="assignment_detail"),

    path('assignments/create/', PostCreateView.as_view()),
   path("api/groups/<int:group_id>/join/", views.join_group, name="join_group"),
    path('groups/join/', JoinGroupChoiceView.as_view()),
    path('submit/', SubmissionCreateView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
