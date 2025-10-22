"""
YouTube API get_video_info
"""
import json
from django.core.management.base import BaseCommand
from youtube.youtube_api_wrapper import YouTubeAPIWrapper

import pprint
pp = pprint.PrettyPrinter(indent=2)  # pp.pprint()

class Command(BaseCommand):
    help = 'YouTube API - get_video_info: 비디오 ID로 영상 상세 정보 조회'

    def add_arguments(self, parser):
        parser.add_argument(
            'video_id',
            type=str,
            help='YouTube 비디오 ID (예: dQw4w9WgXcQ)'
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
        video_id = options['video_id']
        save_to_db = not options['no_db']
        verbose = options['verbose']

        youtube_api = YouTubeAPIWrapper(save_to_db=save_to_db, verbose=verbose)

        print(f"\n{'='*80}")
        print(f"🎬 비디오 정보 조회: {video_id}")
        print(f"{'='*80}\n")

        video_info = youtube_api.get_video_info(video_id)

        if video_info:
            if verbose:
                print("\n" + "="*80)
                print("📋 파싱된 비디오 정보")
                print("="*80)
                pp.pprint(video_info)
                print("="*80 + "\n")

            # 주요 정보 요약 출력
            print("\n" + "="*80)
            print("📊 비디오 정보 요약")
            print("="*80)
            print(f"제목: {video_info['title']}")
            print(f"채널: {video_info['channel_title']} ({video_info['channel_id']})")
            print(f"게시일: {video_info['published_at']}")
            print(f"재생시간: {video_info['duration']} ({video_info['duration_seconds']}초)")
            print(f"Shorts 여부: {'예' if video_info['is_short'] else '아니오'}")
            print(f"조회수: {video_info['view_count']:,}")
            print(f"좋아요: {video_info['like_count']:,}")
            print(f"댓글: {video_info['comment_count']:,}")
            print(f"카테고리 ID: {video_info['category_id']}")
            if video_info['tags']:
                print(f"태그: {', '.join(video_info['tags'][:5])}" + (" ..." if len(video_info['tags']) > 5 else ""))
            print(f"썸네일: {video_info['thumbnail_url']}")
            print("="*80 + "\n")
        else:
            print("\n❌ 비디오 정보를 가져오지 못했습니다.\n")
