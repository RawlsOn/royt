from rest_framework.routers import DefaultRouter
from django.conf import settings

from django.urls import re_path, path, include

from . import apis

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register('매물노트', apis.매물노트ViewSet)

router = DefaultRouter()
urlpatterns = [
    path('main/', include(router.urls)),
    # path('main/매물노트/', apis.매물노트.as_view(), name='매물노트'),
]
