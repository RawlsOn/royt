"""
YouTube API get_video_categories
"""
import json
from django.core.management.base import BaseCommand
from youtube.youtube_api_wrapper import YouTubeAPIWrapper

import pprint
pp = pprint.PrettyPrinter(indent=2)  # pp.pprint()

class Command(BaseCommand):
    help = 'YouTube API - get_video_categories: 비디오 카테고리 목록 조회'

    def add_arguments(self, parser):
        parser.add_argument(
            '--region',
            type=str,
            default=None,
            help='특정 지역 코드만 조회 (예: KR, US). 지정하지 않으면 KR, US 자동 수집'
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
        save_to_db = not options['no_db']
        verbose = options['verbose']

        # region 파라미터가 없으면 KR, US 자동 수집
        if region_code:
            regions = [region_code]
        else:
            regions = ['KR', 'US']

        youtube_api = YouTubeAPIWrapper(save_to_db=save_to_db, verbose=verbose)

        print(f"\n{'='*80}")
        print(f"📂 비디오 카테고리 조회")
        print(f"{'='*80}")
        print(f"지역 코드: {', '.join(regions)}")
        print(f"DB 저장: {'예' if save_to_db else '아니오'}")
        print(f"{'='*80}\n")

        all_categories = []
        stats = {
            'total': 0,
            'new': 0,
            'updated': 0
        }

        for region in regions:
            print(f"\n{'='*80}")
            print(f"🌍 지역: {region}")
            print(f"{'='*80}\n")

            categories = youtube_api.get_video_categories(region_code=region)

            if categories:
                if verbose:
                    print("\n" + "="*80)
                    print("📋 파싱된 카테고리 정보 (전체)")
                    print("="*80)
                    pp.pprint(categories)
                    print("="*80 + "\n")

                # 카테고리 목록 테이블 형식 출력
                print("\n" + "="*80)
                print(f"📊 [{region}] 카테고리 목록 (총 {len(categories)}개)")
                print("="*80)
                print(f"{'ID':<10} {'카테고리명':<30} {'할당가능':<10}")
                print("-"*80)

                for category in categories:
                    assignable_str = "✅" if category['assignable'] else "❌"
                    print(f"{category['category_id']:<10} {category['category_title']:<30} {assignable_str:<10}")

                print("="*80 + "\n")

                all_categories.extend(categories)
                stats['total'] += len(categories)

                # DB 저장 시 신규/업데이트 통계 (간단히 표시)
                if save_to_db:
                    from youtube.models import YouTubeVideoCategory
                    new_count = 0
                    updated_count = 0
                    for cat in categories:
                        exists = YouTubeVideoCategory.objects.filter(
                            category_id=cat['category_id'],
                            region_code=cat['region_code']
                        ).exists()
                        if exists:
                            updated_count += 1
                        else:
                            new_count += 1

                    stats['new'] += new_count
                    stats['updated'] += updated_count

                    print(f"💾 DB 저장 결과: 신규 {new_count}개, 업데이트 {updated_count}개\n")

            else:
                print(f"\n❌ [{region}] 카테고리를 가져오지 못했습니다.\n")

        # 전체 요약
        if len(regions) > 1 and all_categories:
            print("\n" + "="*80)
            print("📈 전체 수집 요약")
            print("="*80)
            print(f"수집 지역: {', '.join(regions)}")
            print(f"총 카테고리 수: {stats['total']}개")
            if save_to_db:
                print(f"신규 생성: {stats['new']}개")
                print(f"업데이트: {stats['updated']}개")
            print("="*80 + "\n")
