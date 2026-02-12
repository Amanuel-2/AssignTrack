from django.urls import path
from .views import register_view,login_view,logout_view,profile_view
from . import views
urlpatterns = [
    path("register/",register_view  , name="register"),
    path("login/", login_view, name="login"),
    path("logout/",logout_view,name='logout'),
    path("profile/",profile_view,name="profile"),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
