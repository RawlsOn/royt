# YouTube API Wrapper 테스트 커맨드 사용법

## 개요

YouTube Data API v3 래퍼 클래스의 기능을 테스트할 수 있는 Django management command입니다.

## 기본 사용법

```bash
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api
```

## 커맨드 옵션

### 1. 채널 지정

```bash
--channel-id CHANNEL_IDENTIFIER
```

테스트할 YouTube 채널을 지정합니다. **채널 ID 또는 채널 핸들(@username)** 모두 사용 가능합니다.

기본값은 `@juegagerman` 입니다.

**예시 (채널 ID):**
```bash
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api --channel-id UCYiGq8XF7YQD00x7wAd62Zg
```

**예시 (채널 핸들):**
```bash
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api --channel-id @juegagerman
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api --channel-id @mkbhd
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api --channel-id @youtube
```

### 2. 조회할 영상 개수 제한

```bash
--max-results MAX_RESULTS
```

조회할 영상의 최대 개수를 지정합니다. 기본값은 10, 최대값은 50입니다.

**예시:**
```bash
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api --max-results 20
```

### 3. 특정 테스트만 실행

#### 채널 정보만 조회
```bash
--test-channel
```

#### 영상 목록만 조회
```bash
--test-videos
```

#### 모든 테스트 실행 (기본값)
```bash
--test-all
```

### 4. JSON 형식 출력

```bash
--json
```

결과를 JSON 형식으로 출력합니다.

**예시:**
```bash
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api --json --channel-id UCYiGq8XF7YQD00x7wAd62Zg
```

## 사용 예시

### 1. 채널 정보만 조회

**채널 ID 사용:**
```bash
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api \
  --test-channel \
  --channel-id UCYiGq8XF7YQD00x7wAd62Zg
```

**채널 핸들 사용:**
```bash
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api \
  --test-channel \
  --channel-id @juegagerman
```

**출력 예시:**
```
====================================================================================================
YouTube API Wrapper 테스트
====================================================================================================

■ 채널 정보 조회 테스트
   채널 ID: UCYiGq8XF7YQD00x7wAd62Zg

   ✅ 채널: JuegaGerman

   📋 기본 정보
      - 채널 ID: UCYiGq8XF7YQD00x7wAd62Zg
      - URL: https://youtube.com/@juegagerman
      - 국가: CL
      - 생성일: 2013-05-19 00:09:13

   📊 통계
      - 구독자: 5430.0만명
      - 영상 수: 2,376개
      - 총 조회수: 176.3억회

   📝 채널 설명
      Lento pero seguro.
```

### 2. 영상 목록 조회

```bash
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api \
  --test-videos \
  --channel-id UCYiGq8XF7YQD00x7wAd62Zg \
  --max-results 10
```

**출력 예시:**
```
■ 영상 목록 조회 테스트
   채널 ID: UCYiGq8XF7YQD00x7wAd62Zg
   최대 개수: 10

🎬 [1] No debí haber bajado esto... Those Nights at Fredbears
      - 비디오 ID: HtJ4Uf6WOnA
      - 게시일: 2025-10-21 19:02:51
      - 길이: 33분 20초 (2000초)
      - URL: https://www.youtube.com/watch?v=HtJ4Uf6WOnA

...

✅ 총 10개의 영상 조회 완료
   - 쇼츠: 0개
   - 일반 영상: 10개
   - 평균 길이: 59분 55초
```

### 3. JSON 형식으로 출력

```bash
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api \
  --json \
  --channel-id UCYiGq8XF7YQD00x7wAd62Zg \
  --max-results 5
```

## 구현된 파일 위치

- **YouTube API Wrapper 클래스**: `tech/api-gateway/common/util/youtube_api_wrapper.py`
- **테스트 커맨드**: `tech/api-gateway/base/management/commands/test_youtube_api.py`

## API 클래스 직접 사용

Django 코드 내에서 직접 사용할 수도 있습니다:

```python
from common.util.youtube_api_wrapper import YouTubeAPIWrapper

# 초기화 (settings.YOUTUBE_API_KEY 자동 사용)
youtube = YouTubeAPIWrapper()

# 채널 정보 조회 (채널 ID 사용)
channel = youtube.get_channel_info('UCYiGq8XF7YQD00x7wAd62Zg')
print(f"채널명: {channel['channel_title']}")
print(f"구독자: {channel['subscriber_count']}")

# 채널 정보 조회 (채널 핸들 사용)
channel = youtube.get_channel_info('@juegagerman')
print(f"채널명: {channel['channel_title']}")
print(f"채널 ID: {channel['channel_id']}")

# 영상 목록 조회 (채널 ID 사용)
videos = youtube.list_channel_videos('UCYiGq8XF7YQD00x7wAd62Zg', max_results=20)
for video in videos:
    print(f"{video['title']}: {video['duration_seconds']}초")

# 영상 목록 조회 (채널 핸들 사용)
videos = youtube.list_channel_videos('@juegagerman', max_results=20)
for video in videos:
    print(f"{video['title']}: {video['duration_seconds']}초")
    if video['is_short']:
        print("  → 쇼츠 영상입니다!")
```

## 주요 기능

### YouTubeAPIWrapper 클래스 메서드

1. **`get_channel_info(channel_identifier)`**
   - 채널의 기본 정보, 통계, 업로드 플레이리스트 ID 등을 조회
   - **파라미터**: 채널 ID 또는 채널 핸들 (@username)
   - 반환: 채널 정보 딕셔너리 또는 None

2. **`list_channel_videos(channel_identifier, max_results=50)`**
   - 채널의 영상 목록 조회
   - **파라미터**: 채널 ID 또는 채널 핸들 (@username)
   - 자동으로 영상 길이를 batch 조회하여 쇼츠 여부 판단 (`is_short` 필드 제공)
   - 반환: 영상 정보 딕셔너리 리스트

3. **`_parse_duration(iso_duration)`**
   - ISO 8601 형식의 duration을 초 단위로 변환
   - 예: "PT1M30S" → 90초

## 에러 처리

YouTube API 호출 시 다음과 같은 에러를 처리합니다:

- **401 Unauthorized**: API 키 인증 오류
- **403 Forbidden**: 할당량 초과 또는 접근 제한
- **404 Not Found**: 존재하지 않는 채널/영상 ID
- **Timeout**: 네트워크 타임아웃 (10초)
- **ConnectionError**: 네트워크 연결 오류

## 환경 변수 설정

`.env` 파일에 YouTube API 키가 설정되어 있어야 합니다:

```
YOUTUBE_API_KEY=your_youtube_api_key_here
```

## 참고사항

- YouTube Data API v3의 일일 할당량은 10,000 units입니다
- 영상 duration 조회는 최대 50개씩 batch로 처리됩니다
- 쇼츠는 duration이 60초 미만인 영상으로 정의되며, 각 영상 정보에 `is_short` 필드로 표시됩니다
- Pagination을 지원하여 많은 양의 영상도 조회 가능합니다
