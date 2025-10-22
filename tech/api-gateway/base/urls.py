from django.urls import re_path, path, include

from . import apis

urlpatterns = [

    path(
        'log4j/',
        apis.Log4j.as_view(),
        name="api_Log4j"
    ),
    path(
        'fev/',
        apis.GetFrontendVersion.as_view(),
        name="api_GetFrontendVersion"
    )
]
