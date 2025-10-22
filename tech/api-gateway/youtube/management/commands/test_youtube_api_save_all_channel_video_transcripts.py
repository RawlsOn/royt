"""
YouTube API save_all_channel_video_transcripts
"""
from django.core.management.base import BaseCommand
from youtube.youtube_api_wrapper import YouTubeAPIWrapper


class Command(BaseCommand):
    help = 'YouTube API - save_all_channel_video_transcripts: 채널의 모든 영상 자막 일괄 저장'

    def add_arguments(self, parser):
        parser.add_argument(
            'channel_identifier',
            type=str,
            help='채널 ID 또는 핸들 (예: @떠들썩, UC_x5XG1OV2P6uZZ5FSM9Ttw)'
        )
        parser.add_argument(
            '--languages',
            type=str,
            default='ko',
            help='우선순위 언어 (쉼표로 구분, 기본값: ko)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='상세한 로그 출력'
        )

    def handle(self, *args, **options):
        channel_identifier = options['channel_identifier']
        languages = options['languages'].split(',')
        verbose = options['verbose']

        youtube_api = YouTubeAPIWrapper(save_to_db=True, verbose=verbose)

        result = youtube_api.save_all_channel_video_transcripts(
            channel_identifier=channel_identifier,
            languages=languages
        )

        # 결과는 이미 메서드에서 출력되므로 여기서는 추가 출력 없음
