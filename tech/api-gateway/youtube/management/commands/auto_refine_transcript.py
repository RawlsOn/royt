"""
자막 자동 정리 커맨드
Claude Code가 직접 자막을 정리해서 저장하는 방식
"""
from django.core.management.base import BaseCommand
from youtube.models import YouTubeVideo


class Command(BaseCommand):
    help = '자막 자동 정리 - 정리된 자막을 직접 입력받아 저장'

    def add_arguments(self, parser):
        parser.add_argument(
            '--video-id',
            type=str,
            required=True,
            help='처리할 비디오 ID'
        )
        parser.add_argument(
            '--refined-transcript',
            type=str,
            required=True,
            help='정리된 자막 텍스트'
        )

    def handle(self, *args, **options):
        video_id = options.get('video_id')
        refined_transcript = options.get('refined_transcript')

        try:
            video = YouTubeVideo.objects.get(video_id=video_id)
        except YouTubeVideo.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ 영상을 찾을 수 없습니다: {video_id}'))
            return

        if video.transcript_status != 'success' or not video.transcript:
            self.stdout.write(self.style.ERROR(f'❌ 원본 자막이 없습니다: {video_id}'))
            return

        self.stdout.write(f'\n{"="*80}')
        self.stdout.write(f'📝 자막 정리')
        self.stdout.write(f'{"="*80}')
        self.stdout.write(f'제목: {video.title}')
        self.stdout.write(f'비디오 ID: {video.video_id}')
        self.stdout.write(f'채널: {video.channel.channel_title}')
        self.stdout.write(f'원본 자막 길이: {len(video.transcript)}자')
        self.stdout.write(f'정리된 자막 길이: {len(refined_transcript)}자')
        self.stdout.write(f'{"="*80}\n')

        # DB에 저장
        video.refined_transcript = refined_transcript
        video.refined_transcript_status = 'completed'
        video.save(update_fields=['refined_transcript', 'refined_transcript_status', 'updated_at'])

        self.stdout.write(self.style.SUCCESS(f'✅ 자막 정리 완료!'))
        self.stdout.write(f'\n원본: {video.transcript[:100]}...')
        self.stdout.write(f'정리: {refined_transcript[:100]}...\n')
