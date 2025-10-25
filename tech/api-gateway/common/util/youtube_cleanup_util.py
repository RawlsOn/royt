"""
YouTube 데이터 정리 유틸리티
"""
from typing import Dict
from youtube.models import YouTubeChannel, YouTubeVideo, YouTubeVideoStatHistory


class YouTubeCleanup:
    """YouTube DB 정리 유틸리티"""

    @staticmethod
    def get_excluded_channels_stats() -> Dict:
        """
        제외된 채널 및 관련 영상 통계 조회

        Returns:
            통계 정보 딕셔너리
        """
        excluded_channels = YouTubeChannel.objects.filter(is_excluded=True)
        excluded_channel_count = excluded_channels.count()

        # 제외된 채널의 영상 수
        excluded_videos = YouTubeVideo.objects.filter(channel__is_excluded=True)
        excluded_video_count = excluded_videos.count()

        # 제외된 채널의 영상 통계 히스토리 수
        excluded_stats_count = YouTubeVideoStatHistory.objects.filter(
            video__channel__is_excluded=True
        ).count()

        return {
            'excluded_channel_count': excluded_channel_count,
            'excluded_video_count': excluded_video_count,
            'excluded_stats_count': excluded_stats_count,
            'excluded_channels': excluded_channels,
            'excluded_videos': excluded_videos,
        }

    @staticmethod
    def delete_excluded_videos(delete_channels: bool = False) -> Dict:
        """
        제외된 채널의 영상 삭제

        Args:
            delete_channels: True이면 채널도 함께 삭제

        Returns:
            삭제된 항목 수 정보
        """
        # 삭제 전 통계
        stats = YouTubeCleanup.get_excluded_channels_stats()

        deleted_stats = 0
        deleted_videos = 0
        deleted_channels = 0

        # 1. 통계 히스토리 삭제 (CASCADE로 자동 삭제되지만 명시적으로 처리)
        if stats['excluded_stats_count'] > 0:
            deleted_stats = YouTubeVideoStatHistory.objects.filter(
                video__channel__is_excluded=True
            ).delete()[0]

        # 2. 영상 삭제 (CASCADE로 통계 히스토리도 함께 삭제됨)
        if stats['excluded_video_count'] > 0:
            result = YouTubeVideo.objects.filter(
                channel__is_excluded=True
            ).delete()
            deleted_videos = result[0]

        # 3. 채널 삭제 (옵션)
        if delete_channels and stats['excluded_channel_count'] > 0:
            result = YouTubeChannel.objects.filter(
                is_excluded=True
            ).delete()
            deleted_channels = result[0]

        return {
            'deleted_channels': deleted_channels,
            'deleted_videos': deleted_videos,
            'deleted_stats': deleted_stats,
        }

    @staticmethod
    def get_channel_details(channel_id: str = None, is_excluded: bool = None) -> Dict:
        """
        채널 상세 정보 조회

        Args:
            channel_id: 특정 채널 ID (옵션)
            is_excluded: 제외 여부 필터 (옵션)

        Returns:
            채널 정보 리스트
        """
        queryset = YouTubeChannel.objects.all()

        if channel_id:
            queryset = queryset.filter(channel_id=channel_id)

        if is_excluded is not None:
            queryset = queryset.filter(is_excluded=is_excluded)

        channels_info = []
        for channel in queryset:
            video_count = channel.videos.count()
            stats_count = YouTubeVideoStatHistory.objects.filter(
                video__channel=channel
            ).count()

            channels_info.append({
                'channel': channel,
                'video_count_in_db': video_count,
                'stats_count_in_db': stats_count,
            })

        return channels_info
