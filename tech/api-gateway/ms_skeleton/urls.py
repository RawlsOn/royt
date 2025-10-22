# /Users/kimmyounghoon/Works/mkay/common/api-gateway/common 여기서 수정한 후 카피해 올 것
# cp ~/Works/mkay/common/api-gateway/common/ms_skeleton/* ./api-gateway/ms_skeleton/

"""skeleton URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework import permissions

# schema_view = get_schema_view(
#     openapi.Info(
#         title=settings.SERVICE_NAME,
#         version="1.0.0",
#         default_version='v1',
#         description="",
#         terms_of_service="https://www.google.com/policies/terms/",
#         contact=openapi.Contact(email="freehn@gmail.com"),
#         license=openapi.License(name="BSD License"),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

from django.contrib.sitemaps.views import sitemap

# sitemaps = {
#     'root': sitemaps.RootSitemap,
#     'chories': sitemaps.ChorySitemap
# }

print('settings.RUNNING_ENV', settings.RUNNING_ENV)

admin.site.site_header = '[' + settings.RUNNING_ENV.upper() + '] ' + settings.SERVICE_NAME
if settings.RUNNING_ENV.upper() == 'PROD':
    admin.site.site_header = settings.SERVICE_NAME

admin.site.site_title = settings.SERVICE_NAME
admin.site.index_title = settings.SERVICE_NAME

urlpatterns = [
    path(settings.ADMIN_PREFIX + '/', admin.site.urls),
    # path('schema/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap')
    path('api/', include('base.urls')),
    path('api/', include('config.urls')),
    # path('api/', include('user.urls')),
    path('api/', include('main.urls')),

    # path('api/', include('dorogglinecore.urls')),
    # path('api/', include('doroggareacore.urls')),

    # path('api/', include('gdbound.urls')),
    # path('api/', include('grid.urls')),

    # path('api/', include('onenlc.urls')),

    # path('api/rticler/', include('rticler.urls')),
]

# print(settings.APP_TO_ADD)

# for app in settings.APP_TO_ADD:
#     if app:
#         app_name, project_name = app.split('|')
#         urlpatterns += [path('api/', include(app_name + '.urls'))]