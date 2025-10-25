/**
 * YouTube API 관련 타입 정의
 */

// YouTube 채널 정보 타입
export interface YouTubeChannel {
  id: number;
  channel_id: string;
  channel_title: string;
  channel_thumbnail: string;
  subscriber_count: number;
  view_count: number;
}

// YouTube 비디오 타입
export interface YouTubeVideo {
  id: number;
  video_id: string;
  title: string;
  description: string;
  published_at: string;
  view_count: number;
  like_count: number;
  comment_count: number;
  engagement_rate: number;
  views_per_subscriber: number;
  thumbnail_url: string;
  youtube_url: string;
  duration: string;
  category_id: string;
  tags: string[];
  transcript_status: string;
  channel: number;
  channel_data: YouTubeChannel;
}

// 비디오 조회 쿼리 파라미터 타입
export interface VideoQueryParams {
  ordering?: string;
  page?: number;
  page_size?: number;
  category_id?: string;
  channel?: number;
  transcript_status?: string;
}
