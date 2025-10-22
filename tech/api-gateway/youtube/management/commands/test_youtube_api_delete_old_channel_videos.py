"""
YouTube API delete_old_channel_videos
"""
import json
from django.core.management.base import BaseCommand
from youtube.youtube_api_wrapper import YouTubeAPIWrapper

import pprint
pp = pprint.PrettyPrinter(indent=2)  # pp.pprint()

class Command(BaseCommand):
    help = 'YouTube API - delete_old_channel_videos: DB에서 N개월 이상 된 영상 삭제'

    def add_arguments(self, parser):
        parser.add_argument(
            '--channel',
            type=str,
            default=None,
            help='YouTube 채널 ID 또는 핸들 (예: @channelname 또는 UCxxxxx). 생략하면 모든 채널에서 삭제'
        )
        parser.add_argument(
            '--months',
            type=int,
            default=3,
            help='몇 개월 이전 영상을 삭제할지 (기본값: 3개월)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='상세한 로그 출력'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='삭제 확인 없이 바로 실행 (주의: 이 옵션 없이는 실제 삭제 안 됨)'
        )

    def handle(self, *args, **options):
        channel_identifier = options['channel']
        months = options['months']
        verbose = options['verbose']
        confirm = options['confirm']

        print(f"\n{'='*80}")
        print(f"🗑️  DB에서 오래된 영상 삭제")
        print(f"{'='*80}")
        if channel_identifier:
            print(f"대상 채널: {channel_identifier}")
        else:
            print(f"대상 채널: 모든 채널")
        print(f"삭제 기준: {months}개월 이전 영상")
        print(f"{'='*80}\n")

        # 확인 절차
        if not confirm:
            print("⚠️  주의: 이 작업은 되돌릴 수 없습니다!")
            print(f"   {months}개월 이전에 업로드된 영상이 DB에서 영구 삭제됩니다.")
            if channel_identifier:
                print(f"   대상: {channel_identifier}")
            else:
                print(f"   대상: 모든 채널의 영상")
            print("\n계속하시겠습니까?")

            response = input("삭제를 진행하려면 'yes'를 입력하세요: ")

            if response.lower() != 'yes':
                print("\n❌ 삭제가 취소되었습니다.\n")
                return

        youtube_api = YouTubeAPIWrapper(save_to_db=False, verbose=verbose)

        result = youtube_api.delete_old_channel_videos(
            channel_identifier=channel_identifier,
            months=months
        )

        if verbose:
            print("\n" + "="*80)
            print("📋 삭제 결과 상세")
            print("="*80)
            pp.pprint(result)
            print("="*80 + "\n")

        # 최종 요약
        print(f"\n{'='*80}")
        print("✅ 삭제 작업 완료")
        print(f"{'='*80}")
        print(f"삭제된 영상 수: {result['deleted_count']}개")
        if result['channel_id']:
            print(f"채널 ID: {result['channel_id']}")
        if result['cutoff_date']:
            print(f"기준 날짜: {result['cutoff_date'].strftime('%Y-%m-%d %H:%M:%S')} 이전")
        print(f"{'='*80}\n")
