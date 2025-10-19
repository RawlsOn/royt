"""
YouTube API 연동 유틸리티
"""
import requests
from typing import List, Dict, Optional
from django.conf import settings


class YouTubeAPI:
    """YouTube Data API v3 래퍼"""

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_trending_videos(
        self,
        region_code: str = "KR",
        max_results: int = 10,
        video_category_id: Optional[str] = None,
        include_channel_info: bool = True
    ) -> List[Dict]:
        """
        인기 급상승 동영상 조회

        Args:
            region_code: 국가 코드 (KR, US, JP 등)
            max_results: 조회할 영상 개수 (1-50)
            video_category_id: 카테고리 ID (옵션)
            include_channel_info: 채널 상세 정보 포함 여부

        Returns:
            영상 정보 리스트
        """
        url = f"{self.BASE_URL}/videos"
        params = {
            "part": "snippet,statistics,contentDetails",
            "chart": "mostPopular",
            "regionCode": region_code,
            "maxResults": min(max_results, 50),
            "key": self.api_key
        }

        if video_category_id:
            params["videoCategoryId"] = video_category_id

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            videos = self._parse_videos(data.get("items", []))

            # 채널 정보 추가
            if include_channel_info and videos:
                channel_ids = list(set([v["channel_id"] for v in videos]))
                channels_info = self.get_channels_info(channel_ids)

                # 채널 정보를 영상에 매핑
                channel_dict = {ch["channel_id"]: ch for ch in channels_info}
                for video in videos:
                    channel_id = video["channel_id"]
                    if channel_id in channel_dict:
                        video["channel_info"] = channel_dict[channel_id]

            return videos

        except requests.exceptions.RequestException as e:
            print(f"YouTube API 요청 실패: {e}")
            if hasattr(response, 'status_code'):
                if response.status_code == 401:
                    print("\n🔑 API 키 문제:")
                    print("  1. Google Cloud Console에서 YouTube Data API v3가 활성화되어 있는지 확인")
                    print("  2. API 키가 올바른지 확인")
                    print("  3. API 키에 YouTube Data API v3 접근 권한이 있는지 확인")
                elif response.status_code == 403:
                    print("\n⚠️  API 할당량 초과 또는 권한 문제:")
                    print("  1. Google Cloud Console에서 할당량 확인")
                    print("  2. 결제 계정이 연결되어 있는지 확인")
            return []

    def _parse_videos(self, items: List[Dict]) -> List[Dict]:
        """
        YouTube API 응답 파싱

        Args:
            items: API 응답의 items 배열

        Returns:
            파싱된 영상 정보 리스트
        """
        videos = []

        for item in items:
            video_id = item.get("id")
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})
            content_details = item.get("contentDetails", {})

            video_info = {
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "channel_id": snippet.get("channelId", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "view_count": int(statistics.get("viewCount", 0)),
                "like_count": int(statistics.get("likeCount", 0)),
                "comment_count": int(statistics.get("commentCount", 0)),
                "duration": content_details.get("duration", ""),
                "category_id": snippet.get("categoryId", ""),
                "tags": snippet.get("tags", []),
            }

            videos.append(video_info)

        return videos

    def get_channels_info(self, channel_ids: List[str]) -> List[Dict]:
        """
        채널 정보 조회 (최대 50개씩 배치 처리)

        Args:
            channel_ids: 채널 ID 리스트

        Returns:
            채널 정보 리스트
        """
        if not channel_ids:
            return []

        url = f"{self.BASE_URL}/channels"
        all_channels = []

        # 50개씩 배치 처리 (YouTube API 제한)
        for i in range(0, len(channel_ids), 50):
            batch_ids = channel_ids[i:i + 50]
            params = {
                "part": "snippet,statistics,brandingSettings",
                "id": ",".join(batch_ids),
                "key": self.api_key
            }

            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                for item in data.get("items", []):
                    snippet = item.get("snippet", {})
                    statistics = item.get("statistics", {})
                    branding = item.get("brandingSettings", {}).get("channel", {})

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
                        "channel_keywords": branding.get("keywords", ""),
                    }

                    all_channels.append(channel_info)

            except requests.exceptions.RequestException as e:
                print(f"채널 정보 조회 실패: {e}")
                continue

        return all_channels

    def get_video_categories(self, region_code: str = "KR") -> List[Dict]:
        """
        비디오 카테고리 목록 조회

        Args:
            region_code: 국가 코드

        Returns:
            카테고리 정보 리스트
        """
        url = f"{self.BASE_URL}/videoCategories"
        params = {
            "part": "snippet",
            "regionCode": region_code,
            "key": self.api_key
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            categories = []
            for item in data.get("items", []):
                categories.append({
                    "id": item.get("id"),
                    "title": item.get("snippet", {}).get("title", ""),
                })

            return categories

        except requests.exceptions.RequestException as e:
            print(f"YouTube API 요청 실패: {e}")
            return []
