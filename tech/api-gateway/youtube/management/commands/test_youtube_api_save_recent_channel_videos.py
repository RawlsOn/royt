"""
YouTube API save_recent_channel_videos
"""
import json
from django.core.management.base import BaseCommand
from youtube.youtube_api_wrapper import YouTubeAPIWrapper

import pprint
pp = pprint.PrettyPrinter(indent=2)  # pp.pprint()

class Command(BaseCommand):
    help = 'YouTube API - save_recent_channel_videos: 채널의 최근 N개월 영상만 DB에 저장'

    def add_arguments(self, parser):
        parser.add_argument(
            'channel_identifier',
            type=str,
            help='YouTube 채널 ID 또는 핸들 (예: @channelname 또는 UCxxxxx)'
        )
        parser.add_argument(
            '--months',
            type=int,
            default=3,
            help='최근 몇 개월까지 저장할지 (기본값: 3개월)'
        )
        parser.add_argument(
            '--max-results',
            type=int,
            default=200,
            help='조회할 최대 영상 개수 (기본값: 200)'
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
        channel_identifier = options['channel_identifier']
        months = options['months']
        max_results = options['max_results']
        save_to_db = not options['no_db']
        verbose = options['verbose']

        youtube_api = YouTubeAPIWrapper(save_to_db=save_to_db, verbose=verbose)

        print(f"\n{'='*80}")
        print(f"📅 채널의 최근 {months}개월 영상 저장")
        print(f"{'='*80}")
        print(f"채널: {channel_identifier}")
        print(f"최근 {months}개월 이내 영상만 필터링")
        print(f"최대 조회 개수: {max_results}개")
        print(f"DB 저장: {'예' if save_to_db else '아니오'}")
        print(f"{'='*80}\n")

        recent_videos = youtube_api.save_recent_channel_videos(
            channel_identifier=channel_identifier,
            months=months,
            max_results=max_results
        )

        if recent_videos:
            print(f"\n{'='*80}")
            print(f"📋 필터링된 최근 영상 목록 (총 {len(recent_videos)}개)")
            print(f"{'='*80}")

            for i, video in enumerate(recent_videos[:10], 1):
                print(f"{i}. {video['title'][:60]}")
                print(f"   게시일: {video['published_at']}")
                print(f"   비디오 ID: {video['video_id']}")
                print()

            if len(recent_videos) > 10:
                print(f"... 외 {len(recent_videos) - 10}개")

            print(f"{'='*80}\n")

            # verbose 모드일 때만 전체 데이터 출력
            if verbose:
                print(f"\n{'='*80}")
                print("📋 전체 필터링된 영상 정보")
                print(f"{'='*80}")
                pp.pprint(recent_videos)
                print(f"{'='*80}\n")
        else:
            print("\n❌ 필터링된 영상이 없습니다.\n")
