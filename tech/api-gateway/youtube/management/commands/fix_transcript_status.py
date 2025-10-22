"""
자막이 있는 영상의 transcript_status를 'success'로 업데이트하는 임시 커맨드
"""
from django.core.management.base import BaseCommand
from youtube.models import YouTubeVideo


class Command(BaseCommand):
    help = '자막이 있는 영상의 transcript_status를 success로 업데이트'

    def handle(self, *args, **options):
        print(f"\n{'='*80}")
        print(f"📝 자막 상태 업데이트")
        print(f"{'='*80}\n")

        # 자막은 있지만 status가 없는 영상 찾기
        videos_with_transcript = YouTubeVideo.objects.filter(
            transcript__isnull=False
        ).exclude(
            transcript=''
        ).filter(
            transcript_status=''
        )

        total_count = videos_with_transcript.count()

        if total_count == 0:
            print("✅ 업데이트할 영상이 없습니다.\n")
            return

        print(f"📊 총 {total_count}개 영상을 업데이트합니다.\n")

        # 업데이트
        updated_count = videos_with_transcript.update(transcript_status='success')

        print(f"{'='*80}")
        print(f"✅ 업데이트 완료")
        print(f"{'='*80}")
        print(f"업데이트된 영상: {updated_count}개")
        print(f"{'='*80}\n")
