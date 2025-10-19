from rest_framework.routers import DefaultRouter
from django.conf import settings

from django.urls import re_path, path, include

from . import apis

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register('core', apis.CoreViewSet)
# router.register('jijeok', apis.JijeokMultiShapeViewSet)
# router.register('토지매물', apis.토지매물ViewSet)
# router.register('건물매물', apis.건물매물ViewSet)

urlpatterns = [
    # path('core/jijeok/', apis.Jijeok.as_view(), name='jijeok'),

    # path('core/jijeok/<str:pnu>/', apis.JijeokByPnu.as_view(), name='jijeok-pnu'),

    # path('doroggareacore/', include(router.urls)),

    # path('core/searched-keyword/', apis.SearchedKeyword.as_view(),
    #     name="SearchedKeyword"
    # ),
]
