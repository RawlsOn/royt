"""
YouTube API get_video_transcript
"""
import json
from django.core.management.base import BaseCommand
from youtube.youtube_api_wrapper import YouTubeAPIWrapper

import pprint
pp = pprint.PrettyPrinter(indent=2)  # pp.pprint()

class Command(BaseCommand):
    help = 'YouTube API - get_video_transcript: 비디오 자막 조회 및 DB 저장'

    def add_arguments(self, parser):
        parser.add_argument(
            'video_id',
            type=str,
            help='YouTube 비디오 ID (예: dQw4w9WgXcQ)'
        )
        parser.add_argument(
            '--languages',
            type=str,
            default='ko,en',
            help='우선순위 언어 (쉼표로 구분, 기본값: ko,en)'
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
        languages = options['languages'].split(',')
        save_to_db = not options['no_db']
        verbose = options['verbose']

        youtube_api = YouTubeAPIWrapper(save_to_db=save_to_db, verbose=verbose)

        print(f"\n{'='*80}")
        print(f"📝 비디오 자막 조회: {video_id}")
        print(f"{'='*80}")
        print(f"우선순위 언어: {', '.join(languages)}")
        print(f"DB 저장: {'예' if save_to_db else '아니오'}")
        print(f"{'='*80}\n")

        transcript_info = youtube_api.get_video_transcript(
            video_id=video_id,
            languages=languages
        )

        if transcript_info:
            print("\n" + "="*80)
            print("📋 자막 정보 요약")
            print("="*80)
            print(f"비디오 ID: {transcript_info['video_id']}")
            print(f"언어: {transcript_info['language']}")
            print(f"전체 길이: {len(transcript_info['transcript'])}자")
            print(f"\n첫 500자:")
            print("-" * 80)
            print(transcript_info['transcript'][:500])
            if len(transcript_info['transcript']) > 500:
                print("...")
            print("-" * 80)
            print("="*80 + "\n")

            # verbose 모드에서 세그먼트 정보 출력
            if verbose and 'segments' in transcript_info:
                print("\n" + "="*80)
                print("📊 세그먼트 정보 (첫 5개)")
                print("="*80)
                for i, segment in enumerate(transcript_info['segments'], 1):
                    print(f"{i}. [{segment['start']:.2f}s] {segment['text']}")
                print("="*80 + "\n")

            if verbose:
                print("\n" + "="*80)
                print("📋 전체 자막 정보")
                print("="*80)
                pp.pprint(transcript_info)
                print("="*80 + "\n")
        else:
            print("\n❌ 자막을 가져오지 못했습니다.\n")
