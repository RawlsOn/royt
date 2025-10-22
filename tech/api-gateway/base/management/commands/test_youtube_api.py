"""
YouTube API Wrapper 테스트 커맨드
"""
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from common.util.youtube_api_wrapper import YouTubeAPIWrapper


class Command(BaseCommand):
    help = "YouTube API Wrapper 기능 테스트"

    def add_arguments(self, parser):
        parser.add_argument(
            '--channel-id',
            type=str,
            default='@juegagerman',  # 예시 채널 핸들
            help='테스트할 채널 ID 또는 핸들 (@username 형태, 기본값: @juegagerman)'
        )
        parser.add_argument(
            '--max-results',
            type=int,
            default=10,
            help='조회할 영상 개수 (기본값: 10, 최대: 50)'
        )
        parser.add_argument(
            '--test-all',
            action='store_true',
            help='모든 테스트 실행 (채널 정보 + 영상 목록)'
        )
        parser.add_argument(
            '--test-channel',
            action='store_true',
            help='채널 정보 조회 테스트만 실행'
        )
        parser.add_argument(
            '--test-videos',
            action='store_true',
            help='영상 목록 조회 테스트만 실행'
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='JSON 형식으로 결과 출력'
        )

    def handle(self, *args, **options):
        # YouTube API 키 확인
        api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
        if not api_key:
            self.stdout.write(
                self.style.ERROR('❌ YouTube API 키가 설정되지 않았습니다.')
            )
            self.stdout.write(
                'settings.py 또는 .env 파일에 YOUTUBE_API_KEY를 추가해주세요.'
            )
            return

        channel_id = options['channel_id']
        max_results = min(options['max_results'], 50)
        output_json = options['json']

        # 테스트 옵션 확인
        test_all = options['test_all']
        test_channel = options['test_channel']
        test_videos = options['test_videos']

        # 기본값: 모든 테스트 실행
        if not (test_channel or test_videos):
            test_all = True

        try:
            # API 래퍼 초기화
            youtube = YouTubeAPIWrapper(api_key)

            self.stdout.write('')
            self.stdout.write(self.style.WARNING('=' * 100))
            self.stdout.write(self.style.WARNING('YouTube API Wrapper 테스트'))
            self.stdout.write(self.style.WARNING('=' * 100))
            self.stdout.write('')

            # 1. 채널 정보 조회 테스트
            channel_info = None
            if test_all or test_channel:
                self.stdout.write(self.style.SUCCESS('■ 채널 정보 조회 테스트'))
                self.stdout.write(f'   채널 ID: {channel_id}')
                self.stdout.write('')

                channel_info = youtube.get_channel_info(channel_id)

                if channel_info:
                    if output_json:
                        self.stdout.write(json.dumps(channel_info, ensure_ascii=False, indent=2))
                    else:
                        self._display_channel_info(channel_info)
                else:
                    self.stdout.write(
                        self.style.ERROR('   ❌ 채널 정보를 조회할 수 없습니다.')
                    )

                self.stdout.write('')
                self.stdout.write('-' * 100)
                self.stdout.write('')

            # 2. 영상 목록 조회 테스트
            if test_all or test_videos:
                self.stdout.write(self.style.SUCCESS('■ 영상 목록 조회 테스트'))
                self.stdout.write(f'   채널 ID: {channel_id}')
                self.stdout.write(f'   최대 개수: {max_results}')
                self.stdout.write('')

                videos = youtube.list_channel_videos(
                    channel_identifier=channel_id,
                    max_results=max_results
                )

                if videos:
                    if output_json:
                        self.stdout.write(json.dumps(videos, ensure_ascii=False, indent=2))
                    else:
                        self._display_videos(videos, channel_info)

                    # 통계 요약
                    self.stdout.write('')
                    self.stdout.write(self.style.SUCCESS(f'✅ 총 {len(videos)}개의 영상 조회 완료'))

                    if videos:
                        shorts_count = sum(1 for v in videos if v['is_short'])
                        regular_count = len(videos) - shorts_count
                        self.stdout.write(f'   - 쇼츠: {shorts_count}개')
                        self.stdout.write(f'   - 일반 영상: {regular_count}개')

                        # 평균 duration 계산
                        total_duration = sum(v['duration_seconds'] for v in videos)
                        avg_duration = total_duration / len(videos) if videos else 0
                        self.stdout.write(f'   - 평균 길이: {self._format_seconds(int(avg_duration))}')
                else:
                    self.stdout.write(
                        self.style.ERROR('   ❌ 영상 목록을 조회할 수 없습니다.')
                    )

                self.stdout.write('')
                self.stdout.write('-' * 100)

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✅ 테스트 완료'))
            self.stdout.write('')

        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'❌ 초기화 실패: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 테스트 중 오류 발생: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())

    def _display_channel_info(self, channel_info: dict):
        """채널 정보를 보기 좋게 출력"""
        self.stdout.write(self.style.SUCCESS(f'   ✅ 채널: {channel_info["channel_title"]}'))
        self.stdout.write('')

        # 기본 정보
        self.stdout.write('   📋 기본 정보')
        self.stdout.write(f'      - 채널 ID: {channel_info["channel_id"]}')
        if channel_info.get('channel_custom_url'):
            self.stdout.write(f'      - URL: https://youtube.com/{channel_info["channel_custom_url"]}')
        if channel_info.get('channel_country'):
            self.stdout.write(f'      - 국가: {channel_info["channel_country"]}')
        self.stdout.write(f'      - 생성일: {self._format_datetime(channel_info["channel_published_at"])}')
        self.stdout.write('')

        # 통계
        self.stdout.write('   📊 통계')
        self.stdout.write(f'      - 구독자: {self._format_number(channel_info["subscriber_count"])}명')
        self.stdout.write(f'      - 영상 수: {self._format_number(channel_info["video_count"])}개')
        self.stdout.write(f'      - 총 조회수: {self._format_number(channel_info["view_count"])}회')
        self.stdout.write('')

        # 설명 (처음 3줄만)
        if channel_info.get('channel_description'):
            desc_lines = channel_info['channel_description'].split('\n')[:3]
            self.stdout.write('   📝 채널 설명')
            for line in desc_lines:
                if line.strip():
                    self.stdout.write(f'      {line[:100]}')
            if len(channel_info['channel_description'].split('\n')) > 3:
                self.stdout.write('      ...')

    def _display_videos(self, videos: list, channel_info: dict = None):
        """영상 목록을 보기 좋게 출력"""
        for idx, video in enumerate(videos, 1):
            self.stdout.write('')

            # 제목 (쇼츠 표시)
            title_prefix = '🩳' if video['is_short'] else '🎬'
            self.stdout.write(
                self.style.SUCCESS(f'{title_prefix} [{idx}] {video["title"][:80]}')
            )

            # 영상 정보
            self.stdout.write(f'      - 비디오 ID: {video["video_id"]}')
            self.stdout.write(f'      - 게시일: {self._format_datetime(video["published_at"])}')
            self.stdout.write(f'      - 길이: {self._format_duration(video["duration"])} ({video["duration_seconds"]}초)')
            self.stdout.write(f'      - URL: https://www.youtube.com/watch?v={video["video_id"]}')

            # 설명 (첫 줄만)
            if video.get('description'):
                desc_lines = video['description'].split('\n')
                first_line = next((line for line in desc_lines if line.strip()), '')
                if first_line:
                    self.stdout.write(f'      - 설명: {first_line[:100]}...')

    def _format_number(self, num: int) -> str:
        """숫자를 읽기 쉬운 형식으로 변환"""
        if num >= 100000000:  # 1억 이상
            return f'{num / 100000000:.1f}억'
        elif num >= 10000:  # 1만 이상
            return f'{num / 10000:.1f}만'
        else:
            return f'{num:,}'

    def _format_datetime(self, dt_str: str) -> str:
        """ISO 8601 형식의 날짜를 읽기 쉬운 형식으로 변환"""
        if not dt_str:
            return ''
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, AttributeError):
            return dt_str

    def _format_duration(self, duration: str) -> str:
        """ISO 8601 duration을 읽기 쉬운 형식으로 변환"""
        if not duration or not duration.startswith('PT'):
            return duration

        duration = duration[2:]  # PT 제거
        hours = 0
        minutes = 0
        seconds = 0

        if 'H' in duration:
            hours = int(duration.split('H')[0])
            duration = duration.split('H')[1]

        if 'M' in duration:
            minutes = int(duration.split('M')[0])
            duration = duration.split('M')[1]

        if 'S' in duration:
            seconds = int(duration.split('S')[0])

        parts = []
        if hours:
            parts.append(f'{hours}시간')
        if minutes:
            parts.append(f'{minutes}분')
        if seconds or not parts:  # seconds가 0이어도 다른 값이 없으면 표시
            parts.append(f'{seconds}초')

        return ' '.join(parts)

    def _format_seconds(self, seconds: int) -> str:
        """초를 읽기 쉬운 형식으로 변환"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        parts = []
        if hours:
            parts.append(f'{hours}시간')
        if minutes:
            parts.append(f'{minutes}분')
        if secs or not parts:
            parts.append(f'{secs}초')

        return ' '.join(parts)
