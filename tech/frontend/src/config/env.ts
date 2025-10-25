/**
 * 환경변수 설정
 * Vite는 VITE_ 접두사가 있는 환경변수만 노출합니다.
 */

interface EnvConfig {
  apiBaseUrl: string;
  env: string;
  serviceName: string;
}

export const env: EnvConfig = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5100/api',
  env: import.meta.env.VITE_ENV || 'local',
  serviceName: import.meta.env.VITE_SERVICE_NAME || 'Royt',
};

// 개발 모드에서 환경변수 로깅
if (import.meta.env.DEV) {
  console.log('Environment Config:', env);
}
