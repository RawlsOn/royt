"""
YouTube API get_channel_info 메소드 테스트 커맨드
"""
import json
from django.core.management.base import BaseCommand
from youtube.youtube_api_wrapper import YouTubeAPIWrapper


class Command(BaseCommand):
    help = 'YouTube API의 get_channel_info 메소드를 테스트합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            'channel_identifier',
            type=str,
            help='유튜브 채널 ID 또는 핸들 (예: @username 또는 UC...)'
        )
        parser.add_argument(
            '--no-db',
            action='store_true',
            help='DB에 저장하지 않고 API 결과만 조회합니다'
        )

    def handle(self, *args, **options):
        channel_identifier = options['channel_identifier']
        save_to_db = not options['no_db']

        self.stdout.write(self.style.SUCCESS(f'\n{"="*80}'))
        self.stdout.write(self.style.SUCCESS(f'YouTube API get_channel_info 테스트'))
        self.stdout.write(self.style.SUCCESS(f'{"="*80}\n'))

        self.stdout.write(f'채널 식별자: {channel_identifier}')
        self.stdout.write(f'DB 저장: {"예" if save_to_db else "아니오"}\n')

        try:
            # YouTube API 래퍼 초기화
            youtube_api = YouTubeAPIWrapper(save_to_db=save_to_db)

            self.stdout.write(self.style.WARNING('API 호출 중...\n'))

            # 채널 정보 조회
            channel_info = youtube_api.get_channel_info(channel_identifier)

            if channel_info:
                self.stdout.write(self.style.SUCCESS('✅ 채널 정보 조회 성공!\n'))

                # 결과를 보기 좋게 출력
                self.stdout.write(self.style.SUCCESS(f'{"─"*80}'))
                self.stdout.write(self.style.SUCCESS('채널 정보:'))
                self.stdout.write(self.style.SUCCESS(f'{"─"*80}\n'))

                # 주요 정보 먼저 표시
                self.stdout.write(f'📺 채널명: {channel_info["channel_title"]}')
                self.stdout.write(f'🆔 채널 ID: {channel_info["channel_id"]}')
                self.stdout.write(f'🔗 커스텀 URL: {channel_info.get("channel_custom_url", "N/A")}')
                self.stdout.write(f'📅 생성일: {channel_info.get("channel_published_at", "N/A")}')
                self.stdout.write(f'🌍 국가: {channel_info.get("channel_country", "N/A")}\n')

                # 통계 정보
                self.stdout.write(self.style.WARNING('📊 통계:'))
                self.stdout.write(f'  - 구독자 수: {channel_info["subscriber_count"]:,}명')
                self.stdout.write(f'  - 동영상 수: {channel_info["video_count"]:,}개')
                self.stdout.write(f'  - 총 조회수: {channel_info["view_count"]:,}회\n')

                # 설명
                description = channel_info.get("channel_description", "")
                if description:
                    self.stdout.write(self.style.WARNING('📝 채널 설명:'))
                    # 설명이 너무 길면 첫 200자만 표시
                    if len(description) > 200:
                        self.stdout.write(f'{description[:200]}...\n')
                    else:
                        self.stdout.write(f'{description}\n')

                # 썸네일
                if channel_info.get("channel_thumbnail"):
                    self.stdout.write(f'🖼️  썸네일 URL: {channel_info["channel_thumbnail"]}\n')

                # 업로드 플레이리스트 ID
                if channel_info.get("uploads_playlist_id"):
                    self.stdout.write(f'📂 업로드 플레이리스트 ID: {channel_info["uploads_playlist_id"]}\n')

                # JSON 형식으로도 출력
                self.stdout.write(self.style.SUCCESS(f'\n{"─"*80}'))
                self.stdout.write(self.style.SUCCESS('JSON 형식:'))
                self.stdout.write(self.style.SUCCESS(f'{"─"*80}\n'))
                self.stdout.write(json.dumps(channel_info, indent=2, ensure_ascii=False))

                self.stdout.write(self.style.SUCCESS(f'\n{"="*80}'))
                self.stdout.write(self.style.SUCCESS('✅ 테스트 완료!'))
                self.stdout.write(self.style.SUCCESS(f'{"="*80}\n'))

            else:
                self.stdout.write(self.style.ERROR('❌ 채널 정보를 가져오지 못했습니다.'))
                self.stdout.write(self.style.ERROR('채널 ID 또는 핸들을 확인해주세요.\n'))

        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'\n❌ 설정 오류: {e}'))
            self.stdout.write(self.style.ERROR('YouTube API 키가 올바르게 설정되어 있는지 확인하세요.\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ 예상치 못한 오류 발생: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
