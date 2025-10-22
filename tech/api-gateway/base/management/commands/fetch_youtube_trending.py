"""
유튜브 인기 급상승 동영상 조회 커맨드
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.dateparse import parse_datetime
from common.util.youtube_util import YouTubeAPI
from youtube.models import YouTubeChannel, YouTubeVideo, YouTubeVideoStatHistory
from datetime import datetime


def parse_datetime_to_naive(dt_str):
    """
    ISO 8601 형식의 datetime 문자열을 naive datetime으로 변환
    (USE_TZ=False 환경에서 사용)
    """
    if not dt_str:
        return None
    dt = parse_datetime(dt_str)
    if dt and dt.tzinfo is not None:
        # timezone-aware를 naive로 변환
        return dt.replace(tzinfo=None)
    return dt


class Command(BaseCommand):
    help = "유튜브 인기 급상승 동영상 조회"

    def add_arguments(self, parser):
        parser.add_argument(
            '--region',
            type=str,
            default='KR',
            help='국가 코드 (기본값: KR)'
        )
        parser.add_argument(
            '--max-results',
            type=int,
            default=10,
            help='조회할 영상 개수 (기본값: 10, 최대: 50)'
        )
        parser.add_argument(
            '--category',
            type=str,
            default=None,
            help='카테고리 ID (선택사항)'
        )
        parser.add_argument(
            '--show-categories',
            action='store_true',
            help='사용 가능한 카테고리 목록 표시'
        )
        parser.add_argument(
            '--save-db',
            action='store_true',
            help='DB에 저장'
        )
        parser.add_argument(
            '--save-stats',
            action='store_true',
            help='통계 히스토리 저장 (--save-db와 함께 사용)'
        )

    def handle(self, *args, **options):
        # YouTube API 키 확인
        api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
        if not api_key:
            self.stdout.write(
                self.style.ERROR('YouTube API 키가 설정되지 않았습니다.')
            )
            self.stdout.write(
                'settings.py 또는 .env 파일에 YOUTUBE_API_KEY를 추가해주세요.'
            )
            return

        print('api_key', api_key)
        youtube = YouTubeAPI(api_key)

        # 카테고리 목록 표시
        if options['show_categories']:
            self.show_categories(youtube, options['region'])
            return

        # 인기 급상승 동영상 조회
        region = options['region']
        max_results = options['max_results']
        category = options['category']

        self.stdout.write(
            self.style.WARNING(f'\n🔍 유튜브 인기 급상승 동영상 조회 중...')
        )
        self.stdout.write(f'   지역: {region}')
        self.stdout.write(f'   개수: {max_results}')
        if category:
            self.stdout.write(f'   카테고리: {category}')
        self.stdout.write('')

        videos = youtube.get_trending_videos(
            region_code=region,
            max_results=max_results,
            video_category_id=category
        )

        if not videos:
            self.stdout.write(
                self.style.ERROR('동영상을 조회할 수 없습니다.')
            )
            return

        # DB 저장
        if options['save_db']:
            success = self.save_to_db(videos, options['save_stats'])
            if not success:
                return
        else:
            # 결과 출력 (DB 저장하지 않을 때만)
            self.display_videos(videos)

    def show_categories(self, youtube: YouTubeAPI, region: str):
        """카테고리 목록 표시"""
        self.stdout.write(
            self.style.WARNING(f'\n📂 {region} 지역 카테고리 목록:\n')
        )

        categories = youtube.get_video_categories(region_code=region)

        if not categories:
            self.stdout.write(
                self.style.ERROR('카테고리를 조회할 수 없습니다.')
            )
            return

        for cat in categories:
            self.stdout.write(f"   [{cat['id']}] {cat['title']}")

    def save_to_db(self, videos: list, save_stats: bool = False):
        """DB에 저장"""
        self.stdout.write(
            self.style.WARNING(f'\n💾 DB에 저장 중...')
        )

        saved_channels = 0
        updated_channels = 0
        saved_videos = 0
        updated_videos = 0
        saved_stats = 0
        failed_count = 0
        total_count = len(videos)

        for idx, video_data in enumerate(videos, 1):
            try:
                # 진행상황 표시
                self.stdout.write(f'   [{idx}/{total_count}] {video_data.get("title", "Unknown")[:50]}...', ending='\r')
                self.stdout.flush()

                # 1. 채널 정보 저장/업데이트
                channel_info = video_data.get('channel_info')
                if channel_info:
                    channel, created = YouTubeChannel.objects.update_or_create(
                        channel_id=channel_info['channel_id'],
                        defaults={
                            'channel_title': channel_info['channel_title'],
                            'channel_description': channel_info.get('channel_description', ''),
                            'channel_custom_url': channel_info.get('channel_custom_url', ''),
                            'channel_published_at': parse_datetime_to_naive(channel_info.get('channel_published_at')),
                            'channel_thumbnail': channel_info.get('channel_thumbnail', ''),
                            'channel_country': channel_info.get('channel_country', ''),
                            'subscriber_count': channel_info['subscriber_count'],
                            'video_count': channel_info['video_count'],
                            'view_count': channel_info['view_count'],
                            'channel_keywords': channel_info.get('channel_keywords', ''),
                        }
                    )

                    if created:
                        saved_channels += 1
                    else:
                        updated_channels += 1
                else:
                    # 채널 정보가 없으면 기본 채널 생성
                    channel, created = YouTubeChannel.objects.get_or_create(
                        channel_id=video_data['channel_id'],
                        defaults={
                            'channel_title': video_data['channel_title'],
                        }
                    )
                    if created:
                        saved_channels += 1

                # 2. 영상 정보 저장/업데이트
                # 통계 계산
                view_count = video_data['view_count']
                like_count = video_data['like_count']
                comment_count = video_data['comment_count']

                # 참여율 계산
                engagement_rate = 0.0
                if view_count > 0:
                    engagement_rate = (like_count + comment_count) / view_count * 100

                # 구독자 대비 조회수 계산 (배수)
                views_per_subscriber = 0.0
                channel_info = video_data.get('channel_info')
                if channel_info and channel_info.get('subscriber_count', 0) > 0:
                    views_per_subscriber = view_count / channel_info['subscriber_count']

                # 기존 영상이 있는지 확인 (업데이트 전 통계 저장용)
                try:
                    existing_video = YouTubeVideo.objects.get(video_id=video_data['video_id'])
                    # 기존 통계를 히스토리에 저장 (통계가 변경된 경우만)
                    if (existing_video.view_count != view_count or
                        existing_video.like_count != like_count or
                        existing_video.comment_count != comment_count):
                        YouTubeVideoStatHistory.objects.create(
                            video=existing_video,
                            view_count=existing_video.view_count,
                            like_count=existing_video.like_count,
                            comment_count=existing_video.comment_count,
                            engagement_rate=existing_video.engagement_rate,
                            views_per_subscriber=existing_video.views_per_subscriber,
                            original_saved_at=existing_video.updated_at,  # 원본 데이터의 마지막 업데이트 시각
                        )
                        saved_stats += 1
                    video_exists = True
                except YouTubeVideo.DoesNotExist:
                    video_exists = False

                # 영상 정보 업데이트 또는 생성
                video, created = YouTubeVideo.objects.update_or_create(
                    video_id=video_data['video_id'],
                    defaults={
                        'title': video_data['title'][:200],  # 최대 길이 제한
                        'description': video_data.get('description', ''),
                        'channel': channel,
                        'published_at': parse_datetime_to_naive(video_data['published_at']),
                        'thumbnail_url': video_data.get('thumbnail_url', '')[:500],  # 최대 길이 제한
                        'youtube_url': f"https://www.youtube.com/watch?v={video_data['video_id']}",
                        'view_count': view_count,
                        'like_count': like_count,
                        'comment_count': comment_count,
                        'engagement_rate': engagement_rate,
                        'views_per_subscriber': views_per_subscriber,
                        'duration': video_data.get('duration', ''),
                        'category_id': video_data.get('category_id', ''),
                        'tags': video_data.get('tags', []),
                    }
                )

                if created:
                    saved_videos += 1
                else:
                    updated_videos += 1

                # 3. 통계 히스토리 저장 (save_stats 옵션일 때 추가 저장)
                if save_stats and created:
                    # 새로 생성된 경우만 현재 통계 저장 (기존 영상은 위에서 이미 저장됨)
                    YouTubeVideoStatHistory.objects.create(
                        video=video,
                        view_count=view_count,
                        like_count=like_count,
                        comment_count=comment_count,
                        engagement_rate=engagement_rate,
                        views_per_subscriber=views_per_subscriber,
                        original_saved_at=video.created_at,  # 원본 데이터 생성 시각
                    )
                    saved_stats += 1

            except Exception as e:
                failed_count += 1
                self.stdout.write('')  # 진행상황 라인 클리어
                self.stdout.write(
                    self.style.ERROR(f'   ❌ [{idx}/{total_count}] 저장 실패: {video_data.get("title", "Unknown")[:50]}')
                )
                self.stdout.write(
                    self.style.ERROR(f'      에러: {str(e)}')
                )
                import traceback
                self.stdout.write(
                    self.style.ERROR(f'      상세: {traceback.format_exc()}')
                )
                continue

        # 결과 출력
        self.stdout.write('')  # 진행상황 라인 클리어
        self.stdout.write('')

        # 성공/실패 판단
        success_count = saved_videos + updated_videos

        if failed_count == total_count:
            # 전체 실패
            self.stdout.write(
                self.style.ERROR(f'❌ DB 저장 실패! (0/{total_count})')
            )
            return False
        elif failed_count > 0:
            # 일부 실패
            self.stdout.write(
                self.style.WARNING(f'⚠️  DB 저장 부분 완료 ({success_count}/{total_count})')
            )
        else:
            # 전체 성공
            self.stdout.write(
                self.style.SUCCESS(f'✅ DB 저장 완료! ({success_count}/{total_count})')
            )

        self.stdout.write(f'   📺 채널: {saved_channels}개 생성, {updated_channels}개 업데이트')
        self.stdout.write(f'   🎬 영상: {saved_videos}개 생성, {updated_videos}개 업데이트')
        if save_stats:
            self.stdout.write(f'   📊 통계: {saved_stats}개 저장')
        if failed_count > 0:
            self.stdout.write(
                self.style.ERROR(f'   ❌ 실패: {failed_count}개')
            )
        self.stdout.write('')

        return success_count > 0

    def display_videos(self, videos: list):
        """동영상 정보 출력"""
        self.stdout.write(
            self.style.SUCCESS(f'✅ {len(videos)}개의 동영상을 조회했습니다.\n')
        )
        self.stdout.write('=' * 100)

        for idx, video in enumerate(videos, 1):
            self.stdout.write('')
            self.stdout.write(
                self.style.SUCCESS(f'[{idx}] {video["title"]}')
            )
            self.stdout.write('-' * 100)

            # 기본 정보
            self.stdout.write(f'   🎬 비디오 ID: {video["video_id"]}')
            self.stdout.write(f'   📺 채널: {video["channel_title"]}')
            self.stdout.write(f'   🕐 게시일: {self.format_datetime(video["published_at"])}')
            self.stdout.write(f'   ⏱️  길이: {self.format_duration(video["duration"])}')

            # 채널 정보
            if "channel_info" in video:
                ch = video["channel_info"]
                self.stdout.write('')
                self.stdout.write(self.style.WARNING('   ▶ 채널 정보:'))
                self.stdout.write(f'      👥 구독자: {self.format_number(ch["subscriber_count"])}명')
                self.stdout.write(f'      🎥 영상 수: {self.format_number(ch["video_count"])}개')
                self.stdout.write(f'      👁️  총 조회수: {self.format_number(ch["view_count"])}회')
                if ch.get("channel_country"):
                    self.stdout.write(f'      🌍 국가: {ch["channel_country"]}')
                if ch.get("channel_custom_url"):
                    self.stdout.write(f'      🔗 채널: https://youtube.com/{ch["channel_custom_url"]}')

            # 통계
            self.stdout.write('')
            self.stdout.write(
                f'   👁️  조회수: {self.format_number(video["view_count"])}회'
            )
            self.stdout.write(
                f'   👍 좋아요: {self.format_number(video["like_count"])}개'
            )
            self.stdout.write(
                f'   💬 댓글: {self.format_number(video["comment_count"])}개'
            )

            # 참여율 계산
            if video["view_count"] > 0:
                engagement_rate = (
                    (video["like_count"] + video["comment_count"])
                    / video["view_count"] * 100
                )
                self.stdout.write(
                    f'   📊 참여율: {engagement_rate:.2f}%'
                )

            # URL
            self.stdout.write('')
            self.stdout.write(
                f'   🔗 https://www.youtube.com/watch?v={video["video_id"]}'
            )

            # 설명 (첫 2줄만)
            if video["description"]:
                desc_lines = video["description"].split('\n')[:2]
                desc = '\n      '.join(desc_lines)
                self.stdout.write(f'\n   📝 {desc}...')

            self.stdout.write('')
            self.stdout.write('=' * 100)

    def format_number(self, num: int) -> str:
        """숫자를 읽기 쉬운 형식으로 변환"""
        if num >= 100000000:  # 1억 이상
            return f'{num / 100000000:.1f}억'
        elif num >= 10000:  # 1만 이상
            return f'{num / 10000:.1f}만'
        else:
            return f'{num:,}'

    def format_datetime(self, dt_str: str) -> str:
        """ISO 8601 형식의 날짜를 읽기 쉬운 형식으로 변환"""
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return dt_str

    def format_duration(self, duration: str) -> str:
        """ISO 8601 duration을 읽기 쉬운 형식으로 변환"""
        # PT1H2M10S -> 1시간 2분 10초
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
        if seconds:
            parts.append(f'{seconds}초')

        return ' '.join(parts) if parts else '0초'
