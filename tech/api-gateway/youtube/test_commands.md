# YouTube API 테스트 커맨드 사용법

YouTube API 래퍼 클래스의 기능을 테스트하기 위한 Django 관리 커맨드 문서입니다.

---

## 채널 정보 조회
```bash
# 채널 ID로 조회
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_channel_info UC_x5XG1OV2P6uZZ5FSM9Ttw

# 채널 핸들로 조회
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_channel_info @떠들썩
```

## 비디오 목록 조회
```bash
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_list_channel_videos UCPF2WvEWPP-1utUwwsdbeCw
```
