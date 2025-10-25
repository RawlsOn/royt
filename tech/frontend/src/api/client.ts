/**
 * Axios 클라이언트 설정
 * API 호출을 위한 기본 설정 및 인터셉터
 */

import axios from 'axios';
import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { env } from '../config/env';
import type { ApiError } from '../types/api';

// Axios 인스턴스 생성
const apiClient: AxiosInstance = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 토큰 저장소 (localStorage 사용)
export const tokenStorage = {
  getAccessToken: (): string | null => {
    return localStorage.getItem('access_token');
  },
  setAccessToken: (token: string): void => {
    localStorage.setItem('access_token', token);
  },
  getRefreshToken: (): string | null => {
    return localStorage.getItem('refresh_token');
  },
  setRefreshToken: (token: string): void => {
    localStorage.setItem('refresh_token', token);
  },
  clearTokens: (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

// 요청 인터셉터: 모든 요청에 JWT 토큰 추가
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = tokenStorage.getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터: 에러 처리 및 토큰 갱신
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // 401 에러 (인증 실패) 처리
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = tokenStorage.getRefreshToken();
        if (refreshToken) {
          // 토큰 갱신 시도
          const response = await axios.post(`${env.apiBaseUrl}/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          tokenStorage.setAccessToken(access);

          // 원래 요청 재시도
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access}`;
          }
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // 토큰 갱신 실패 시 로그아웃 처리
        tokenStorage.clearTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // 에러 변환
    const apiError: ApiError = {
      message: error.response?.data?.message || error.message || 'An error occurred',
      status: error.response?.status || 500,
      errors: error.response?.data?.errors,
    };

    return Promise.reject(apiError);
  }
);

export default apiClient;
