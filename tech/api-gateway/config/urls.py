

from django.urls import re_path, path, include

from config import apis
urlpatterns = [

    path(
        'config/seo/',
        apis.SEO.as_view(),
        name="api_SEO"
    ),

    path(
        'config/base-setting/',
        apis.BaseSetting.as_view(),
        name="api_BaseSetting"
    ),

]
