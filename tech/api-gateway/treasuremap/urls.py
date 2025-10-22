from rest_framework.routers import DefaultRouter
from django.conf import settings

from django.urls import re_path, path, include

from . import apis

from django.contrib import admin

urlpatterns = [
    path('immortal/', apis.Uploader.as_view(), name='upload_excel'),
]
