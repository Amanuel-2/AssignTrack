from django.urls import path

from accounts.views import login_view, logout_view, profile_view, register_view, upload_profile_picture_view

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("profile/picture/", upload_profile_picture_view, name="upload_profile_picture"),
]
