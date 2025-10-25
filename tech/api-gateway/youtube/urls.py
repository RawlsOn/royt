from rest_framework.routers import DefaultRouter
from youtube import views

router = DefaultRouter()
router.register('videos', views.YouTubeVideoViewSet, basename='youtube-video')

urlpatterns = router.urls
