from rest_framework.routers import DefaultRouter

from django.urls import re_path, path, include

from . import apis

router = DefaultRouter()
router.register('article', apis.ArticleViewSet)
router.register('temp-article', apis.TempArticleViewSet)

router.register('comment', apis.CommentViewSet)


urlpatterns = [

    path('', include(router.urls)),

    # path('user/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
