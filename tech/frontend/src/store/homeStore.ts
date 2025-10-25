import { create } from 'zustand';

export type TabType = 'channels' | 'keywords' | 'settings' | 'results';

interface HomeState {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;

  // 채널 목록 데이터
  channels: any[];
  setChannels: (channels: any[]) => void;

  // 키워드 데이터
  keywords: string[];
  addKeyword: (keyword: string) => void;
  removeKeyword: (keyword: string) => void;
  setKeywords: (keywords: string[]) => void;

  // 설정 데이터
  settings: {
    sortBy: 'newest' | 'views' | 'subscribers';
    daysFilter: number;
    minViews: number;
    minViewsPerHour: number;
    maxViews: number;
    apiKeyWaitTime: number;
    showWaitNotification: boolean;
    language: string;
    region: string;
  };
  updateSettings: (settings: Partial<HomeState['settings']>) => void;

  // 검색 결과 데이터
  results: any[];
  setResults: (results: any[]) => void;
}

export const useHomeStore = create<HomeState>((set) => ({
  activeTab: 'channels',
  setActiveTab: (tab) => set({ activeTab: tab }),

  channels: [],
  setChannels: (channels) => set({ channels }),

  keywords: [],
  addKeyword: (keyword) => set((state) => ({
    keywords: [...state.keywords, keyword]
  })),
  removeKeyword: (keyword) => set((state) => ({
    keywords: state.keywords.filter(k => k !== keyword)
  })),
  setKeywords: (keywords) => set({ keywords }),

  settings: {
    sortBy: 'newest',
    daysFilter: 10,
    minViews: 0,
    minViewsPerHour: 600,
    maxViews: 20000,
    apiKeyWaitTime: 30,
    showWaitNotification: false,
    language: 'ko',
    region: 'KR',
  },
  updateSettings: (newSettings) => set((state) => ({
    settings: { ...state.settings, ...newSettings }
  })),

  results: [],
  setResults: (results) => set({ results }),
}));
