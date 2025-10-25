/**
 * YouTube API 서비스
 * YouTube 비디오 관련 API 호출 함수
 */

import apiClient from './client';
import type { PaginatedResponse } from '@/types/api';
import type { YouTubeVideo, VideoQueryParams } from '@/types/youtube';

/**
 * YouTube 비디오 목록 조회
 * @param params - 조회 조건 (정렬, 페이지네이션, 필터링)
 * @returns 페이지네이션된 YouTube 비디오 목록
 */
export const getYouTubeVideos = async (
  params?: VideoQueryParams
): Promise<PaginatedResponse<YouTubeVideo>> => {
  const response = await apiClient.get<PaginatedResponse<YouTubeVideo>>('/videos/', {
    params,
  });
  return response.data;
};
