"""
YouTube Data API v3 Wrapper
채널 정보 조회 및 영상 목록 조회 기능 제공
"""
import re
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone


class YouTubeAPIWrapper:
    """YouTube Data API v3 래퍼 클래스"""

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: Optional[str] = None, save_to_db: bool = True, verbose: bool = False):
        """
        YouTube API 래퍼 초기화

        Args:
            api_key: YouTube Data API v3 키 (None이면 settings.YOUTUBE_API_KEY 사용)
            save_to_db: API 호출 결과를 DB에 저장할지 여부 (기본값: True)
            verbose: 상세 로그 출력 여부 (기본값: False)
        """
        self.api_key = api_key or getattr(settings, 'YOUTUBE_API_KEY', None)
        if not self.api_key:
            raise ValueError("YouTube API 키가 설정되지 않았습니다. settings.YOUTUBE_API_KEY를 확인하세요.")
        self.save_to_db = save_to_db
        self.verbose = verbose
        self.api_call_count = 0  # API 호출 횟수 추적

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

            # API 호출 횟수 증가
            self.api_call_count += 1

            # 원본 API 응답 출력 (verbose 모드)
            if self.verbose:
                print("\n" + "="*80)
                print("📡 YouTube API 원본 응답 (JSON)")
                print("="*80)
                print(json.dumps(data, indent=2, ensure_ascii=False))
                print("="*80 + "\n")

            items = data.get("items", [])
            if not items:
                if self.verbose:
                    print(f"채널을 찾을 수 없습니다: {channel_identifier}")
                self._print_api_call_summary()
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

            # DB에 저장
            if self.save_to_db:
                self._save_channel_to_db(channel_info)

            # 간단한 요약 출력
            if not self.verbose:
                print(f"✅ 채널 정보 조회 완료: {channel_info['channel_title']} (구독자: {channel_info['subscriber_count']:,}명)")

            # API 호출 요약 출력
            self._print_api_call_summary()

            return channel_info

        except requests.exceptions.HTTPError as e:
            self.api_call_count += 1
            self._handle_http_error(e, response)
            self._print_api_call_summary()
            return None
        except requests.exceptions.RequestException as e:
            print(f"YouTube API 요청 실패: {e}")
            self._print_api_call_summary()
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

        # 1. DB에서 uploads_playlist_id 조회 시도
        uploads_playlist_id = None
        channel_info = None

        if self.save_to_db:
            try:
                from youtube.models import YouTubeChannel

                # 채널 핸들(@username)인지 채널 ID인지 구분
                if channel_identifier.startswith('@'):
                    # 핸들인 경우 custom_url로 조회
                    channel = YouTubeChannel.objects.filter(
                        channel_custom_url=channel_identifier
                    ).first()
                else:
                    # 채널 ID인 경우
                    channel = YouTubeChannel.objects.filter(
                        channel_id=channel_identifier
                    ).first()

                if channel and channel.uploads_playlist_id:
                    uploads_playlist_id = channel.uploads_playlist_id
                    if self.verbose:
                        print(f"  ✅ DB에서 uploads_playlist_id 캐시 사용: {uploads_playlist_id}")
            except Exception as e:
                if self.verbose:
                    print(f"  ⚠️  DB 조회 실패: {e}")

        # 2. DB에 없으면 API로 채널 정보 조회
        if not uploads_playlist_id:
            if self.verbose:
                print(f"  🔍 API로 채널 정보 조회 중...")
            channel_info = self.get_channel_info(channel_identifier)
            if not channel_info:
                return []

            uploads_playlist_id = channel_info.get("uploads_playlist_id")
            if not uploads_playlist_id:
                if self.verbose:
                    print(f"채널의 uploads_playlist_id를 찾을 수 없습니다: {channel_identifier}")
                return []

        # 3. 플레이리스트에서 영상 목록 가져오기
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

                # API 호출 횟수 증가
                self.api_call_count += 1

                # 원본 API 응답 출력 (verbose 모드)
                if self.verbose:
                    print("\n" + "="*80)
                    print("📡 YouTube API 원본 응답 (playlistItems)")
                    print("="*80)
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    print("="*80 + "\n")

                items = data.get("items", [])
                if not items:
                    break

                # 비디오 ID 추출
                video_ids = [item["contentDetails"]["videoId"] for item in items]

                # 영상 정보 파싱
                for item in items:
                    snippet = item.get("snippet", {})
                    content_details = item.get("contentDetails", {})
                    video_id = content_details.get("videoId")

                    video_info = {
                        "video_id": video_id,
                        "title": snippet.get("title", ""),
                        "description": snippet.get("description", ""),
                        "published_at": snippet.get("publishedAt", ""),
                        "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
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
                self.api_call_count += 1
                self._handle_http_error(e, response)
                break
            except requests.exceptions.RequestException as e:
                print(f"YouTube API 요청 실패: {e}")
                break

        # DB에 저장
        if self.save_to_db and videos:
            # channel_info가 없으면 channel_identifier로부터 생성
            if not channel_info:
                # DB에서 채널 정보 조회
                try:
                    from youtube.models import YouTubeChannel

                    if channel_identifier.startswith('@'):
                        channel = YouTubeChannel.objects.filter(
                            channel_custom_url=channel_identifier
                        ).first()
                    else:
                        channel = YouTubeChannel.objects.filter(
                            channel_id=channel_identifier
                        ).first()

                    if channel:
                        channel_info = {'channel_id': channel.channel_id}
                except Exception as e:
                    if self.verbose:
                        print(f"  ⚠️  채널 정보 조회 실패: {e}")

            if channel_info:
                self._save_videos_to_db(videos, channel_info)

        # 간단한 요약 출력
        if not self.verbose:
            print(f"✅ 채널 영상 목록 조회 완료: {len(videos[:max_results])}개")

        # API 호출 요약 출력
        self._print_api_call_summary()

        return videos[:max_results]

    def save_recent_channel_videos(
        self,
        channel_identifier: str,
        months: int = 3,
        max_results: int = 200
    ) -> List[Dict]:
        """
        채널의 최근 N개월 영상만 DB에 저장

        list_channel_videos를 사용하여 영상 목록을 가져온 후,
        최근 N개월 이내의 영상만 필터링하여 DB에 저장합니다.

        Args:
            channel_identifier: 유튜브 채널 ID 또는 핸들 (@username 형태)
            months: 최근 몇 개월까지 저장할지 (기본값: 3개월)
            max_results: 조회할 최대 영상 개수 (기본값: 200)

        Returns:
            저장된 영상 정보 리스트
        """
        # 현재 시각 기준 N개월 전 날짜 계산
        cutoff_date = datetime.now() - timedelta(days=months * 30)

        if self.verbose:
            print(f"\n{'='*80}")
            print(f"📅 최근 {months}개월 영상 저장 시작")
            print(f"   기준 날짜: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}\n")

        # list_channel_videos로 영상 목록 조회
        videos = self.list_channel_videos(channel_identifier, max_results=max_results)

        if not videos:
            if not self.verbose:
                print("❌ 조회된 영상이 없습니다.")
            return []

        # 최근 N개월 이내의 영상만 필터링
        recent_videos = []
        for video in videos:
            published_at_str = video.get('published_at', '')
            if not published_at_str:
                continue

            try:
                # ISO 8601 형식 파싱
                from django.utils.dateparse import parse_datetime
                published_at = parse_datetime(published_at_str)

                if published_at:
                    # timezone-aware라면 naive로 변환
                    if timezone.is_aware(published_at):
                        published_at = timezone.make_naive(published_at, timezone.utc)

                    # 최근 N개월 이내인지 체크
                    if published_at >= cutoff_date:
                        recent_videos.append(video)
                    else:
                        # 오래된 영상이 나오면 더 이상 체크하지 않음 (업로드 순서로 정렬되어 있으므로)
                        break
            except Exception as e:
                if self.verbose:
                    print(f"  ⚠️  날짜 파싱 실패: {video.get('video_id')} - {e}")
                continue

        # 필터링된 영상 정보 출력
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"📊 필터링 결과")
            print(f"{'='*80}")
            print(f"전체 조회 영상: {len(videos)}개")
            print(f"최근 {months}개월 영상: {len(recent_videos)}개")
            print(f"{'='*80}\n")

        # DB에 저장 (save_to_db가 True인 경우 이미 list_channel_videos에서 저장됨)
        # 하지만 필터링된 영상만 반환

        # 간단한 요약 출력
        if not self.verbose:
            print(f"✅ 최근 {months}개월 영상 {len(recent_videos)}개 필터링 완료 (전체 {len(videos)}개 중)")

        return recent_videos

    def delete_old_channel_videos(
        self,
        channel_identifier: Optional[str] = None,
        months: int = 3
    ) -> Dict:
        """
        DB에서 N개월 이상 된 영상 삭제

        Args:
            channel_identifier: 유튜브 채널 ID 또는 핸들 (None이면 모든 채널)
            months: 몇 개월 이전 영상을 삭제할지 (기본값: 3개월)

        Returns:
            삭제 결과 딕셔너리
            {
                'deleted_count': int,  # 삭제된 영상 수
                'channel_id': str,     # 채널 ID (특정 채널인 경우)
                'cutoff_date': datetime  # 기준 날짜
            }
        """
        try:
            from youtube.models import YouTubeChannel, YouTubeVideo

            # 현재 시각 기준 N개월 전 날짜 계산
            cutoff_date = datetime.now() - timedelta(days=months * 30)

            if self.verbose:
                print(f"\n{'='*80}")
                print(f"🗑️  {months}개월 이상 된 영상 삭제 시작")
                print(f"   기준 날짜: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*80}\n")

            # 채널 필터링
            videos_query = YouTubeVideo.objects.filter(published_at__lt=cutoff_date)

            channel_id = None
            if channel_identifier:
                # 채널 정보 조회
                if channel_identifier.startswith('@'):
                    # 핸들인 경우
                    channel = YouTubeChannel.objects.filter(
                        channel_custom_url=channel_identifier
                    ).first()
                else:
                    # 채널 ID인 경우
                    channel = YouTubeChannel.objects.filter(
                        channel_id=channel_identifier
                    ).first()

                if not channel:
                    if not self.verbose:
                        print(f"❌ 채널을 찾을 수 없습니다: {channel_identifier}")
                    return {
                        'deleted_count': 0,
                        'channel_id': None,
                        'cutoff_date': cutoff_date
                    }

                channel_id = channel.channel_id
                videos_query = videos_query.filter(channel=channel)

                if self.verbose:
                    print(f"  📌 특정 채널만 삭제: {channel.channel_title} ({channel_id})")

            # 삭제 전 카운트
            old_videos_count = videos_query.count()

            if old_videos_count == 0:
                if not self.verbose:
                    print(f"✅ 삭제할 오래된 영상이 없습니다.")
                return {
                    'deleted_count': 0,
                    'channel_id': channel_id,
                    'cutoff_date': cutoff_date
                }

            # verbose 모드일 때 삭제될 영상 목록 출력
            if self.verbose:
                print(f"\n{'='*80}")
                print(f"📋 삭제 대상 영상 목록 (총 {old_videos_count}개)")
                print(f"{'='*80}")
                for video in videos_query[:10]:
                    print(f"- {video.title[:60]}")
                    print(f"  게시일: {video.published_at.strftime('%Y-%m-%d') if video.published_at else 'N/A'}")
                    print(f"  비디오 ID: {video.video_id}")
                    print()

                if old_videos_count > 10:
                    print(f"... 외 {old_videos_count - 10}개")
                print(f"{'='*80}\n")

            # 삭제 실행
            deleted_count, _ = videos_query.delete()

            # 결과 출력
            if not self.verbose:
                if channel_identifier:
                    print(f"✅ {months}개월 이상 된 영상 {deleted_count}개 삭제 완료 (채널: {channel_identifier})")
                else:
                    print(f"✅ {months}개월 이상 된 영상 {deleted_count}개 삭제 완료 (모든 채널)")

            if self.verbose:
                print(f"\n{'='*80}")
                print(f"📊 삭제 완료")
                print(f"{'='*80}")
                print(f"삭제된 영상 수: {deleted_count}개")
                if channel_identifier:
                    print(f"대상 채널: {channel_identifier}")
                else:
                    print(f"대상 채널: 모든 채널")
                print(f"기준 날짜: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} 이전")
                print(f"{'='*80}\n")

            return {
                'deleted_count': deleted_count,
                'channel_id': channel_id,
                'cutoff_date': cutoff_date
            }

        except Exception as e:
            if self.verbose:
                print(f"❌ 영상 삭제 실패: {e}")
                import traceback
                traceback.print_exc()
            else:
                print(f"❌ 영상 삭제 실패: {e}")

            return {
                'deleted_count': 0,
                'channel_id': None,
                'cutoff_date': None
            }

    def search_channel_videos(
        self,
        channel_identifier: str,
        max_results: int = 50,
        order: str = 'viewCount',
        published_after: Optional[str] = None,
        published_before: Optional[str] = None
    ) -> List[Dict]:
        """
        채널 영상 검색 (정렬 및 날짜 필터링 지원)

        Args:
            channel_identifier: 유튜브 채널 ID 또는 핸들 (@username 형태)
            max_results: 조회할 최대 영상 개수 (기본값: 50)
            order: 정렬 순서 (date, viewCount, rating, relevance, title)
            published_after: 이 날짜 이후 업로드된 영상만 (RFC 3339 형식, 예: '2024-07-22T00:00:00Z')
            published_before: 이 날짜 이전 업로드된 영상만 (RFC 3339 형식)

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
                    'view_count': int,  # 조회수
                },
                ...
            ]
        """
        # 1. 채널 정보에서 채널 ID 가져오기 (핸들인 경우 ID로 변환)
        channel_info = self.get_channel_info(channel_identifier)
        if not channel_info:
            return []

        channel_id = channel_info.get("channel_id")
        if not channel_id:
            print(f"채널 ID를 찾을 수 없습니다: {channel_identifier}")
            return []

        # 2. search API로 영상 검색
        videos = []
        next_page_token = None

        while len(videos) < max_results:
            url = f"{self.BASE_URL}/search"
            params = {
                "part": "snippet",
                "channelId": channel_id,
                "type": "video",
                "order": order,
                "maxResults": min(50, max_results - len(videos)),  # 최대 50개씩
                "key": self.api_key
            }

            if published_after:
                params["publishedAfter"] = published_after
            if published_before:
                params["publishedBefore"] = published_before
            if next_page_token:
                params["pageToken"] = next_page_token

            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                # API 호출 횟수 증가
                self.api_call_count += 1

                # 원본 API 응답 출력 (verbose 모드)
                if self.verbose:
                    print("\n" + "="*80)
                    print("📡 YouTube API 원본 응답 (search)")
                    print("="*80)
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    print("="*80 + "\n")

                items = data.get("items", [])
                if not items:
                    break

                # 비디오 ID 추출
                video_ids = [item["id"]["videoId"] for item in items]

                # 비디오 상세 정보 가져오기 (duration, view count 등)
                videos_details = self._get_video_details(video_ids)

                # 영상 정보 파싱
                for item in items:
                    snippet = item.get("snippet", {})
                    video_id = item["id"]["videoId"]

                    # 상세 정보에서 duration과 통계 가져오기
                    details = videos_details.get(video_id, {})
                    duration = details.get("duration", "")
                    duration_seconds = self._parse_duration(duration)
                    is_short = duration_seconds > 0 and duration_seconds < 60
                    view_count = details.get("view_count", 0)

                    video_info = {
                        "video_id": video_id,
                        "title": snippet.get("title", ""),
                        "description": snippet.get("description", ""),
                        "published_at": snippet.get("publishedAt", ""),
                        "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                        "duration": duration,
                        "duration_seconds": duration_seconds,
                        "is_short": is_short,
                        "view_count": view_count,
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
                self.api_call_count += 1
                self._handle_http_error(e, response)
                break
            except requests.exceptions.RequestException as e:
                if self.verbose:
                    print(f"YouTube API 요청 실패: {e}")
                break

        # DB에 저장
        if self.save_to_db and videos:
            self._save_videos_to_db(videos, channel_info)

        # 간단한 요약 출력
        if not self.verbose:
            print(f"✅ 채널 영상 검색 완료: {len(videos[:max_results])}개 (정렬: {order})")

        # API 호출 요약 출력
        self._print_api_call_summary()

        return videos[:max_results]

    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """
        비디오 상세 정보 조회

        Args:
            video_id: 유튜브 비디오 ID

        Returns:
            비디오 정보 딕셔너리 또는 None (실패 시)
            {
                'video_id': str,
                'title': str,
                'description': str,
                'published_at': str,
                'thumbnail_url': str,
                'duration': str,  # ISO 8601 형식
                'duration_seconds': int,  # 초 단위
                'is_short': bool,  # 60초 미만 여부
                'view_count': int,
                'like_count': int,
                'comment_count': int,
                'channel_id': str,
                'channel_title': str,
                'tags': List[str],  # 태그 목록
                'category_id': str,  # 카테고리 ID
            }
        """
        url = f"{self.BASE_URL}/videos"
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": video_id,
            "key": self.api_key
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # API 호출 횟수 증가
            self.api_call_count += 1

            # 원본 API 응답 출력 (verbose 모드)
            if self.verbose:
                print("\n" + "="*80)
                print("📡 YouTube API 원본 응답 (videos - get_video_info)")
                print("="*80)
                print(json.dumps(data, indent=2, ensure_ascii=False))
                print("="*80 + "\n")

            items = data.get("items", [])
            if not items:
                if self.verbose:
                    print(f"비디오를 찾을 수 없습니다: {video_id}")
                self._print_api_call_summary()
                return None

            item = items[0]
            snippet = item.get("snippet", {})
            content_details = item.get("contentDetails", {})
            statistics = item.get("statistics", {})

            duration = content_details.get("duration", "")
            duration_seconds = self._parse_duration(duration)
            is_short = duration_seconds > 0 and duration_seconds < 60

            video_info = {
                "video_id": item.get("id"),
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "duration": duration,
                "duration_seconds": duration_seconds,
                "is_short": is_short,
                "view_count": int(statistics.get("viewCount", 0)),
                "like_count": int(statistics.get("likeCount", 0)),
                "comment_count": int(statistics.get("commentCount", 0)),
                "channel_id": snippet.get("channelId", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "tags": snippet.get("tags", []),
                "category_id": snippet.get("categoryId", ""),
            }

            # DB에 저장
            if self.save_to_db:
                self._save_single_video_to_db(video_info)

            # 간단한 요약 출력
            if not self.verbose:
                print(f"✅ 비디오 정보 조회 완료: {video_info['title'][:50]} (조회수: {video_info['view_count']:,})")

            # API 호출 요약 출력
            self._print_api_call_summary()

            return video_info

        except requests.exceptions.HTTPError as e:
            self.api_call_count += 1
            self._handle_http_error(e, response)
            self._print_api_call_summary()
            return None
        except requests.exceptions.RequestException as e:
            print(f"YouTube API 요청 실패: {e}")
            self._print_api_call_summary()
            return None

    def get_video_transcript(
        self,
        video_id: str,
        languages: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        비디오 자막 조회 (youtube-transcript-api 사용)

        Args:
            video_id: 유튜브 비디오 ID
            languages: 우선순위 언어 리스트 (기본값: ['ko', 'en'])

        Returns:
            자막 정보 딕셔너리 또는 None (실패 시)
            {
                'video_id': str,
                'transcript': str,  # 전체 자막 텍스트
                'language': str,    # 사용된 언어 코드
                'segments': List[Dict],  # 타임스탬프 정보 포함 (verbose 모드)
            }
        """
        if languages is None:
            languages = ['ko']
            # languages = ['ko', 'en']

        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            from youtube_transcript_api._errors import (
                TranscriptsDisabled,
                NoTranscriptFound,
                VideoUnavailable
            )

            if self.verbose:
                print(f"\n{'='*80}")
                print(f"📝 자막 조회 시작: {video_id}")
                print(f"   우선 언어: {', '.join(languages)}")
                print(f"{'='*80}\n")

            # 자막 가져오기
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # 우선순위 언어로 시도
            transcript = None
            used_language = None
            is_generated = False

            for lang in languages:
                try:
                    # 먼저 수동 자막 시도
                    transcript = transcript_list.find_manually_created_transcript([lang])
                    used_language = lang
                    is_generated = False
                    if self.verbose:
                        print(f"  ✅ {lang} 수동 자막 발견")
                    break
                except NoTranscriptFound:
                    if self.verbose:
                        print(f"  ⚠️  {lang} 수동 자막 없음, 자동 생성 자막 시도...")

                    # 수동 자막이 없으면 자동 생성 자막 시도
                    try:
                        transcript = transcript_list.find_generated_transcript([lang])
                        used_language = lang
                        is_generated = True
                        if self.verbose:
                            print(f"  ✅ {lang} 자동 생성 자막 발견")
                        break
                    except NoTranscriptFound:
                        if self.verbose:
                            print(f"  ⚠️  {lang} 자동 생성 자막도 없음, 다음 언어 시도...")
                        continue

            # 우선순위 언어가 없으면 사용 가능한 첫 번째 자막 사용
            if not transcript:
                try:
                    available_transcripts = list(transcript_list)
                    if available_transcripts:
                        transcript = available_transcripts[0]
                        used_language = transcript.language_code
                        if self.verbose:
                            print(f"  ℹ️  사용 가능한 자막 언어: {used_language}")
                except Exception:
                    pass

            if not transcript:
                if not self.verbose:
                    print(f"❌ 사용 가능한 자막이 없습니다: {video_id}")
                return None

            # 자막 데이터 가져오기
            segments = transcript.fetch()

            # 전체 텍스트 생성
            full_text = ' '.join([segment['text'] for segment in segments])

            if self.verbose:
                print(f"\n{'='*80}")
                print(f"📊 자막 정보")
                print(f"{'='*80}")
                print(f"언어: {used_language}")
                print(f"유형: {'자동 생성' if is_generated else '수동 작성'}")
                print(f"세그먼트 수: {len(segments)}개")
                print(f"전체 길이: {len(full_text)}자")
                print(f"첫 100자: {full_text[:100]}...")
                print(f"{'='*80}\n")

            transcript_info = {
                'video_id': video_id,
                'transcript': full_text,
                'language': used_language,
                'is_generated': is_generated,
            }

            # verbose 모드에서는 세그먼트 정보도 포함
            if self.verbose:
                transcript_info['segments'] = segments[:5]  # 첫 5개만

            # DB에 저장
            if self.save_to_db:
                self._save_transcript_to_db(video_id, full_text, used_language)

            # 간단한 요약 출력
            if not self.verbose:
                subtitle_type = "자동생성" if is_generated else "수동"
                print(f"✅ 자막 조회 완료: {video_id} ({subtitle_type}, 언어: {used_language}, {len(full_text)}자)")

            return transcript_info

        except TranscriptsDisabled:
            if not self.verbose:
                print(f"❌ 자막이 비활성화되어 있습니다: {video_id}")
            else:
                print(f"  ❌ 자막이 비활성화되어 있습니다")
            return None

        except VideoUnavailable:
            if not self.verbose:
                print(f"❌ 비디오를 사용할 수 없습니다: {video_id}")
            else:
                print(f"  ❌ 비디오를 사용할 수 없습니다")
            return None

        except Exception as e:
            error_msg = str(e)

            # 일반적인 오류 패턴 파악
            if "no element found" in error_msg.lower():
                if not self.verbose:
                    print(f"❌ 자막 조회 실패: {video_id}")
                    print(f"   원인: YouTube에서 빈 응답을 받았습니다. 가능한 원인:")
                    print(f"   - 비디오에 자막이 없음")
                    print(f"   - 비디오가 비공개/삭제됨")
                    print(f"   - 지역 제한이 걸려 있음")
                else:
                    print(f"❌ XML 파싱 오류: YouTube에서 유효하지 않은 응답을 받았습니다")
            else:
                if not self.verbose:
                    print(f"❌ 자막 조회 실패: {video_id} - {e}")
                else:
                    print(f"❌ 자막 조회 실패: {e}")

            if self.verbose:
                import traceback
                traceback.print_exc()

            return None

    def _get_video_details(self, video_ids: List[str]) -> Dict[str, Dict]:
        """
        비디오 상세 정보 조회 (duration, view count 등)

        Args:
            video_ids: 비디오 ID 리스트 (최대 50개)

        Returns:
            {video_id: {duration, view_count}} 형태의 딕셔너리
        """
        if not video_ids:
            return {}

        # 최대 50개씩만 처리
        if len(video_ids) > 50:
            print(f"경고: 한 번에 최대 50개의 비디오만 처리 가능합니다. (요청: {len(video_ids)}개)")
            video_ids = video_ids[:50]

        url = f"{self.BASE_URL}/videos"
        params = {
            "part": "contentDetails,statistics",
            "id": ",".join(video_ids),
            "key": self.api_key
        }

        details_map = {}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # API 호출 횟수 증가
            self.api_call_count += 1

            # 원본 API 응답 출력 (verbose 모드)
            if self.verbose:
                print("\n" + "="*80)
                print("📡 YouTube API 원본 응답 (videos - details)")
                print("="*80)
                print(json.dumps(data, indent=2, ensure_ascii=False))
                print("="*80 + "\n")

            for item in data.get("items", []):
                video_id = item.get("id")
                duration = item.get("contentDetails", {}).get("duration", "")
                view_count = int(item.get("statistics", {}).get("viewCount", 0))

                details_map[video_id] = {
                    "duration": duration,
                    "view_count": view_count
                }

        except requests.exceptions.HTTPError as e:
            self.api_call_count += 1
            self._handle_http_error(e, response)
        except requests.exceptions.RequestException as e:
            print(f"YouTube API 요청 실패: {e}")

        return details_map

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

            # API 호출 횟수 증가
            self.api_call_count += 1

            # 원본 API 응답 출력 (verbose 모드)
            if self.verbose:
                print("\n" + "="*80)
                print("📡 YouTube API 원본 응답 (videos - durations)")
                print("="*80)
                print(json.dumps(data, indent=2, ensure_ascii=False))
                print("="*80 + "\n")

            for item in data.get("items", []):
                video_id = item.get("id")
                duration = item.get("contentDetails", {}).get("duration", "")
                durations_map[video_id] = duration

        except requests.exceptions.HTTPError as e:
            self.api_call_count += 1
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

        # 간단한 에러 메시지 (항상 출력)
        if status_code == 401:
            print("❌ API 키 인증 실패 (401)")
        elif status_code == 403:
            print("❌ 접근 거부 (403) - API 할당량 초과 가능성")
        elif status_code == 404:
            print("❌ 리소스를 찾을 수 없음 (404)")
        else:
            print(f"❌ HTTP 에러 발생: {status_code}")

        # 상세한 에러 메시지 (verbose 모드)
        if self.verbose:
            if status_code == 401:
                print("  1. Google Cloud Console에서 YouTube Data API v3가 활성화되어 있는지 확인")
                print("  2. API 키가 올바른지 확인")
                print("  3. API 키에 YouTube Data API v3 접근 권한이 있는지 확인")
            elif status_code == 403:
                print("  1. API 할당량 초과 여부 확인 (Google Cloud Console)")
                print("  2. 결제 계정이 연결되어 있는지 확인")
                print("  3. API 키의 제한사항 확인 (IP, Referrer 등)")
            elif status_code == 404:
                print("  1. 채널 ID 또는 비디오 ID가 올바른지 확인")
                print("  2. 삭제되었거나 비공개 처리된 리소스일 수 있음")
            else:
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

    def _save_channel_to_db(self, channel_info: Dict) -> None:
        """
        채널 정보를 DB에 저장 (update or create)

        Args:
            channel_info: 채널 정보 딕셔너리
        """
        try:
            from youtube.models import YouTubeChannel
            from django.utils.dateparse import parse_datetime

            # 날짜 파싱 (naive datetime으로 변환)
            published_at = None
            if channel_info.get('channel_published_at'):
                dt = parse_datetime(channel_info['channel_published_at'])
                if dt:
                    # timezone-aware라면 naive로 변환
                    if timezone.is_aware(dt):
                        published_at = timezone.make_naive(dt, timezone.utc)
                    else:
                        published_at = dt

            # 채널 저장 또는 업데이트
            channel, created = YouTubeChannel.objects.update_or_create(
                channel_id=channel_info['channel_id'],
                defaults={
                    'channel_title': channel_info['channel_title'],
                    'channel_description': channel_info.get('channel_description', ''),
                    'channel_custom_url': channel_info.get('channel_custom_url', ''),
                    'channel_published_at': published_at,
                    'channel_thumbnail': channel_info.get('channel_thumbnail', ''),
                    'channel_country': channel_info.get('channel_country', ''),
                    'subscriber_count': channel_info.get('subscriber_count', 0),
                    'video_count': channel_info.get('video_count', 0),
                    'view_count': channel_info.get('view_count', 0),
                    'channel_keywords': channel_info.get('channel_keywords', ''),
                    'uploads_playlist_id': channel_info.get('uploads_playlist_id', ''),
                }
            )

            action = "생성" if created else "업데이트"
            if self.verbose:
                print(f"  💾 채널 DB {action}: {channel.channel_title}")

        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  채널 DB 저장 실패: {e}")

    def _save_videos_to_db(self, videos: List[Dict], channel_info: Dict) -> None:
        """
        영상 정보를 DB에 저장 (update or create)

        Args:
            videos: 영상 정보 리스트
            channel_info: 채널 정보 딕셔너리
        """
        try:
            from youtube.models import YouTubeChannel, YouTubeVideo
            from django.utils.dateparse import parse_datetime

            # 채널 가져오기
            try:
                channel = YouTubeChannel.objects.get(channel_id=channel_info['channel_id'])
            except YouTubeChannel.DoesNotExist:
                # 채널이 없으면 먼저 생성
                self._save_channel_to_db(channel_info)
                channel = YouTubeChannel.objects.get(channel_id=channel_info['channel_id'])

            created_count = 0
            updated_count = 0

            for video_data in videos:
                # 날짜 파싱 (naive datetime으로 변환)
                published_at = None
                if video_data.get('published_at'):
                    dt = parse_datetime(video_data['published_at'])
                    if dt:
                        # timezone-aware라면 naive로 변환
                        if timezone.is_aware(dt):
                            published_at = timezone.make_naive(dt, timezone.utc)
                        else:
                            published_at = dt

                # YouTube URL 생성
                youtube_url = f"https://www.youtube.com/watch?v={video_data['video_id']}"

                # 영상 저장 또는 업데이트
                video, created = YouTubeVideo.objects.update_or_create(
                    video_id=video_data['video_id'],
                    defaults={
                        'channel': channel,
                        'title': video_data.get('title', ''),
                        'description': video_data.get('description', ''),
                        'published_at': published_at or datetime.now(),
                        'thumbnail_url': video_data.get('thumbnail_url', ''),
                        'youtube_url': youtube_url,
                        'duration': video_data.get('duration', ''),
                        'view_count': video_data.get('view_count', 0),
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            if self.verbose:
                print(f"  💾 영상 DB 저장 완료: 신규 {created_count}개, 업데이트 {updated_count}개")

        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  영상 DB 저장 실패: {e}")
            import traceback
            traceback.print_exc()

    def _save_single_video_to_db(self, video_info: Dict) -> None:
        """
        단일 영상 정보를 DB에 저장 (update or create)

        Args:
            video_info: 영상 정보 딕셔너리
        """
        try:
            from youtube.models import YouTubeChannel, YouTubeVideo
            from django.utils.dateparse import parse_datetime

            # 채널 가져오기 또는 생성
            channel_id = video_info.get('channel_id')
            if not channel_id:
                if self.verbose:
                    print(f"  ⚠️  영상에 채널 정보가 없습니다: {video_info.get('video_id')}")
                return

            # 채널이 DB에 있는지 확인, 없으면 기본 정보로 생성
            channel, created = YouTubeChannel.objects.get_or_create(
                channel_id=channel_id,
                defaults={
                    'channel_title': video_info.get('channel_title', ''),
                }
            )

            if created and self.verbose:
                print(f"  💾 채널 DB 생성: {channel.channel_title}")

            # 날짜 파싱 (naive datetime으로 변환)
            published_at = None
            if video_info.get('published_at'):
                dt = parse_datetime(video_info['published_at'])
                if dt:
                    # timezone-aware라면 naive로 변환
                    if timezone.is_aware(dt):
                        published_at = timezone.make_naive(dt, timezone.utc)
                    else:
                        published_at = dt

            # YouTube URL 생성
            youtube_url = f"https://www.youtube.com/watch?v={video_info['video_id']}"

            # 영상 저장 또는 업데이트
            video, created = YouTubeVideo.objects.update_or_create(
                video_id=video_info['video_id'],
                defaults={
                    'channel': channel,
                    'title': video_info.get('title', ''),
                    'description': video_info.get('description', ''),
                    'published_at': published_at or datetime.now(),
                    'thumbnail_url': video_info.get('thumbnail_url', ''),
                    'youtube_url': youtube_url,
                    'duration': video_info.get('duration', ''),
                    'view_count': video_info.get('view_count', 0),
                }
            )

            action = "생성" if created else "업데이트"
            if self.verbose:
                print(f"  💾 영상 DB {action}: {video_info.get('title', '')[:50]}")

        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  영상 DB 저장 실패: {e}")
            import traceback
            traceback.print_exc()

    def _save_transcript_to_db(self, video_id: str, transcript: str, language: str) -> None:
        """
        자막 정보를 DB에 저장

        Args:
            video_id: 비디오 ID
            transcript: 자막 전체 텍스트
            language: 언어 코드
        """
        try:
            from youtube.models import YouTubeVideo

            # 비디오 찾기
            try:
                video = YouTubeVideo.objects.get(video_id=video_id)
                video.transcript = transcript
                video.transcript_language = language
                video.save(update_fields=['transcript', 'transcript_language', 'updated_at'])

                if self.verbose:
                    print(f"  💾 자막 DB 저장 완료: {video.title[:50]}")

            except YouTubeVideo.DoesNotExist:
                if self.verbose:
                    print(f"  ⚠️  비디오를 찾을 수 없습니다 (DB에 없음): {video_id}")

        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  자막 DB 저장 실패: {e}")
                import traceback
                traceback.print_exc()

    def _print_api_call_summary(self) -> None:
        """
        API 호출 횟수 요약 출력
        """
        if self.verbose:
            print("\n" + "="*80)
            print(f"📊 YouTube API 호출 요약")
            print("="*80)
            print(f"총 API 호출 횟수: {self.api_call_count}회")
            print("="*80 + "\n")
