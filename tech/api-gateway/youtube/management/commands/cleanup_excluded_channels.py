"""
제외된 채널의 영상 및 데이터 정리 커맨드
"""
from django.core.management.base import BaseCommand
from common.util.youtube_cleanup_util import YouTubeCleanup


class Command(BaseCommand):
    help = "제외된 채널(is_excluded=True)의 영상 및 관련 데이터 삭제"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제로 삭제하지 않고 삭제될 항목만 표시'
        )
        parser.add_argument(
            '--no-confirm',
            action='store_true',
            help='확인 절차 없이 바로 삭제 실행'
        )
        parser.add_argument(
            '--delete-channels',
            action='store_true',
            help='영상뿐만 아니라 제외된 채널도 함께 삭제'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        no_confirm = options['no_confirm']
        delete_channels = options['delete_channels']

        self.stdout.write('')
        self.print_separator()
        self.stdout.write(
            self.style.WARNING('🗑️  제외된 채널 데이터 정리')
        )
        self.print_separator()
        self.stdout.write('')

        # 1. 현재 통계 조회
        self.stdout.write(self.style.WARNING('📊 현재 DB 상태 조회 중...'))
        self.stdout.write('')

        stats = YouTubeCleanup.get_excluded_channels_stats()

        if stats['excluded_channel_count'] == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ 제외된 채널이 없습니다.')
            )
            self.stdout.write('')
            return

        # 2. 통계 출력
        self.print_sub_separator()
        self.stdout.write(self.style.WARNING('제외된 채널 통계:'))
        self.print_sub_separator()
        self.stdout.write(f'📺 채널: {stats["excluded_channel_count"]:,}개')
        self.stdout.write(f'🎬 영상: {stats["excluded_video_count"]:,}개')
        self.stdout.write(f'📊 통계 히스토리: {stats["excluded_stats_count"]:,}개')
        self.stdout.write('')

        # 3. 채널 목록 출력
        if stats['excluded_channel_count'] > 0:
            self.print_sub_separator()
            self.stdout.write(self.style.WARNING('제외된 채널 목록:'))
            self.print_sub_separator()

            for idx, channel in enumerate(stats['excluded_channels'][:10], 1):
                video_count = channel.videos.count()
                self.stdout.write(
                    f'{idx}. {channel.channel_title} '
                    f'(구독자: {self.format_number(channel.subscriber_count)}, '
                    f'DB 영상: {video_count:,}개)'
                )

            if stats['excluded_channel_count'] > 10:
                self.stdout.write(
                    self.style.WARNING(f'... 외 {stats["excluded_channel_count"] - 10}개 채널')
                )

            self.stdout.write('')

        # 4. Dry run 모드
        if dry_run:
            self.print_separator()
            self.stdout.write(
                self.style.SUCCESS('✅ [DRY RUN] 실제로 삭제되지 않았습니다.')
            )
            self.stdout.write('')
            self.stdout.write('삭제될 항목:')
            if delete_channels:
                self.stdout.write(f'  - 채널: {stats["excluded_channel_count"]:,}개')
            self.stdout.write(f'  - 영상: {stats["excluded_video_count"]:,}개')
            self.stdout.write(f'  - 통계 히스토리: {stats["excluded_stats_count"]:,}개')
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING('실제로 삭제하려면 --dry-run 옵션 없이 실행하세요.')
            )
            self.print_separator()
            self.stdout.write('')
            return

        # 5. 확인 절차
        if not no_confirm:
            self.print_sub_separator()
            self.stdout.write(
                self.style.ERROR('⚠️  경고: 이 작업은 되돌릴 수 없습니다!')
            )
            self.print_sub_separator()
            self.stdout.write('')
            self.stdout.write('삭제될 항목:')
            if delete_channels:
                self.stdout.write(
                    self.style.ERROR(f'  - 채널: {stats["excluded_channel_count"]:,}개')
                )
            self.stdout.write(
                self.style.ERROR(f'  - 영상: {stats["excluded_video_count"]:,}개')
            )
            self.stdout.write(
                self.style.ERROR(f'  - 통계 히스토리: {stats["excluded_stats_count"]:,}개')
            )
            self.stdout.write('')

            confirm = input('정말로 삭제하시겠습니까? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write('')
                self.stdout.write(
                    self.style.WARNING('❌ 삭제가 취소되었습니다.')
                )
                self.stdout.write('')
                return

        # 6. 삭제 실행
        self.stdout.write('')
        self.print_sub_separator()
        self.stdout.write(self.style.WARNING('🗑️  삭제 중...'))
        self.print_sub_separator()
        self.stdout.write('')

        result = YouTubeCleanup.delete_excluded_videos(delete_channels=delete_channels)

        # 7. 결과 출력
        self.print_separator()
        self.stdout.write(
            self.style.SUCCESS('✅ 삭제 완료!')
        )
        self.print_separator()
        self.stdout.write('')
        self.stdout.write('삭제된 항목:')
        if delete_channels:
            self.stdout.write(
                self.style.SUCCESS(f'  📺 채널: {result["deleted_channels"]:,}개')
            )
        self.stdout.write(
            self.style.SUCCESS(f'  🎬 영상: {result["deleted_videos"]:,}개')
        )
        self.stdout.write(
            self.style.SUCCESS(f'  📊 통계 히스토리: {result["deleted_stats"]:,}개')
        )
        self.stdout.write('')

        self.print_separator()
        self.stdout.write('')

    def print_separator(self, char: str = '=', length: int = 80):
        """구분선 출력"""
        self.stdout.write(char * length)

    def print_sub_separator(self, char: str = '-', length: int = 80):
        """서브 구분선 출력"""
        self.stdout.write(char * length)

    def format_number(self, num: int) -> str:
        """숫자를 읽기 쉬운 형식으로 변환"""
        if num >= 100000000:  # 1억 이상
            return f'{num / 100000000:.1f}억'
        elif num >= 10000:  # 1만 이상
            return f'{num / 10000:.1f}만'
        else:
            return f'{num:,}'
