from django.urls import path

from groups.api_views import join_group_api
from groups.views import JoinGroupChoiceView

urlpatterns = [
    path("join/", JoinGroupChoiceView.as_view(), name="group_join_choice"),
    path("<int:group_id>/join/", join_group_api, name="join_group_api"),
]
