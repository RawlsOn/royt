from django.contrib import admin
from youtube.models import YouTubeChannel, YouTubeVideo, YouTubeVideoStatHistory, YouTubeVideoCategory


@admin.register(YouTubeChannel)
class YouTubeChannelAdmin(admin.ModelAdmin):
    list_display = ('channel_title', 'subscriber_count', 'video_count', 'view_count', 'channel_country', 'is_excluded', 'updated_at')
    list_filter = ('is_excluded', 'channel_country', 'created_date')
    search_fields = ('channel_title', 'channel_id', 'channel_custom_url')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-subscriber_count',)
    list_editable = ('is_excluded',)


@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel', 'view_count', 'like_count', 'comment_count', 'transcript_status', 'transcript_language', 'published_at', 'created_at')
    list_filter = ('transcript_status', 'category_id', 'created_date', 'published_at')
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


@admin.register(YouTubeVideoCategory)
class YouTubeVideoCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_title', 'region_code', 'assignable', 'updated_at')
    list_filter = ('region_code', 'assignable')
    search_fields = ('category_id', 'category_title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('region_code', 'category_id')
