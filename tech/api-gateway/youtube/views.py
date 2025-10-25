from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

import youtube.models as youtube_models
import youtube.serializers as youtube_serializers


class YouTubeVideoViewSet(viewsets.ModelViewSet):
    """YouTube 영상 ViewSet"""

    queryset = youtube_models.YouTubeVideo.objects.select_related('channel').all()
    serializer_class = youtube_serializers.YouTubeVideoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'category_id': ['exact'],
        'channel': ['exact'],
        'transcript_status': ['exact'],
    }
    ordering_fields = [
        'view_count',
        'like_count',
        'comment_count',
        'engagement_rate',
        'views_per_subscriber',
        'published_at',
        'created_at',
    ]
    ordering = ['-view_count']
