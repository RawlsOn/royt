"""
YouTube API get_trending_videos
"""
import json
from django.core.management.base import BaseCommand
from youtube.youtube_api_wrapper import YouTubeAPIWrapper

import pprint
pp = pprint.PrettyPrinter(indent=2)  # pp.pprint()

class Command(BaseCommand):
    help = 'YouTube API - get_trending_videos: 인기 급상승 영상 조회'

    def add_arguments(self, parser):
        parser.add_argument(
            '--region',
            type=str,
            default='KR',
            help='국가 코드 (기본값: KR)'
        )
        parser.add_argument(
            '--category',
            type=str,
            default=None,
            help='카테고리 ID (예: 10=음악, 20=게임, 24=엔터테인먼트)'
        )
        parser.add_argument(
            '--max-results',
            type=int,
            default=10,
            help='조회할 최대 영상 개수 (기본값: 10, 최대: 200)'
        )
        parser.add_argument(
            '--no-db',
            action='store_true',
            help='DB에 저장하지 않음'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='상세한 로그 출력'
        )

    def handle(self, *args, **options):
        region_code = options['region']
        category_id = options['category']
        max_results = options['max_results']
        save_to_db = not options['no_db']
        verbose = options['verbose']

        youtube_api = YouTubeAPIWrapper(save_to_db=save_to_db, verbose=verbose)

        print(f"\n{'='*80}")
        print(f"📈 인기 급상승 영상 조회")
        print(f"{'='*80}")
        print(f"지역 코드: {region_code}")
        if category_id:
            print(f"카테고리 ID: {category_id}")
        print(f"최대 결과 수: {max_results}")
        print(f"DB 저장: {'예' if save_to_db else '아니오'}")
        print(f"{'='*80}\n")

        videos = youtube_api.get_trending_videos(
            region_code=region_code,
            category_id=category_id,
            max_results=max_results
        )

        if videos:
            if verbose:
                print("\n" + "="*80)
                print("📋 파싱된 영상 정보 (전체)")
                print("="*80)
                pp.pprint(videos)
                print("="*80 + "\n")

            # 영상 목록 요약 출력
            print("\n" + "="*80)
            print(f"📊 인기 급상승 영상 목록 (총 {len(videos)}개)")
            print("="*80)

            shorts_count = sum(1 for v in videos if v['is_short'])
            print(f"Shorts 영상: {shorts_count}개")
            print(f"일반 영상: {len(videos) - shorts_count}개")
            print("="*80)

            for idx, video in enumerate(videos, 1):
                print(f"\n[{idx}] {video['title']}")
                print(f"    채널: {video['channel_title']}")
                print(f"    조회수: {video['view_count']:,} | 좋아요: {video['like_count']:,} | 댓글: {video['comment_count']:,}")
                print(f"    재생시간: {video['duration']} ({video['duration_seconds']}초) | Shorts: {'✅' if video['is_short'] else '❌'}")
                print(f"    게시일: {video['published_at']}")
                print(f"    카테고리: {video['category_id']}")
                print(f"    비디오 ID: {video['video_id']}")

            print("\n" + "="*80 + "\n")

            # 통계 정보
            total_views = sum(v['view_count'] for v in videos)
            avg_views = total_views // len(videos) if videos else 0

            print("="*80)
            print("📈 통계 요약")
            print("="*80)
            print(f"총 조회수: {total_views:,}")
            print(f"평균 조회수: {avg_views:,}")
            print(f"최고 조회수: {max(v['view_count'] for v in videos):,}")
            print(f"최저 조회수: {min(v['view_count'] for v in videos):,}")
            print("="*80 + "\n")
        else:
            print("\n❌ 인기 급상승 영상을 가져오지 못했습니다.\n")
