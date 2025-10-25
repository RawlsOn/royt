from rest_framework import serializers

import youtube.models as youtube_models


class YouTubeChannelSerializer(serializers.ModelSerializer):
    """YouTube 채널 정보 시리얼라이저"""

    class Meta:
        model = youtube_models.YouTubeChannel
        fields = [
            'id',
            'channel_id',
            'channel_title',
            'channel_thumbnail',
            'subscriber_count',
            'view_count',
        ]


class YouTubeVideoSerializer(serializers.ModelSerializer):
    """YouTube 영상 정보 시리얼라이저"""

    channel_data = YouTubeChannelSerializer(source='channel', read_only=True)
    youtube_url = serializers.ReadOnlyField(source='generate_youtube_url')

    class Meta:
        model = youtube_models.YouTubeVideo
        fields = [
            'id',
            'video_id',
            'title',
            'description',
            'published_at',
            'view_count',
            'like_count',
            'comment_count',
            'engagement_rate',
            'views_per_subscriber',
            'thumbnail_url',
            'youtube_url',
            'duration',
            'category_id',
            'tags',
            'transcript_status',
            'channel',
            'channel_data',
        ]
