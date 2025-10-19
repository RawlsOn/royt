from rest_framework.routers import DefaultRouter
from django.conf import settings

from django.urls import re_path, path, include

from . import apis

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('상가매물', apis.상가매물ViewSet)
router.register('토지매물', apis.토지매물ViewSet)
router.register('건물매물', apis.건물매물ViewSet)

urlpatterns = [
    # path('immortal/', apis.Uploader.as_view(), name='upload_excel'),

    path('core/', include(router.urls)),
]
