"""
특정 채널의 모든 영상 텍스트 데이터를 JSON 파일로 내보내기
"""
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from youtube.models import YouTubeChannel, YouTubeVideo


class Command(BaseCommand):
    help = '특정 채널의 모든 영상 텍스트 데이터(제목, 스크립트)를 JSON 파일로 내보내기'

    def add_arguments(self, parser):
        parser.add_argument(
            '--channel',
            type=str,
            required=True,
            help='내보낼 채널 ID 또는 핸들 (예: UCPF2WvEWPP-1utUwwsdbeCw 또는 @떠들썩)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='/usr/data/roytlocal/',
            help='JSON 파일을 저장할 디렉토리 (기본값: /usr/data/roytlocal/)'
        )
        parser.add_argument(
            '--only-with-transcript',
            action='store_true',
            help='자막이 있는 영상만 내보내기'
        )

    def handle(self, *args, **options):
        channel_input = options.get('channel')
        output_dir = options.get('output_dir')
        only_with_transcript = options.get('only_with_transcript')

        # 채널 조회 (ID 또는 핸들)
        try:
            if channel_input.startswith('@'):
                # 핸들로 조회 (@ 포함)
                channel = YouTubeChannel.objects.get(channel_custom_url=channel_input)
            else:
                # 채널 ID로 조회
                channel = YouTubeChannel.objects.get(channel_id=channel_input)
        except YouTubeChannel.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ 채널을 찾을 수 없습니다: {channel_input}'))
            return

        # 영상 조회
        videos_query = YouTubeVideo.objects.filter(channel=channel)

        if only_with_transcript:
            videos_query = videos_query.filter(
                transcript_status='success',
                transcript__isnull=False
            ).exclude(transcript='')

        videos = videos_query.order_by('-published_at')
        total_count = videos.count()

        if total_count == 0:
            self.stdout.write(self.style.WARNING('⚠️  내보낼 영상이 없습니다.'))
            return

        self.stdout.write(f'\n{"="*80}')
        self.stdout.write(f'📦 채널 데이터 내보내기')
        self.stdout.write(f'{"="*80}')
        self.stdout.write(f'채널: {channel.channel_title}')
        self.stdout.write(f'채널 ID: {channel.channel_id}')
        self.stdout.write(f'총 영상 수: {total_count}개')
        self.stdout.write(f'{"="*80}\n')

        # JSON 데이터 구성
        export_data = {
            'channel': {
                'channel_id': channel.channel_id,
                'channel_title': channel.channel_title,
                'channel_description': channel.channel_description,
                'channel_custom_url': channel.channel_custom_url,
                'subscriber_count': channel.subscriber_count,
                'video_count': channel.video_count,
                'view_count': channel.view_count,
                'channel_country': channel.channel_country,
            },
            'export_info': {
                'exported_at': datetime.now().isoformat(),
                'total_videos': total_count,
                'only_with_transcript': only_with_transcript,
            },
            'videos': []
        }

        # 영상 데이터 추가
        for idx, video in enumerate(videos, 1):
            video_data = {
                'video_id': video.video_id,
                'title': video.title,
                'description': video.description,
                'youtube_url': video.youtube_url or video.generate_youtube_url(),
                'published_at': video.published_at.isoformat() if video.published_at else None,
                'view_count': video.view_count,
                'like_count': video.like_count,
                'comment_count': video.comment_count,
                'duration': video.duration,
                'tags': video.tags,
                'transcript': video.transcript,
                'transcript_language': video.transcript_language,
                'transcript_status': video.transcript_status,
            }

            export_data['videos'].append(video_data)

            # 진행 상황 표시
            if idx % 10 == 0 or idx == total_count:
                self.stdout.write(f'  진행: {idx}/{total_count} ({idx/total_count*100:.1f}%)')

        # 파일명 생성 (채널명 사용, 특수문자 제거)
        safe_channel_name = "".join(
            c for c in channel.channel_title
            if c.isalnum() or c in (' ', '-', '_')
        ).strip()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{safe_channel_name}_{timestamp}.json'
        filepath = f'{output_dir}/{filename}'

        # JSON 파일 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        file_size = len(json.dumps(export_data, ensure_ascii=False))
        file_size_mb = file_size / (1024 * 1024)

        self.stdout.write(f'\n{"="*80}')
        self.stdout.write(self.style.SUCCESS(f'✅ 내보내기 완료!'))
        self.stdout.write(f'{"="*80}')
        self.stdout.write(f'저장 위치: {filepath}')
        self.stdout.write(f'파일 크기: {file_size_mb:.2f} MB')
        self.stdout.write(f'총 영상 수: {total_count}개')
        self.stdout.write(f'{"="*80}\n')
