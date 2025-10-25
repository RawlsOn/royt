import { create } from 'zustand';
import { getYouTubeVideos } from '@/api/youtube';
import type { YouTubeVideo } from '@/types/youtube';

interface VideoListState {
  // 영상 리스트 데이터
  videos: YouTubeVideo[];
  totalCount: number;

  // 페이지네이션 상태
  page: number;
  pageSize: number;

  // 정렬 상태
  ordering: string;

  // 로딩 및 에러 상태
  isLoading: boolean;
  error: string | null;

  // 액션
  fetchVideos: () => Promise<void>;
  setSorting: (field: string) => void;
  setPage: (page: number) => void;
  resetFilters: () => void;
}

export const useVideoListStore = create<VideoListState>((set, get) => ({
  // 초기 상태
  videos: [],
  totalCount: 0,
  page: 1,
  pageSize: 20,
  ordering: '-view_count',
  isLoading: false,
  error: null,

  // 영상 리스트 조회
  fetchVideos: async () => {
    const state = get();

    // API 호출 중복 방지
    if (state.isLoading) {
      return;
    }

    set({ isLoading: true, error: null });

    try {
      const response = await getYouTubeVideos({
        ordering: state.ordering,
        page: state.page,
        page_size: state.pageSize,
      });

      set({
        videos: response.results,
        totalCount: response.count,
        isLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '영상 리스트를 불러오는데 실패했습니다.',
        isLoading: false,
      });
    }
  },

  // 정렬 변경 (페이지 1로 리셋)
  setSorting: (field: string) => {
    set({ ordering: field, page: 1 });
    // 정렬 변경 후 자동으로 데이터 다시 가져오기
    get().fetchVideos();
  },

  // 페이지 변경
  setPage: (page: number) => {
    set({ page });
    // 페이지 변경 후 자동으로 데이터 다시 가져오기
    get().fetchVideos();
  },

  // 필터 초기화
  resetFilters: () => {
    set({
      page: 1,
      pageSize: 20,
      ordering: '-view_count',
      videos: [],
      totalCount: 0,
      error: null,
    });
  },
}));
