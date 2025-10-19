from rest_framework.routers import DefaultRouter
from django.conf import settings

from django.urls import re_path, path, include

from . import apis

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('geo-unit', apis.GeoUnitViewSet)

urlpatterns = [
    # path('immortal/', apis.Uploader.as_view(), name='upload_excel'),

    path('geoinfo/', include(router.urls)),
]
