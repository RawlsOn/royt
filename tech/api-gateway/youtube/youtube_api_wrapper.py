"""
YouTube Data API v3 Wrapper
채널 정보 조회 및 영상 목록 조회 기능 제공
"""
import re
import json
import time
import random
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from youtube.models import YouTubeChannel, YouTubeVideo
from common.util.print_util import tprint, tprint_header, tprint_separator


class YouTubeAPIWrapper:
    """YouTube Data API v3 래퍼 클래스"""

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: Optional[str] = None, save_to_db: bool = True, verbose: bool = True):
        """
        YouTube API 래퍼 초기화

        Args:
            api_key: YouTube Data API v3 키 (None이면 settings.YOUTUBE_API_KEY 사용)
            save_to_db: API 호출 결과를 DB에 저장할지 여부 (기본값: True)
            verbose: 상세 로그 출력 여부 (기본값: True)
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
                ttprint()
                tprint_separator("=", 80)
                ttprint("📡 YouTube API 원본 응답 (JSON)")
                tprint_separator("=", 80)
                ttprint(json.dumps(data, indent=2, ensure_ascii=False))
                tprint_separator("=", 80)
                ttprint()

            items = data.get("items", [])
            if not items:
                if self.verbose:
                    ttprint(f"채널을 찾을 수 없습니다: {channel_identifier}")
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
                tprint(f"✅ 채널 정보 조회 완료: {channel_info['channel_title']} (구독자: {channel_info['subscriber_count']:,}명)")

            # API 호출 요약 출력
            self._print_api_call_summary()

            return channel_info

        except requests.exceptions.HTTPError as e:
            self.api_call_count += 1
            self._handle_http_error(e, response)
            self._print_api_call_summary()
            return None
        except requests.exceptions.RequestException as e:
            ttprint(f"YouTube API 요청 실패: {e}")
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
                        tprint(f"  ✅ DB에서 uploads_playlist_id 캐시 사용: {uploads_playlist_id}")
            except Exception as e:
                if self.verbose:
                    tprint(f"  ⚠️  DB 조회 실패: {e}")

        # 2. DB에 없으면 API로 채널 정보 조회
        if not uploads_playlist_id:
            if self.verbose:
                tprint(f"  🔍 API로 채널 정보 조회 중...")
            channel_info = self.get_channel_info(channel_identifier)
            if not channel_info:
                return []

            uploads_playlist_id = channel_info.get("uploads_playlist_id")
            if not uploads_playlist_id:
                if self.verbose:
                    tprint(f"채널의 uploads_playlist_id를 찾을 수 없습니다: {channel_identifier}")
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
                    ttprint()
                    tprint_separator("=", 80)
                    ttprint("📡 YouTube API 원본 응답 (playlistItems)")
                    tprint_separator("=", 80)
                    ttprint(json.dumps(data, indent=2, ensure_ascii=False))
                    tprint_separator("=", 80)
                    ttprint()

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
                ttprint(f"YouTube API 요청 실패: {e}")
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
                        tprint(f"  ⚠️  채널 정보 조회 실패: {e}")

            if channel_info:
                self._save_videos_to_db(videos, channel_info)

        # 간단한 요약 출력
        if not self.verbose:
            tprint(f"✅ 채널 영상 목록 조회 완료: {len(videos[:max_results])}개")

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
            tprint(f"\n{'='*80}")
            tprint(f"📅 최근 {months}개월 영상 저장 시작")
            tprint(f"   기준 날짜: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
            tprint(f"{'='*80}\n")

        # list_channel_videos로 영상 목록 조회
        videos = self.list_channel_videos(channel_identifier, max_results=max_results)

        if not videos:
            if not self.verbose:
                tprint("❌ 조회된 영상이 없습니다.")
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
                    tprint(f"  ⚠️  날짜 파싱 실패: {video.get('video_id')} - {e}")
                continue

        # 필터링된 영상 정보 출력
        if self.verbose:
            tprint(f"\n{'='*80}")
            tprint(f"📊 필터링 결과")
            tprint(f"{'='*80}")
            tprint(f"전체 조회 영상: {len(videos)}개")
            tprint(f"최근 {months}개월 영상: {len(recent_videos)}개")
            tprint(f"{'='*80}\n")

        # DB에 저장 (save_to_db가 True인 경우 이미 list_channel_videos에서 저장됨)
        # 하지만 필터링된 영상만 반환

        # 간단한 요약 출력
        if not self.verbose:
            tprint(f"✅ 최근 {months}개월 영상 {len(recent_videos)}개 필터링 완료 (전체 {len(videos)}개 중)")

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
                tprint(f"\n{'='*80}")
                tprint(f"🗑️  {months}개월 이상 된 영상 삭제 시작")
                tprint(f"   기준 날짜: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
                tprint(f"{'='*80}\n")

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
                        tprint(f"❌ 채널을 찾을 수 없습니다: {channel_identifier}")
                    return {
                        'deleted_count': 0,
                        'channel_id': None,
                        'cutoff_date': cutoff_date
                    }

                channel_id = channel.channel_id
                videos_query = videos_query.filter(channel=channel)

                if self.verbose:
                    tprint(f"  📌 특정 채널만 삭제: {channel.channel_title} ({channel_id})")

            # 삭제 전 카운트
            old_videos_count = videos_query.count()

            if old_videos_count == 0:
                if not self.verbose:
                    tprint(f"✅ 삭제할 오래된 영상이 없습니다.")
                return {
                    'deleted_count': 0,
                    'channel_id': channel_id,
                    'cutoff_date': cutoff_date
                }

            # verbose 모드일 때 삭제될 영상 목록 출력
            if self.verbose:
                tprint(f"\n{'='*80}")
                tprint(f"📋 삭제 대상 영상 목록 (총 {old_videos_count}개)")
                tprint(f"{'='*80}")
                for video in videos_query[:10]:
                    tprint(f"- {video.title[:60]}")
                    tprint(f"  게시일: {video.published_at.strftime('%Y-%m-%d') if video.published_at else 'N/A'}")
                    tprint(f"  비디오 ID: {video.video_id}")
                    tprint()

                if old_videos_count > 10:
                    tprint(f"... 외 {old_videos_count - 10}개")
                tprint(f"{'='*80}\n")

            # 삭제 실행
            deleted_count, _ = videos_query.delete()

            # 결과 출력
            if not self.verbose:
                if channel_identifier:
                    tprint(f"✅ {months}개월 이상 된 영상 {deleted_count}개 삭제 완료 (채널: {channel_identifier})")
                else:
                    tprint(f"✅ {months}개월 이상 된 영상 {deleted_count}개 삭제 완료 (모든 채널)")

            if self.verbose:
                tprint(f"\n{'='*80}")
                tprint(f"📊 삭제 완료")
                tprint(f"{'='*80}")
                tprint(f"삭제된 영상 수: {deleted_count}개")
                if channel_identifier:
                    tprint(f"대상 채널: {channel_identifier}")
                else:
                    tprint(f"대상 채널: 모든 채널")
                tprint(f"기준 날짜: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} 이전")
                tprint(f"{'='*80}\n")

            return {
                'deleted_count': deleted_count,
                'channel_id': channel_id,
                'cutoff_date': cutoff_date
            }

        except Exception as e:
            if self.verbose:
                tprint(f"❌ 영상 삭제 실패: {e}")
                import traceback
                traceback.print_exc()
            else:
                tprint(f"❌ 영상 삭제 실패: {e}")

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
            tprint(f"채널 ID를 찾을 수 없습니다: {channel_identifier}")
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
                    tprint("\n" + "="*80)
                    tprint("📡 YouTube API 원본 응답 (search)")
                    tprint("="*80)
                    tprint(json.dumps(data, indent=2, ensure_ascii=False))
                    tprint("="*80 + "\n")

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
                    ttprint(f"YouTube API 요청 실패: {e}")
                break

        # DB에 저장
        if self.save_to_db and videos:
            self._save_videos_to_db(videos, channel_info)

        # 간단한 요약 출력
        if not self.verbose:
            tprint(f"✅ 채널 영상 검색 완료: {len(videos[:max_results])}개 (정렬: {order})")

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
                tprint("\n" + "="*80)
                tprint("📡 YouTube API 원본 응답 (videos - get_video_info)")
                tprint("="*80)
                tprint(json.dumps(data, indent=2, ensure_ascii=False))
                tprint("="*80 + "\n")

            items = data.get("items", [])
            if not items:
                if self.verbose:
                    tprint(f"비디오를 찾을 수 없습니다: {video_id}")
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
                tprint(f"✅ 비디오 정보 조회 완료: {video_info['title'][:50]} (조회수: {video_info['view_count']:,})")

            # API 호출 요약 출력
            self._print_api_call_summary()

            return video_info

        except requests.exceptions.HTTPError as e:
            self.api_call_count += 1
            self._handle_http_error(e, response)
            self._print_api_call_summary()
            return None
        except requests.exceptions.RequestException as e:
            ttprint(f"YouTube API 요청 실패: {e}")
            self._print_api_call_summary()
            return None

    def get_trending_videos(
        self,
        region_code: str = "KR",
        category_id: Optional[str] = None,
        max_results: int = 50
    ) -> List[Dict]:
        """
        인기 급상승 영상 조회

        Args:
            region_code: 국가 코드 (기본값: 'KR')
            category_id: 카테고리 ID (None이면 전체 카테고리)
            max_results: 조회할 최대 영상 개수 (기본값: 50, 최대: 200)

        Returns:
            영상 정보 리스트
            [
                {
                    'video_id': str,
                    'title': str,
                    'description': str,
                    'channel_id': str,
                    'channel_title': str,
                    'published_at': str,
                    'thumbnail_url': str,
                    'duration': str,  # ISO 8601 형식
                    'duration_seconds': int,  # 초 단위
                    'is_short': bool,  # 60초 미만 여부
                    'view_count': int,
                    'like_count': int,
                    'comment_count': int,
                    'tags': List[str],
                    'category_id': str,
                },
                ...
            ]
        """
        # 최대 200개로 제한
        if max_results > 200:
            tprint(f"⚠️  최대 조회 가능 개수는 200개입니다. (요청: {max_results}개) -> 200개로 제한합니다.")
            max_results = 200

        videos = []
        next_page_token = None

        while len(videos) < max_results:
            url = f"{self.BASE_URL}/videos"
            params = {
                "part": "snippet,statistics,contentDetails",
                "chart": "mostPopular",
                "regionCode": region_code,
                "maxResults": min(50, max_results - len(videos)),  # 최대 50개씩
                "key": self.api_key
            }

            # category_id가 None이 아닐 때만 추가
            if category_id:
                params["videoCategoryId"] = category_id

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
                    tprint()
                    tprint_separator("=", 80)
                    tprint("📡 YouTube API 원본 응답 (videos - trending)")
                    tprint_separator("=", 80)
                    tprint(json.dumps(data, indent=2, ensure_ascii=False))
                    tprint_separator("=", 80)
                    tprint()

                items = data.get("items", [])
                if not items:
                    break

                # 영상 정보 파싱
                for item in items:
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
                        "channel_id": snippet.get("channelId", ""),
                        "channel_title": snippet.get("channelTitle", ""),
                        "published_at": snippet.get("publishedAt", ""),
                        "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                        "duration": duration,
                        "duration_seconds": duration_seconds,
                        "is_short": is_short,
                        "view_count": int(statistics.get("viewCount", 0)),
                        "like_count": int(statistics.get("likeCount", 0)),
                        "comment_count": int(statistics.get("commentCount", 0)),
                        "tags": snippet.get("tags", []),
                        "category_id": snippet.get("categoryId", ""),
                    }

                    videos.append(video_info)

                    # DB에 저장
                    if self.save_to_db:
                        self._save_single_video_to_db(video_info)

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
                tprint(f"YouTube API 요청 실패: {e}")
                break

        # 간단한 요약 출력
        if not self.verbose:
            category_msg = f" (카테고리: {category_id})" if category_id else ""
            tprint(f"✅ 인기 급상승 영상 조회 완료: {len(videos)}개 (지역: {region_code}{category_msg})")

        # API 호출 요약 출력
        self._print_api_call_summary()

        return videos

    def get_video_transcript(
        self,
        video_id: str,
        languages: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        비디오 자막 조회 (youtube-transcript-api 사용)

        공식 문서: https://pypi.org/project/youtube-transcript-api/

        Args:
            video_id: 유튜브 비디오 ID
            languages: 우선순위 언어 리스트 (기본값: ['ko'])

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

        # DB에 이미 시도한 기록이 있는지 확인
        try:
            existing_video = YouTubeVideo.objects.get(video_id=video_id)

            # 이미 조회를 시도한 적이 있으면
            if existing_video.transcript_status:
                # 성공한 경우 - 자막 반환
                if existing_video.transcript_status == 'success' and existing_video.transcript:
                    if self.verbose:
                        tprint(f"\n{'='*80}")
                        tprint(f"📝 자막 조회: {video_id}")
                        tprint(f"{'='*80}\n")
                        tprint(f"  ✅ DB에 이미 자막이 저장되어 있습니다")
                        tprint(f"     언어: {existing_video.transcript_language}")
                        tprint(f"     길이: {len(existing_video.transcript)}자")
                    else:
                        tprint(f"✅ DB에서 자막 조회: {video_id} (언어: {existing_video.transcript_language}, {len(existing_video.transcript)}자)")

                    return {
                        'video_id': video_id,
                        'transcript': existing_video.transcript,
                        'language': existing_video.transcript_language,
                        'status': 'success'
                    }

                # 실패한 경우 - 다시 시도하지 않음
                else:
                    if not self.verbose:
                        tprint(f"⏭️  이전 시도 기록: {existing_video.transcript_status} (건너뛰기)")

                    return {
                        'video_id': video_id,
                        'error': f'Previously failed with status: {existing_video.transcript_status}',
                        'error_type': 'PreviouslyFailed',
                        'status': existing_video.transcript_status
                    }

        except YouTubeVideo.DoesNotExist:
            pass  # DB에 없으면 YouTube에서 가져옴

        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            if self.verbose:
                tprint(f"\n{'='*80}")
                tprint(f"📝 자막 조회 시작: {video_id}")
                tprint(f"   우선 언어: {', '.join(languages)}")
                tprint(f"{'='*80}\n")

            # 공식 PyPI 문서의 권장 방법: fetch() 메서드 사용
            if self.verbose:
                tprint(f"  🔍 YouTube에서 자막 데이터 조회 중...")

            ytt_api = YouTubeTranscriptApi()
            transcript_data = ytt_api.fetch(video_id, languages=languages)

            if self.verbose:
                tprint(f"  ✅ 자막 데이터 조회 성공 ({len(transcript_data)}개 세그먼트)")

            # 전체 텍스트 생성
            # FetchedTranscriptSnippet 객체는 .text, .start, .duration 속성으로 접근
            full_text = ' '.join([segment.text for segment in transcript_data])

            # 사용된 언어
            used_language = languages[0] if languages else 'unknown'

            if self.verbose:
                tprint(f"\n{'='*80}")
                tprint(f"📊 자막 정보")
                tprint(f"{'='*80}")
                tprint(f"언어: {used_language}")
                tprint(f"세그먼트 수: {len(transcript_data)}개")
                tprint(f"전체 길이: {len(full_text)}자")
                tprint(f"첫 100자: {full_text[:100]}...")
                tprint(f"{'='*80}\n")

            transcript_info = {
                'video_id': video_id,
                'transcript': full_text,
                'language': used_language,
            }

            # verbose 모드에서는 세그먼트 정보도 포함 (딕셔너리로 변환)
            if self.verbose:
                transcript_info['segments'] = [
                    {
                        'text': seg.text,
                        'start': seg.start,
                        'duration': seg.duration
                    }
                    for seg in transcript_data[:5]  # 첫 5개만
                ]

            # DB에 저장
            if self.save_to_db:
                self._save_transcript_to_db(video_id, full_text, used_language)

            # 간단한 요약 출력
            if not self.verbose:
                tprint(f"✅ 자막 조회 완료: {video_id} (언어: {used_language}, {len(full_text)}자)")

            return transcript_info

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)

            # 에러 타입별 처리 및 상태 저장
            status = 'error'
            if 'TranscriptsDisabled' in error_type:
                tprint(f"❌ 자막이 비활성화되어 있습니다: {video_id}")
                status = 'disabled'
            elif 'VideoUnavailable' in error_type:
                tprint(f"❌ 비디오를 사용할 수 없습니다: {video_id}")
                status = 'unavailable'
            elif 'NoTranscriptFound' in error_type:
                tprint(f"❌ 자막을 찾을 수 없습니다: {video_id} (언어: {', '.join(languages)})")
                if self.verbose:
                    tprint(f"   요청한 언어의 자막이 없습니다.")
                status = 'no_transcript'
            else:
                tprint(f"❌ 자막 조회 실패: {video_id} - {e}")
                status = 'error'

            # DB에 상태 저장
            if self.save_to_db:
                self._save_transcript_status_to_db(video_id, status)

            if self.verbose:
                import traceback
                traceback.print_exc()

            # 에러 정보 반환 (IP 블락 감지용)
            return {
                'video_id': video_id,
                'error': error_msg,
                'error_type': error_type,
                'status': status
            }

    def save_all_channel_video_transcripts(
        self,
        channel_identifier: str,
        languages: Optional[List[str]] = None
    ) -> Dict:
        """
        채널의 모든 영상 자막을 저장

        Args:
            channel_identifier: 채널 ID 또는 핸들 (예: @채널명)
            languages: 우선순위 언어 리스트 (기본값: ['ko'])

        Returns:
            결과 딕셔너리 {
                'total': 전체 영상 수,
                'success': 성공 수,
                'failed': 실패 수,
                'skipped': 건너뛴 수 (이미 DB에 있음)
            }
        """
        if languages is None:
            languages = ['ko']

        tprint(f"\n{'='*80}")
        tprint(f"📝 채널 영상 자막 일괄 저장")
        tprint(f"{'='*80}")
        tprint(f"채널: {channel_identifier}")
        tprint(f"언어: {', '.join(languages)}")
        tprint(f"{'='*80}\n")

        # DB에서 채널의 모든 영상 가져오기
        try:
            if channel_identifier.startswith('@'):
                # 핸들로 조회
                channel = YouTubeChannel.objects.get(channel_custom_url=channel_identifier)
            else:
                # 채널 ID로 조회
                channel = YouTubeChannel.objects.get(channel_id=channel_identifier)
        except YouTubeChannel.DoesNotExist:
            tprint(f"❌ 채널을 찾을 수 없습니다: {channel_identifier}")
            tprint(f"   먼저 get_channel_info로 채널 정보를 저장해 주세요.")
            return {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0}

        # 채널의 모든 영상 가져오기
        videos = YouTubeVideo.objects.filter(channel=channel).order_by('-published_at')
        total_count = videos.count()

        if total_count == 0:
            tprint(f"❌ 채널에 저장된 영상이 없습니다: {channel.channel_title}")
            tprint(f"   먼저 list_channel_videos로 영상 목록을 저장해 주세요.")
            return {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0}

        tprint(f"📊 총 {total_count}개 영상 발견")
        tprint(f"{'='*80}\n")

        success_count = 0
        failed_count = 0
        skipped_count = 0

        for idx, video in enumerate(videos, 1):
            # 진행 상황 출력
            tprint(f"[{idx}/{total_count}] {video.title[:50]}...")

            # 이미 시도한 적이 있으면 건너뛰기
            if video.transcript_status:
                if video.transcript_status == 'success':
                    tprint(f"  ⏭️  이미 자막 있음 (건너뛰기)")
                else:
                    tprint(f"  ⏭️  이전 시도: {video.transcript_status} (건너뛰기)")
                skipped_count += 1
                continue

            # 자막 가져오기
            result = self.get_video_transcript(
                video_id=video.video_id,
                languages=languages
            )

            # IP 블락 감지 (다양한 패턴 체크)
            if result and isinstance(result, dict) and 'error' in result:
                error_msg = result['error'].lower()
                error_type = result.get('error_type', '')

                # IP 블락 관련 키워드 체크
                ip_block_keywords = [
                    'youtube is blocking requests from your ip',
                    'blocking requests',
                    'ip has been blocked',
                    'requestblocked',
                    'ipblocked'
                ]

                is_blocked = any(keyword in error_msg for keyword in ip_block_keywords)

                if is_blocked:
                    tprint(f"\n{'='*80}")
                    tprint(f"🚫 YouTube IP 블락 감지!")
                    tprint(f"{'='*80}")
                    tprint(f"YouTube에서 IP 차단을 감지했습니다.")
                    tprint(f"에러: {result['error'][:200]}...")
                    tprint(f"\n작업을 중단합니다.")
                    tprint(f"\n현재까지 결과:")
                    tprint(f"  처리: {idx}/{total_count}개")
                    tprint(f"  성공: {success_count}개")
                    tprint(f"  실패: {failed_count}개")
                    tprint(f"  건너뛰기: {skipped_count}개")
                    tprint(f"{'='*80}\n")
                    tprint(f"💡 해결 방법:")
                    tprint(f"  - 잠시 후에 다시 시도하세요")
                    tprint(f"  - 프록시나 VPN을 사용하세요")
                    tprint(f"  - 다른 네트워크에서 시도하세요")
                    tprint(f"{'='*80}\n")
                    return {
                        'total': total_count,
                        'success': success_count,
                        'failed': failed_count,
                        'skipped': skipped_count,
                        'stopped': True,
                        'stopped_at': idx
                    }

            if result and 'error' not in result:
                success_count += 1
            else:
                failed_count += 1

            # IP 블락 방지를 위한 랜덤 sleep (180~300초)
            if idx < total_count:  # 마지막 영상이 아니면
                sleep_time = random.uniform(180, 300)
                tprint(f"  ⏱️  대기 중... ({sleep_time:.1f}초)")
                time.sleep(sleep_time)

            tprint()  # 빈 줄

        # 최종 결과
        tprint(f"{'='*80}")
        tprint(f"📊 자막 저장 완료")
        tprint(f"{'='*80}")
        tprint(f"전체: {total_count}개")
        tprint(f"성공: {success_count}개")
        tprint(f"실패: {failed_count}개")
        tprint(f"건너뛰기: {skipped_count}개 (이미 DB에 있음)")
        tprint(f"{'='*80}\n")

        return {
            'total': total_count,
            'success': success_count,
            'failed': failed_count,
            'skipped': skipped_count
        }

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
            tprint(f"경고: 한 번에 최대 50개의 비디오만 처리 가능합니다. (요청: {len(video_ids)}개)")
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
                tprint("\n" + "="*80)
                tprint("📡 YouTube API 원본 응답 (videos - details)")
                tprint("="*80)
                tprint(json.dumps(data, indent=2, ensure_ascii=False))
                tprint("="*80 + "\n")

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
            ttprint(f"YouTube API 요청 실패: {e}")

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
            tprint(f"경고: 한 번에 최대 50개의 비디오만 처리 가능합니다. (요청: {len(video_ids)}개)")
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
                tprint("\n" + "="*80)
                tprint("📡 YouTube API 원본 응답 (videos - durations)")
                tprint("="*80)
                tprint(json.dumps(data, indent=2, ensure_ascii=False))
                tprint("="*80 + "\n")

            for item in data.get("items", []):
                video_id = item.get("id")
                duration = item.get("contentDetails", {}).get("duration", "")
                durations_map[video_id] = duration

        except requests.exceptions.HTTPError as e:
            self.api_call_count += 1
            self._handle_http_error(e, response)
        except requests.exceptions.RequestException as e:
            ttprint(f"YouTube API 요청 실패: {e}")

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
            tprint("❌ API 키 인증 실패 (401)")
        elif status_code == 403:
            tprint("❌ 접근 거부 (403) - API 할당량 초과 가능성")
        elif status_code == 404:
            tprint("❌ 리소스를 찾을 수 없음 (404)")
        else:
            tprint(f"❌ HTTP 에러 발생: {status_code}")

        # 상세한 에러 메시지 (verbose 모드)
        if self.verbose:
            if status_code == 401:
                tprint("  1. Google Cloud Console에서 YouTube Data API v3가 활성화되어 있는지 확인")
                tprint("  2. API 키가 올바른지 확인")
                tprint("  3. API 키에 YouTube Data API v3 접근 권한이 있는지 확인")
            elif status_code == 403:
                tprint("  1. API 할당량 초과 여부 확인 (Google Cloud Console)")
                tprint("  2. 결제 계정이 연결되어 있는지 확인")
                tprint("  3. API 키의 제한사항 확인 (IP, Referrer 등)")
            elif status_code == 404:
                tprint("  1. 채널 ID 또는 비디오 ID가 올바른지 확인")
                tprint("  2. 삭제되었거나 비공개 처리된 리소스일 수 있음")
            else:
                tprint(f"   메시지: {error}")

            # API 응답 메시지 출력
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_info = error_data["error"]
                    tprint(f"\n   API 에러 메시지:")
                    tprint(f"   - Code: {error_info.get('code')}")
                    tprint(f"   - Message: {error_info.get('message')}")
                    if "errors" in error_info:
                        for err in error_info["errors"]:
                            tprint(f"   - Reason: {err.get('reason')}")
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
                tprint(f"  💾 채널 DB {action}: {channel.channel_title}")

        except Exception as e:
            if self.verbose:
                tprint(f"  ⚠️  채널 DB 저장 실패: {e}")

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
                tprint(f"  💾 영상 DB 저장 완료: 신규 {created_count}개, 업데이트 {updated_count}개")

        except Exception as e:
            if self.verbose:
                tprint(f"  ⚠️  영상 DB 저장 실패: {e}")
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
                    tprint(f"  ⚠️  영상에 채널 정보가 없습니다: {video_info.get('video_id')}")
                return

            # 채널이 DB에 있는지 확인, 없으면 기본 정보로 생성
            channel, created = YouTubeChannel.objects.get_or_create(
                channel_id=channel_id,
                defaults={
                    'channel_title': video_info.get('channel_title', ''),
                }
            )

            if created and self.verbose:
                tprint(f"  💾 채널 DB 생성: {channel.channel_title}")

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
                tprint(f"  💾 영상 DB {action}: {video_info.get('title', '')[:50]}")

        except Exception as e:
            if self.verbose:
                tprint(f"  ⚠️  영상 DB 저장 실패: {e}")
            import traceback
            traceback.print_exc()

    def _save_transcript_to_db(self, video_id: str, transcript: str, language: str, status: str = 'success') -> None:
        """
        자막 정보를 DB에 저장

        Args:
            video_id: 비디오 ID
            transcript: 자막 전체 텍스트
            language: 언어 코드
            status: 자막 조회 상태 (기본값: 'success')
        """
        try:
            # 비디오 찾기
            try:
                video = YouTubeVideo.objects.get(video_id=video_id)
                video.transcript = transcript
                video.transcript_language = language
                video.transcript_status = status
                video.save(update_fields=['transcript', 'transcript_language', 'transcript_status', 'updated_at'])

                if self.verbose:
                    tprint(f"  💾 자막 DB 저장 완료: {video.title[:50]}")

            except YouTubeVideo.DoesNotExist:
                if self.verbose:
                    tprint(f"  ⚠️  비디오를 찾을 수 없습니다 (DB에 없음): {video_id}")

        except Exception as e:
            if self.verbose:
                tprint(f"  ⚠️  자막 DB 저장 실패: {e}")
                import traceback
                traceback.print_exc()

    def _save_transcript_status_to_db(self, video_id: str, status: str) -> None:
        """
        자막 조회 상태만 DB에 저장

        Args:
            video_id: 비디오 ID
            status: 자막 조회 상태 (no_transcript, disabled, unavailable, error)
        """
        try:
            try:
                video = YouTubeVideo.objects.get(video_id=video_id)
                video.transcript_status = status
                video.save(update_fields=['transcript_status', 'updated_at'])

                if self.verbose:
                    tprint(f"  💾 자막 상태 저장: {status}")

            except YouTubeVideo.DoesNotExist:
                if self.verbose:
                    tprint(f"  ⚠️  비디오를 찾을 수 없습니다 (DB에 없음): {video_id}")

        except Exception as e:
            if self.verbose:
                tprint(f"  ⚠️  자막 상태 저장 실패: {e}")

    def save_channel_video_details(self, channel_identifier: str) -> Dict:
        """
        특정 채널의 모든 비디오에 대해 상세 정보를 조회하고 저장
        이미 상세 정보가 있는 비디오(view_count > 0)는 건너뜀

        Args:
            channel_identifier: 유튜브 채널 ID 또는 핸들 (@username 형태)

        Returns:
            처리 결과 딕셔너리
            {
                'total_videos': int,  # 전체 비디오 수
                'skipped': int,  # 이미 상세 정보가 있어서 건너뛴 수
                'processed': int,  # 새로 처리한 수
                'failed': int,  # 실패한 수
                'api_calls': int,  # 사용한 API 호출 수
            }
        """
        if self.verbose:
            tprint()
            tprint_separator("=", 80)
            tprint(f"📹 채널 비디오 상세 정보 저장 시작")
            tprint(f"   채널: {channel_identifier}")
            tprint_separator("=", 80)
            tprint()

        # 1. 채널 정보 확인
        try:
            channel = YouTubeChannel.objects.get(
                channel_id=channel_identifier if not channel_identifier.startswith('@')
                else YouTubeChannel.objects.filter(channel_custom_url__icontains=channel_identifier[1:]).first().channel_id
            )
        except Exception as e:
            if self.verbose:
                tprint(f"❌ 채널을 찾을 수 없습니다: {channel_identifier}")
                tprint(f"   오류: {e}")
            return {
                'total_videos': 0,
                'skipped': 0,
                'processed': 0,
                'failed': 0,
                'api_calls': 0
            }

        # 2. 해당 채널의 모든 비디오 조회
        all_videos = YouTubeVideo.objects.filter(channel=channel)
        total_count = all_videos.count()

        # 3. 상세 정보가 없는 비디오만 필터링 (view_count가 0인 것들)
        videos_to_process = all_videos.filter(view_count=0)
        to_process_count = videos_to_process.count()
        skipped_count = total_count - to_process_count

        if self.verbose:
            tprint(f"📊 비디오 분석:")
            tprint(f"   전체 비디오: {total_count}개")
            tprint(f"   상세 정보 필요: {to_process_count}개")
            tprint(f"   건너뛸 비디오: {skipped_count}개 (이미 상세 정보 있음)")
            tprint()

        if to_process_count == 0:
            if self.verbose:
                tprint("✅ 모든 비디오가 이미 상세 정보를 가지고 있습니다.")
                self._print_api_call_summary()
            return {
                'total_videos': total_count,
                'skipped': skipped_count,
                'processed': 0,
                'failed': 0,
                'api_calls': 0
            }

        # 4. 비디오 ID 목록 생성
        video_ids = list(videos_to_process.values_list('video_id', flat=True))

        processed_count = 0
        failed_count = 0

        if self.verbose:
            tprint(f"🔄 상세 정보 조회 시작...")
            tprint()

        # 5. 50개씩 배치 처리 (YouTube API 제한)
        batch_size = 50
        for i in range(0, len(video_ids), batch_size):
            batch_ids = video_ids[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(video_ids) + batch_size - 1) // batch_size

            if self.verbose:
                tprint(f"📦 배치 {batch_num}/{total_batches} 처리 중 ({len(batch_ids)}개 비디오)...")

            # API 호출 전 랜덤 대기 (3-5초)
            if i > 0:  # 첫 번째 배치는 대기하지 않음
                delay = random.uniform(3, 5)
                if self.verbose:
                    tprint(f"   ⏱️  {delay:.1f}초 대기 중...")
                time.sleep(delay)

            # 비디오 상세 정보 조회
            try:
                video_details = self._get_video_details_for_save(batch_ids)

                # 각 비디오 정보 업데이트
                for video_id, details in video_details.items():
                    try:
                        video = YouTubeVideo.objects.get(video_id=video_id)
                        video.view_count = details.get('view_count', 0)
                        video.like_count = details.get('like_count', 0)
                        video.comment_count = details.get('comment_count', 0)
                        video.category_id = details.get('category_id', '')
                        video.tags = details.get('tags', [])
                        video.save()
                        processed_count += 1

                        if self.verbose:
                            tprint(f"   ✅ {video.title[:50]}... (조회수: {video.view_count:,})")
                    except Exception as e:
                        failed_count += 1
                        if self.verbose:
                            tprint(f"   ❌ DB 저장 실패 (video_id: {video_id}): {e}")

            except Exception as e:
                failed_count += len(batch_ids)
                if self.verbose:
                    tprint(f"   ❌ API 호출 실패: {e}")

            if self.verbose:
                tprint()

        # 6. 결과 출력
        if self.verbose:
            tprint_separator("=", 80)
            tprint(f"✅ 채널 비디오 상세 정보 저장 완료")
            tprint_separator("=", 80)
            tprint(f"전체 비디오: {total_count}개")
            tprint(f"건너뛴 비디오: {skipped_count}개")
            tprint(f"처리 성공: {processed_count}개")
            tprint(f"처리 실패: {failed_count}개")
            tprint_separator("=", 80)
            tprint()

            self._print_api_call_summary()

        return {
            'total_videos': total_count,
            'skipped': skipped_count,
            'processed': processed_count,
            'failed': failed_count,
            'api_calls': self.api_call_count
        }

    def _get_video_details_for_save(self, video_ids: List[str]) -> Dict[str, Dict]:
        """
        비디오 상세 정보 조회 (저장용 - 더 많은 정보 포함)

        Args:
            video_ids: 비디오 ID 리스트 (최대 50개)

        Returns:
            {video_id: {view_count, like_count, comment_count, category_id, tags}} 형태의 딕셔너리
        """
        if not video_ids:
            return {}

        # 최대 50개씩만 처리
        if len(video_ids) > 50:
            if self.verbose:
                tprint(f"⚠️  경고: 한 번에 최대 50개의 비디오만 처리 가능합니다. (요청: {len(video_ids)}개)")
            video_ids = video_ids[:50]

        url = f"{self.BASE_URL}/videos"
        params = {
            "part": "statistics,snippet",
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
                tprint()
                tprint_separator("=", 80)
                tprint("📡 YouTube API 원본 응답 (videos - full details)")
                tprint_separator("=", 80)
                tprint(json.dumps(data, indent=2, ensure_ascii=False))
                tprint_separator("=", 80)
                tprint()

            for item in data.get("items", []):
                video_id = item.get("id")
                statistics = item.get("statistics", {})
                snippet = item.get("snippet", {})

                details_map[video_id] = {
                    "view_count": int(statistics.get("viewCount", 0)),
                    "like_count": int(statistics.get("likeCount", 0)),
                    "comment_count": int(statistics.get("commentCount", 0)),
                    "category_id": snippet.get("categoryId", ""),
                    "tags": snippet.get("tags", [])
                }

        except requests.exceptions.HTTPError as e:
            self.api_call_count += 1
            self._handle_http_error(e, response)
        except requests.exceptions.RequestException as e:
            tprint(f"YouTube API 요청 실패: {e}")

        return details_map

    def _print_api_call_summary(self) -> None:
        """
        API 호출 횟수 요약 출력
        """
        if self.verbose:
            tprint()
            tprint_separator("=", 80)
            tprint(f"📊 YouTube API 호출 요약")
            tprint_separator("=", 80)
            tprint(f"총 API 호출 횟수: {self.api_call_count}회")
            tprint_separator("=", 80)
            tprint()
