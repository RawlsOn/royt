# YouTube API 테스트 커맨드 사용법

YouTube API 래퍼 클래스의 기능을 테스트하기 위한 Django 관리 커맨드 문서입니다.

---

## 공통 옵션

모든 커맨드는 다음 옵션을 지원합니다:
- `--verbose`: 상세한 로그 및 API 원본 응답 출력 (기본값: 간단한 요약만 출력)
- `--no-db`: DB에 저장하지 않음 (기본값: DB에 저장)

---

## 채널 정보 조회
```bash
# 채널 ID로 조회
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_channel_info UC_x5XG1OV2P6uZZ5FSM9Ttw

# 채널 핸들로 조회
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_channel_info @떠들썩

# 상세 로그와 함께 조회
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_channel_info @떠들썩 --verbose

# DB에 저장하지 않고 조회
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_channel_info @떠들썩 --no-db
```

## 채널 영상 목록 조회
```bash
# 채널 ID로 조회
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_list_channel_videos UCPF2WvEWPP-1utUwwsdbeCw

# 채널 핸들로 조회
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_list_channel_videos @떠들썩

# 상세 로그와 함께 조회
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_list_channel_videos @떠들썩 --verbose
```

## 최근 N개월 영상만 저장
```bash
# 최근 3개월 영상만 저장 (기본값)
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_save_recent_channel_videos @떠들썩

# 최근 6개월 영상만 저장
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_save_recent_channel_videos @떠들썩 --months 6

# 최대 100개까지만 조회하고 필터링
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_save_recent_channel_videos @떠들썩 --max-results 100

# 상세 로그와 함께 실행
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_save_recent_channel_videos @떠들썩 --verbose

# DB에 저장하지 않고 필터링만 테스트
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_save_recent_channel_videos @떠들썩 --no-db
```

**기능:**
- `list_channel_videos`로 채널의 영상 목록을 가져온 후, 최근 N개월 이내의 영상만 필터링
- 오래된 영상이 나오면 조회를 중단하여 API 할당량 절약
- 필터링된 영상 수와 전체 조회 영상 수를 함께 출력

**옵션:**
- `--months N`: 최근 N개월까지 저장 (기본값: 3개월)
- `--max-results N`: 최대 조회 개수 (기본값: 200)

## DB에서 오래된 영상 삭제
```bash
# 모든 채널의 3개월 이전 영상 삭제 (확인 절차 있음)
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_delete_old_channel_videos

# 특정 채널의 3개월 이전 영상 삭제
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_delete_old_channel_videos --channel @떠들썩 --confirm

# 특정 채널의 6개월 이전 영상 삭제
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_delete_old_channel_videos --channel @떠들썩 --months 6 --confirm

# 확인 없이 바로 삭제 (주의!)
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_delete_old_channel_videos --channel @떠들썩 --confirm

# 상세 로그와 함께 삭제
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_delete_old_channel_videos --channel @떠들썩 --verbose
```

**기능:**
- DB에서 N개월 이상 된 영상을 영구 삭제
- YouTube API를 사용하지 않으므로 할당량 소비 없음
- 특정 채널만 지정하거나 모든 채널 대상 가능
- 기본적으로 삭제 전 확인 절차 제공

**옵션:**
- `--channel @채널명`: 특정 채널만 삭제 (생략하면 모든 채널)
- `--months N`: N개월 이전 영상 삭제 (기본값: 3개월)
- `--confirm`: 확인 절차 없이 바로 삭제 (주의!)
- `--verbose`: 삭제될 영상 목록 미리보기

**⚠️ 주의사항:**
- 이 작업은 되돌릴 수 없습니다!
- `--confirm` 옵션이 없으면 'yes' 입력을 통한 확인 절차가 있습니다
- 영상의 게시일(`published_at`)을 기준으로 삭제됩니다

## 비디오 상세 정보 조회
```bash
# 비디오 ID로 조회
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_video_info 6JYx7wGO5qQ

# 상세 로그와 함께 조회
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_video_info 6JYx7wGO5qQ --verbose
```

