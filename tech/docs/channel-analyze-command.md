# 채널 분석 순서

## 채널 정보 저장
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_get_channel_info @살림남

## 영상 리스트 저장
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_save_recent_channel_videos @살림남 --max-results 100 --months 6

## 영상 자막 저장
**IP block 위험이 있으므로 아이폰 테더링으로 진행할 것**
docker exec royt-royt-api-gateway-1 ./manage.py test_youtube_api_save_all_channel_video_transcripts @살림남

## 영상 정보 저장
docker exec royt-royt-api-gateway-1 ./manage.py save_channel_video_details @살림남


