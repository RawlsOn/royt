"""
자막 정리 커맨드
원본 자막을 읽어서 정리된 자막으로 저장
"""
from django.core.management.base import BaseCommand
from youtube.models import YouTubeVideo


class Command(BaseCommand):
    help = '자막 정리 (맞춤법, 띄어쓰기, 문장 부호 수정)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--video-id',
            type=str,
            help='특정 비디오 ID만 처리'
        )
        parser.add_argument(
            '--max-videos',
            type=int,
            default=1,
            help='처리할 최대 영상 개수 (기본값: 1)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='상세한 로그 출력'
        )

    def handle(self, *args, **options):
        video_id = options.get('video_id')
        max_videos = options.get('max_videos')
        verbose = options.get('verbose')

        # 자막이 있는 영상 조회
        if video_id:
            videos = YouTubeVideo.objects.filter(
                video_id=video_id,
                transcript_status='success',
                transcript__isnull=False
            ).exclude(transcript='')
        else:
            videos = YouTubeVideo.objects.filter(
                transcript_status='success',
                transcript__isnull=False,
                refined_transcript_status=''  # 아직 정리하지 않은 것만
            ).exclude(transcript='')[:max_videos]

        total_count = videos.count()

        if total_count == 0:
            self.stdout.write(self.style.WARNING('처리할 영상이 없습니다.'))
            return

        self.stdout.write(f'\n{"="*80}')
        self.stdout.write(f'📝 자막 정리 시작')
        self.stdout.write(f'{"="*80}')
        self.stdout.write(f'총 {total_count}개 영상')
        self.stdout.write(f'{"="*80}\n')

        for idx, video in enumerate(videos, 1):
            self.stdout.write(f'[{idx}/{total_count}] {video.title[:60]}...')
            self.stdout.write(f'  비디오 ID: {video.video_id}')
            self.stdout.write(f'  채널: {video.channel.channel_title}')
            self.stdout.write(f'  원본 자막 길이: {len(video.transcript)}자')

            if verbose:
                self.stdout.write(f'\n  원본 자막:')
                self.stdout.write(f'  {video.transcript}\n')

            # 여기서 실제로는 AI가 자막을 정리해야 함
            # 지금은 수동으로 정리된 자막을 입력받는 방식
            self.stdout.write(self.style.WARNING('\n  ⚠️  정리된 자막을 수동으로 입력해주세요.'))
            self.stdout.write('  (Enter를 두 번 연속 입력하면 입력 종료)\n')

            lines = []
            while True:
                line = input()
                if line == '' and len(lines) > 0 and lines[-1] == '':
                    lines.pop()  # 마지막 빈 줄 제거
                    break
                lines.append(line)

            refined_transcript = '\n'.join(lines).strip()

            if refined_transcript:
                # DB에 저장
                video.refined_transcript = refined_transcript
                video.refined_transcript_status = 'completed'
                video.save(update_fields=['refined_transcript', 'refined_transcript_status', 'updated_at'])

                self.stdout.write(self.style.SUCCESS(f'  ✅ 정리 완료 ({len(refined_transcript)}자)'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ 정리된 자막이 비어있습니다. 건너뜁니다.'))

            self.stdout.write('')

        self.stdout.write(f'{"="*80}')
        self.stdout.write(self.style.SUCCESS(f'📊 자막 정리 완료: {total_count}개'))
        self.stdout.write(f'{"="*80}\n')
