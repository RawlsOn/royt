"""
특정 채널의 비디오 상세 정보를 저장하는 커맨드
"""
import json
from django.core.management.base import BaseCommand
from youtube.youtube_api_wrapper import YouTubeAPIWrapper


class Command(BaseCommand):
    help = '특정 채널의 비디오 상세 정보(조회수, 좋아요 등)를 조회하고 저장합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            'channel_identifier',
            type=str,
            help='유튜브 채널 ID 또는 핸들 (예: @username 또는 UC...)'
        )

    def handle(self, *args, **options):
        channel_identifier = options['channel_identifier']

        self.stdout.write(self.style.SUCCESS(f'\n{"="*80}'))
        self.stdout.write(self.style.SUCCESS(f'채널 비디오 상세 정보 저장'))
        self.stdout.write(self.style.SUCCESS(f'{"="*80}\n'))

        self.stdout.write(f'채널 식별자: {channel_identifier}\n')

        try:
            # YouTube API 래퍼 초기화
            youtube_api = YouTubeAPIWrapper(save_to_db=True, verbose=True)

            self.stdout.write(self.style.WARNING('비디오 상세 정보 조회 시작...\n'))

            # 채널 비디오 상세 정보 저장
            result = youtube_api.save_channel_video_details(channel_identifier)

            # 결과 출력
            self.stdout.write(self.style.SUCCESS(f'\n{"="*80}'))
            self.stdout.write(self.style.SUCCESS('✅ 처리 완료!'))
            self.stdout.write(self.style.SUCCESS(f'{"="*80}\n'))

            self.stdout.write(f'📊 처리 결과:')
            self.stdout.write(f'  - 전체 비디오: {result["total_videos"]}개')
            self.stdout.write(f'  - 건너뛴 비디오: {result["skipped"]}개 (이미 상세 정보 있음)')
            self.stdout.write(f'  - 처리 성공: {result["processed"]}개')
            self.stdout.write(f'  - 처리 실패: {result["failed"]}개')
            self.stdout.write(f'  - API 호출 수: {result["api_calls"]}회\n')

            # JSON 형식으로도 출력
            self.stdout.write(self.style.SUCCESS(f'\n{"─"*80}'))
            self.stdout.write(self.style.SUCCESS('JSON 형식:'))
            self.stdout.write(self.style.SUCCESS(f'{"─"*80}\n'))
            self.stdout.write(json.dumps(result, indent=2, ensure_ascii=False))

            self.stdout.write(self.style.SUCCESS(f'\n{"="*80}'))
            self.stdout.write(self.style.SUCCESS('✅ 작업 완료!'))
            self.stdout.write(self.style.SUCCESS(f'{"="*80}\n'))

        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'\n❌ 설정 오류: {e}'))
            self.stdout.write(self.style.ERROR('YouTube API 키가 올바르게 설정되어 있는지 확인하세요.\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ 예상치 못한 오류 발생: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
