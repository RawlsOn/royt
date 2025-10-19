from django.contrib import admin
from youtube.models import YouTubeChannel, YouTubeVideo, YouTubeVideoStatHistory


@admin.register(YouTubeChannel)
class YouTubeChannelAdmin(admin.ModelAdmin):
    list_display = ('channel_title', 'subscriber_count', 'video_count', 'view_count', 'channel_country', 'created_at')
    list_filter = ('channel_country', 'created_date')
    search_fields = ('channel_title', 'channel_id', 'channel_custom_url')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-subscriber_count',)


@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel', 'view_count', 'like_count', 'comment_count', 'published_at', 'created_at')
    list_filter = ('category_id', 'created_date', 'published_at')
    search_fields = ('title', 'video_id', 'channel__channel_title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-view_count',)
    raw_id_fields = ('channel',)


@admin.register(YouTubeVideoStatHistory)
class YouTubeVideoStatHistoryAdmin(admin.ModelAdmin):
    list_display = ('video', 'view_count', 'like_count', 'comment_count', 'snapshot_at')
    list_filter = ('snapshot_at',)
    search_fields = ('video__title', 'video__video_id')
    readonly_fields = ('snapshot_at',)
    ordering = ('-snapshot_at',)
    raw_id_fields = ('video',)