**조회되는 정보:**
- 비디오 ID, 제목, 설명
- 채널 ID, 채널 제목
- 게시일, 썸네일 URL
- 재생시간 (ISO 8601 형식 및 초 단위)
- Shorts 여부 (60초 미만)
- 조회수, 좋아요 수, 댓글 수
- 태그, 카테고리 ID

## 비디오 자막 조회
```bash
# 비디오 자막 조회 (기본: 한국어 우선, 없으면 영어)
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_video_transcript 6JYx7wGO5qQ
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_video_transcript bUY3wNjcVMk

# 특정 언어 우선순위 지정
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_video_transcript 6JYx7wGO5qQ --languages en,ko

# 영어만 조회
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_video_transcript 6JYx7wGO5qQ --languages en

# DB에 저장하지 않고 조회
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_video_transcript 6JYx7wGO5qQ --no-db

# 상세 로그와 함께 조회 (세그먼트 정보 포함)
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_video_transcript 6JYx7wGO5qQ --verbose
```

**기능:**
- `youtube-transcript-api` 라이브러리 사용 (YouTube Data API 할당량 소비 없음)
- **수동 자막과 자동 생성 자막 모두 지원** (라이브러리가 자동으로 처리)
- 우선순위 언어 순서대로 자막 검색
- 전체 자막을 하나의 텍스트로 결합하여 DB에 저장

**옵션:**
- `--languages ko,en`: 쉼표로 구분된 언어 코드 우선순위 (기본값: ko)
- `--no-db`: DB에 저장하지 않음
- `--verbose`: 세그먼트 정보 및 타임스탬프 출력

**조회되는 정보:**
- 비디오 ID
- 자막 전체 텍스트
- 사용된 언어 코드
- 세그먼트 정보 (verbose 모드)

**⚠️ 참고사항:**
- 자막이 비활성화된 영상은 조회 불가
- 비공개 또는 삭제된 영상은 조회 불가
- DB에 저장하려면 해당 비디오가 먼저 DB에 있어야 함 (`get_video_info`로 먼저 저장)

## 채널 영상 자막 일괄 저장
```bash
# 채널 핸들로 모든 영상 자막 저장
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_save_all_channel_video_transcripts @떠들썩

# 채널 ID로 모든 영상 자막 저장
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_save_all_channel_video_transcripts UC_x5XG1OV2P6uZZ5FSM9Ttw

# 특정 언어로 저장
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_save_all_channel_video_transcripts @떠들썩 --languages ko

# 상세 로그와 함께 저장
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_save_all_channel_video_transcripts @떠들썩 --verbose
```

**기능:**
- 채널의 DB에 저장된 모든 영상의 자막을 일괄 저장
- 이미 시도한 영상은 자동으로 건너뛰기 (성공/실패 모두)
- 자막 조회 결과를 DB에 저장 (성공, 자막 없음, 비활성화 등)
- 진행 상황을 실시간으로 출력 (예: [1/23])
- 각 요청 후 5~10초 랜덤 대기 (IP 블락 방지)
- YouTube IP 블락 감지 시 자동 중단
- 최종 통계 출력 (성공/실패/건너뛰기)

**옵션:**
- `--languages ko,en`: 쉼표로 구분된 언어 코드 우선순위 (기본값: ko)
- `--verbose`: 각 영상별 상세한 로그 출력

**자막 조회 상태:**
- `success`: 자막을 성공적으로 가져옴
- `no_transcript`: 요청한 언어의 자막이 없음
- `disabled`: 자막이 비활성화됨
- `unavailable`: 비디오를 사용할 수 없음
- `error`: 기타 오류

**⚠️ 주의사항:**
- 먼저 `get_channel_info`로 채널 정보를 저장해야 함
- 먼저 `list_channel_videos`로 영상 목록을 저장해야 함
- 한 번 시도한 영상은 다시 시도하지 않음 (실패해도)
- YouTube API 할당량을 소비하지 않음 (youtube-transcript-api 사용)


## yt-dlp
docker exec royt-royt-api-gateway-1 yt-dlp --write-auto-sub --write-subs --sub-lang ko --sub-format vtt --skip-download "https://www.youtube.com/watch?v=6JYx7wGO5qQ"
