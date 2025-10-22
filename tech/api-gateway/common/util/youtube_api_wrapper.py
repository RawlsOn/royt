"""
YouTube Data API v3 Wrapper
채널 정보 조회 및 영상 목록 조회 기능 제공
"""
import re
import requests
from typing import List, Dict, Optional
from django.conf import settings


class YouTubeAPIWrapper:
    """YouTube Data API v3 래퍼 클래스"""

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: Optional[str] = None):
        """
        YouTube API 래퍼 초기화

        Args:
            api_key: YouTube Data API v3 키 (None이면 settings.YOUTUBE_API_KEY 사용)
        """
        self.api_key = api_key or getattr(settings, 'YOUTUBE_API_KEY', None)
        if not self.api_key:
            raise ValueError("YouTube API 키가 설정되지 않았습니다. settings.YOUTUBE_API_KEY를 확인하세요.")

    def get_channel_info(self, channel_identifier: str) -> Optional[Dict]:
        """
        채널 정보 조회

        Args:
            channel_identifier: 유튜브 채널 ID 또는 핸들 (@username 형태)

        Returns:
            채널 정보 딕셔너리 또는 None (실패 시)
            {
                'channel_id': str,
                'channel_title': str,
                'channel_description': str,
                'channel_custom_url': str,
                'channel_published_at': str,
                'channel_thumbnail': str,
                'channel_country': str,
                'subscriber_count': int,
                'video_count': int,
                'view_count': int,
                'channel_keywords': str,
                'uploads_playlist_id': str,  # 업로드 영상 플레이리스트 ID
            }
        """
        url = f"{self.BASE_URL}/channels"

        # 채널 핸들(@username)인지 채널 ID인지 구분
        if channel_identifier.startswith('@'):
            # forHandle 파라미터 사용
            params = {
                "part": "snippet,statistics,contentDetails",
                "forHandle": channel_identifier[1:],  # @ 제거
                "key": self.api_key
            }
        else:
            # id 파라미터 사용
            params = {
                "part": "snippet,statistics,contentDetails",
                "id": channel_identifier,
                "key": self.api_key
            }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            if not items:
                print(f"채널을 찾을 수 없습니다: {channel_identifier}")
                return None

            item = items[0]
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})
            content_details = item.get("contentDetails", {})
            related_playlists = content_details.get("relatedPlaylists", {})

            channel_info = {
                "channel_id": item.get("id"),
                "channel_title": snippet.get("title", ""),
                "channel_description": snippet.get("description", ""),
                "channel_custom_url": snippet.get("customUrl", ""),
                "channel_published_at": snippet.get("publishedAt", ""),
                "channel_thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "channel_country": snippet.get("country", ""),
                "subscriber_count": int(statistics.get("subscriberCount", 0)),
                "video_count": int(statistics.get("videoCount", 0)),
                "view_count": int(statistics.get("viewCount", 0)),
                "channel_keywords": snippet.get("keywords", ""),
                "uploads_playlist_id": related_playlists.get("uploads", ""),
            }

            return channel_info

        except requests.exceptions.HTTPError as e:
            self._handle_http_error(e, response)
            return None
        except requests.exceptions.RequestException as e:
            print(f"YouTube API 요청 실패: {e}")
            return None

    def list_channel_videos(
        self,
        channel_identifier: str,
        max_results: int = 50
    ) -> List[Dict]:
        """
        채널의 업로드 영상 목록 조회

        Args:
            channel_identifier: 유튜브 채널 ID 또는 핸들 (@username 형태)
            max_results: 조회할 최대 영상 개수 (기본값: 50)

        Returns:
            영상 정보 리스트
            [
                {
                    'video_id': str,
                    'title': str,
                    'description': str,
                    'published_at': str,
                    'thumbnail_url': str,
                    'duration': str,  # ISO 8601 형식
                    'duration_seconds': int,  # 초 단위
                    'is_short': bool,  # 60초 미만 여부
                },
                ...
            ]
        """
        # 1. 채널 정보에서 uploads playlist ID 가져오기
        channel_info = self.get_channel_info(channel_identifier)
        if not channel_info:
            return []

        uploads_playlist_id = channel_info.get("uploads_playlist_id")
        if not uploads_playlist_id:
            print(f"업로드 플레이리스트를 찾을 수 없습니다: {channel_identifier}")
            return []

        # 2. 플레이리스트에서 영상 목록 가져오기
        videos = []
        next_page_token = None

        while len(videos) < max_results:
            url = f"{self.BASE_URL}/playlistItems"
            params = {
                "part": "snippet,contentDetails",
                "playlistId": uploads_playlist_id,
                "maxResults": min(50, max_results - len(videos)),  # 최대 50개씩
                "key": self.api_key
            }

            if next_page_token:
                params["pageToken"] = next_page_token

            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                items = data.get("items", [])
                if not items:
                    break

                # 비디오 ID 추출
                video_ids = [item["contentDetails"]["videoId"] for item in items]

                # 비디오 duration 정보 가져오기 (배치 처리)
                durations_map = self._get_video_durations(video_ids)

                # 영상 정보 파싱
                for item in items:
                    snippet = item.get("snippet", {})
                    content_details = item.get("contentDetails", {})
                    video_id = content_details.get("videoId")

                    # duration 정보 추가
                    duration = durations_map.get(video_id, "")
                    duration_seconds = self._parse_duration(duration)
                    is_short = duration_seconds > 0 and duration_seconds < 60

                    video_info = {
                        "video_id": video_id,
                        "title": snippet.get("title", ""),
                        "description": snippet.get("description", ""),
                        "published_at": snippet.get("publishedAt", ""),
                        "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                        "duration": duration,
                        "duration_seconds": duration_seconds,
                        "is_short": is_short,
                    }

                    videos.append(video_info)

                    # max_results에 도달하면 중단
                    if len(videos) >= max_results:
                        break

                # 다음 페이지 확인
                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break

            except requests.exceptions.HTTPError as e:
                self._handle_http_error(e, response)
                break
            except requests.exceptions.RequestException as e:
                print(f"YouTube API 요청 실패: {e}")
                break

        return videos[:max_results]

    def _get_video_durations(self, video_ids: List[str]) -> Dict[str, str]:
        """
        비디오 duration 정보 조회 (배치 처리)

        Args:
            video_ids: 비디오 ID 리스트 (최대 50개)

        Returns:
            {video_id: duration} 형태의 딕셔너리
            duration은 ISO 8601 형식 (예: PT1M30S)
        """
        if not video_ids:
            return {}

        # 최대 50개씩만 처리
        if len(video_ids) > 50:
            print(f"경고: 한 번에 최대 50개의 비디오만 처리 가능합니다. (요청: {len(video_ids)}개)")
            video_ids = video_ids[:50]

        url = f"{self.BASE_URL}/videos"
        params = {
            "part": "contentDetails",
            "id": ",".join(video_ids),
            "key": self.api_key
        }

        durations_map = {}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                video_id = item.get("id")
                duration = item.get("contentDetails", {}).get("duration", "")
                durations_map[video_id] = duration

        except requests.exceptions.HTTPError as e:
            self._handle_http_error(e, response)
        except requests.exceptions.RequestException as e:
            print(f"YouTube API 요청 실패: {e}")

        return durations_map

    def _parse_duration(self, iso_duration: str) -> int:
        """
        ISO 8601 duration을 초 단위로 변환

        Args:
            iso_duration: ISO 8601 형식의 duration (예: PT1M30S, PT54S)

        Returns:
            초 단위 duration
        """
        if not iso_duration or not iso_duration.startswith("PT"):
            return 0

        # PT 제거
        duration_str = iso_duration[2:]

        hours = 0
        minutes = 0
        seconds = 0

        # 시간 파싱 (예: 1H)
        hour_match = re.search(r'(\d+)H', duration_str)
        if hour_match:
            hours = int(hour_match.group(1))

        # 분 파싱 (예: 2M)
        minute_match = re.search(r'(\d+)M', duration_str)
        if minute_match:
            minutes = int(minute_match.group(1))

        # 초 파싱 (예: 30S)
        second_match = re.search(r'(\d+)S', duration_str)
        if second_match:
            seconds = int(second_match.group(1))

        return hours * 3600 + minutes * 60 + seconds

    def _handle_http_error(self, error: requests.exceptions.HTTPError, response: requests.Response):
        """
        HTTP 에러 처리

        Args:
            error: HTTPError 예외
            response: requests Response 객체
        """
        status_code = response.status_code

        if status_code == 401:
            print("\n🔑 API 키 인증 실패 (401 Unauthorized):")
            print("  1. Google Cloud Console에서 YouTube Data API v3가 활성화되어 있는지 확인")
            print("  2. API 키가 올바른지 확인")
            print("  3. API 키에 YouTube Data API v3 접근 권한이 있는지 확인")
        elif status_code == 403:
            print("\n⚠️  접근 거부 (403 Forbidden):")
            print("  1. API 할당량 초과 여부 확인 (Google Cloud Console)")
            print("  2. 결제 계정이 연결되어 있는지 확인")
            print("  3. API 키의 제한사항 확인 (IP, Referrer 등)")
        elif status_code == 404:
            print("\n❌ 리소스를 찾을 수 없음 (404 Not Found):")
            print("  1. 채널 ID 또는 비디오 ID가 올바른지 확인")
            print("  2. 삭제되었거나 비공개 처리된 리소스일 수 있음")
        else:
            print(f"\n❌ HTTP 에러 발생: {status_code}")
            print(f"   메시지: {error}")

        # API 응답 메시지 출력
        try:
            error_data = response.json()
            if "error" in error_data:
                error_info = error_data["error"]
                print(f"\n   API 에러 메시지:")
                print(f"   - Code: {error_info.get('code')}")
                print(f"   - Message: {error_info.get('message')}")
                if "errors" in error_info:
                    for err in error_info["errors"]:
                        print(f"   - Reason: {err.get('reason')}")
        except (ValueError, KeyError, TypeError):
            pass
