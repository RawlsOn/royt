/**
 * API 응답 및 요청 타입 정의
 */

// 기본 API 응답 타입
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

// 페이지네이션 응답 타입
export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

// 에러 응답 타입
export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}

// JWT 토큰 타입
export interface TokenPair {
  access: string;
  refresh: string;
}

// 사용자 타입 (예시)
export interface User {
  id: number;
  email: string;
  created_at: string;
  updated_at: string;
}
