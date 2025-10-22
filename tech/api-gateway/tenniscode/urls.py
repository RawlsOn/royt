from django.urls import re_path, path, include
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

from . import apis

# router.register('clubs', apis.ClubsViewSet)
# router.register('club', apis.ClubViewSet)

urlpatterns = [
    # path('', include(router.urls)),

    path(
        'clubs/',
        apis.FetchClubs.as_view(),
        name="FetchClubs"
    ),
    path(
        'club/<str:title>/',
        apis.GetClub.as_view(),
        name="GetClub"
    ),
    path(
        'club/<str:club_id>/anon-comment/',
        apis.PostAnonClubComment.as_view(),
        name="PostAnonClubComment"
    ),
    path(
        'club/<str:club_id>/anon-comment/<str:comment_id>/',
        apis.DeleteAnonClubComment.as_view(),
        name="DeleteAnonClubComment"
    ),
    path(
        'index-info/',
        apis.GetIndexInfo.as_view(),
        name="GetIndexInfo"
    ),

]

