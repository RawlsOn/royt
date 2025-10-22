# YouTube API Wrapper 기술 정보

## 채널 영상 조회 메서드 비교

YouTube API wrapper는 채널의 영상을 조회하는 두 가지 메서드를 제공합니다. 각 메서드는 서로 다른 YouTube API를 사용하며, 기능과 비용이 다릅니다.

### `list_channel_videos` vs `search_channel_videos`

| 기능 | list_channel_videos | search_channel_videos |
|------|---------------------|----------------------|
| **사용 API** | playlistItems.list | search.list + videos.list |
| **정렬** | ❌ 불가능 (업로드 순서만) | ✅ 가능 (date, viewCount, rating, relevance, title) |
| **날짜 필터링** | ❌ 불가능 | ✅ 가능 (publishedAfter/Before) |
| **API 할당량 비용** | 낮음 (1 할당량/호출) | 높음 (100 할당량/호출) |
| **DB 캐싱** | ✅ uploads_playlist_id 캐싱 | ❌ 캐싱 없음 |
| **조회수 정보** | ❌ 기본 제공 안 됨 | ✅ 제공됨 |
| **Duration 정보** | ❌ 기본 제공 안 됨 | ✅ 제공됨 |

### 사용 예시

#### list_channel_videos
```python
from youtube.youtube_api_wrapper import YouTubeAPIWrapper

wrapper = YouTubeAPIWrapper()

# 채널의 최신 영상 50개 조회 (업로드 순서)
videos = wrapper.list_channel_videos(
    channel_identifier="@channelname",  # 또는 채널 ID
    max_results=50
)
```

**반환 데이터:**
```python
[
    {
        'video_id': str,
        'title': str,
        'description': str,
        'published_at': str,
        'thumbnail_url': str,
    },
    ...
]
```

#### search_channel_videos
```python
from youtube.youtube_api_wrapper import YouTubeAPIWrapper

wrapper = YouTubeAPIWrapper()

# 조회수 순으로 정렬하고 날짜 필터링
videos = wrapper.search_channel_videos(
    channel_identifier="@channelname",  # 또는 채널 ID
    max_results=50,
    order='viewCount',  # 정렬: date, viewCount, rating, relevance, title
    published_after='2024-07-22T00:00:00Z',  # RFC 3339 형식
    published_before='2025-01-22T00:00:00Z'
)
```

**반환 데이터:**
```python
[
    {
        'video_id': str,
        'title': str,
        'description': str,
        'published_at': str,
        'thumbnail_url': str,
        'duration': str,  # ISO 8601 형식 (예: PT1M30S)
        'duration_seconds': int,  # 초 단위
        'is_short': bool,  # 60초 미만 여부
        'view_count': int,  # 조회수
    },
    ...
]
```

### 선택 가이드

#### `list_channel_videos`를 사용해야 하는 경우
- 채널의 **최신 업로드 영상**을 순서대로 가져올 때
- API 할당량을 절약해야 할 때
- 단순히 영상 목록만 필요할 때
- 빠른 응답이 필요할 때

#### `search_channel_videos`를 사용해야 하는 경우
- **조회수, 평점 등으로 정렬**이 필요할 때
- **특정 기간의 영상만** 필터링해야 할 때
- 영상의 **duration 정보**가 필요할 때
- 영상의 **조회수 정보**가 필요할 때
- Shorts 여부를 판단해야 할 때

### API 할당량 고려사항

YouTube Data API v3는 일일 할당량 제한이 있습니다 (기본 10,000 units/day):

- **list_channel_videos**:
  - playlistItems.list: 1 unit
  - 50개 영상 조회 시: 약 1-2 units

- **search_channel_videos**:
  - search.list: 100 units
  - videos.list: 1 unit
  - 50개 영상 조회 시: 약 101 units (search 100 + videos 1)

따라서 정렬/필터링이 반드시 필요한 경우가 아니라면 `list_channel_videos`를 사용하는 것이 할당량 측면에서 유리합니다.

### 기술적 차이점

#### list_channel_videos 동작 방식
1. 채널의 `uploads_playlist_id` 조회 (DB 캐싱 지원)
2. `playlistItems.list` API로 플레이리스트 항목 조회
3. 업로드 순서대로 영상 반환

#### search_channel_videos 동작 방식
1. `channels.list` API로 채널 ID 확인
2. `search.list` API로 영상 검색 (정렬/필터링 적용)
3. `videos.list` API로 상세 정보 조회 (duration, view count 등)
4. 결합된 데이터 반환

### 참고사항

- 두 메서드 모두 `max_results` 파라미터로 최대 조회 개수를 제한할 수 있습니다
- 페이지네이션은 내부적으로 자동 처리됩니다 (YouTube API의 50개 제한 우회)
- `save_to_db=True`로 초기화하면 조회한 데이터가 자동으로 DB에 저장됩니다
- 모든 API 호출 결과는 콘솔에 상세히 출력됩니다 (디버깅 용도)
