"""
YouTube 영상 및 채널 정보 모델
"""
from django.db import models
from base.models import RoBase


class YouTubeChannel(RoBase):
    """YouTube 채널 정보"""

    channel_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="채널 ID"
    )
    uploads_playlist_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="업로드 플레이리스트 ID"
    )
    channel_title = models.CharField(
        max_length=200,
        verbose_name="채널명"
    )
    channel_description = models.TextField(
        blank=True,
        verbose_name="채널 설명"
    )
    channel_custom_url = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="채널 커스텀 URL"
    )
    channel_published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="채널 생성일"
    )
    channel_thumbnail = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="채널 썸네일"
    )
    channel_country = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="국가"
    )

    # 통계 정보
    subscriber_count = models.BigIntegerField(
        default=0,
        db_index=True,
        verbose_name="구독자 수"
    )
    video_count = models.BigIntegerField(
        default=0,
        verbose_name="영상 수"
    )
    view_count = models.BigIntegerField(
        default=0,
        db_index=True,
        verbose_name="총 조회수"
    )

    # 메타 정보
    channel_keywords = models.TextField(
        blank=True,
        verbose_name="채널 키워드"
    )

    class Meta:
        ordering = ['-subscriber_count', '-view_count']
        verbose_name = "YouTube 채널"
        verbose_name_plural = "YouTube 채널"
        indexes = [
            models.Index(fields=['-subscriber_count', '-view_count']),
        ]

    def __str__(self):
        return f"{self.channel_title} ({self.format_number(self.subscriber_count)}명)"

    @staticmethod
    def format_number(num):
        """숫자를 읽기 쉬운 형식으로 변환"""
        if num >= 100000000:  # 1억 이상
            return f'{num / 100000000:.1f}억'
        elif num >= 10000:  # 1만 이상
            return f'{num / 10000:.1f}만'
        else:
            return f'{num:,}'


class YouTubeVideo(RoBase):
    """YouTube 영상 정보"""

    video_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name="비디오 ID"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="제목"
    )
    description = models.TextField(
        blank=True,
        verbose_name="설명"
    )

    # 채널 정보 (FK)
    channel = models.ForeignKey(
        YouTubeChannel,
        on_delete=models.CASCADE,
        related_name='videos',
        verbose_name="채널"
    )

    # 게시 정보
    published_at = models.DateTimeField(
        db_index=True,
        verbose_name="게시일"
    )
    thumbnail_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="썸네일"
    )
    youtube_url = models.URLField(
        max_length=200,
        blank=True,
        verbose_name="YouTube URL"
    )

    # 통계 정보
    view_count = models.BigIntegerField(
        default=0,
        db_index=True,
        verbose_name="조회수"
    )
    like_count = models.BigIntegerField(
        default=0,
        verbose_name="좋아요 수"
    )
    comment_count = models.BigIntegerField(
        default=0,
        verbose_name="댓글 수"
    )
    engagement_rate = models.FloatField(
        default=0.0,
        db_index=True,
        verbose_name="참여율 (%)"
    )
    views_per_subscriber = models.FloatField(
        default=0.0,
        db_index=True,
        verbose_name="구독자 대비 조회수 (배수)"
    )

    # 메타 정보
    duration = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="길이"
    )
    category_id = models.CharField(
        max_length=10,
        blank=True,
        db_index=True,
        verbose_name="카테고리 ID"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name="태그"
    )

    # 자막 정보
    transcript = models.TextField(
        blank=True,
        verbose_name="자막 (전체 텍스트)"
    )
    transcript_language = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="자막 언어 코드"
    )
    transcript_status = models.CharField(
        max_length=20,
        blank=True,
        db_index=True,
        verbose_name="자막 조회 상태",
        help_text="success: 성공, no_transcript: 자막 없음, disabled: 비활성화, unavailable: 비디오 사용 불가, error: 기타 오류"
    )

    # 정리된 자막 정보
    refined_transcript = models.TextField(
        blank=True,
        verbose_name="정리된 자막 (AI 수정)"
    )
    refined_transcript_status = models.CharField(
        max_length=20,
        blank=True,
        db_index=True,
        verbose_name="자막 정리 상태",
        help_text="pending: 대기, processing: 처리 중, completed: 완료, failed: 실패"
    )

    class Meta:
        ordering = ['-view_count', '-published_at']
        verbose_name = "YouTube 영상"
        verbose_name_plural = "YouTube 영상"
        indexes = [
            models.Index(fields=['-view_count', '-published_at']),
            models.Index(fields=['category_id', '-view_count']),
        ]

    def __str__(self):
        return f"{self.title} ({self.format_number(self.view_count)}회)"

    def calculate_engagement_rate(self):
        """참여율 계산"""
        if self.view_count == 0:
            return 0.0
        return (self.like_count + self.comment_count) / self.view_count * 100

    def generate_youtube_url(self):
        """YouTube URL 생성"""
        return f"https://www.youtube.com/watch?v={self.video_id}"

    @staticmethod
    def format_number(num):
        """숫자를 읽기 쉬운 형식으로 변환"""
        if num >= 100000000:  # 1억 이상
            return f'{num / 100000000:.1f}억'
        elif num >= 10000:  # 1만 이상
            return f'{num / 10000:.1f}만'
        else:
            return f'{num:,}'


class YouTubeVideoStatHistory(RoBase):
    """영상 통계 히스토리 (시간대별 변화 추적)"""

    video = models.ForeignKey(
        YouTubeVideo,
        on_delete=models.CASCADE,
        related_name='stat_history',
        verbose_name="영상"
    )

    # 스냅샷 통계
    view_count = models.BigIntegerField(
        verbose_name="조회수"
    )
    like_count = models.BigIntegerField(
        verbose_name="좋아요 수"
    )
    comment_count = models.BigIntegerField(
        verbose_name="댓글 수"
    )
    engagement_rate = models.FloatField(
        default=0.0,
        verbose_name="참여율 (%)"
    )
    views_per_subscriber = models.FloatField(
        default=0.0,
        verbose_name="구독자 대비 조회수 (배수)"
    )

    # 시각 정보
    original_saved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="원본 데이터 저장 시각"
    )
    snapshot_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="히스토리 저장 시각"
    )

    class Meta:
        ordering = ['-snapshot_at']
        verbose_name = "YouTube 영상 통계 히스토리"
        verbose_name_plural = "YouTube 영상 통계 히스토리"
        indexes = [
            models.Index(fields=['video', '-snapshot_at']),
        ]

    def __str__(self):
        return f"{self.video.title} - {self.snapshot_at}"

    @property
    def view_count_formatted(self):
        """조회수 포맷"""
        return YouTubeVideo.format_number(self.view_count)
