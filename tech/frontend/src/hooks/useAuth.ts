import { tokenStorage } from '@/api';

/**
 * 인증 상태를 확인하는 훅
 */
export function useAuth() {
  const isAuthenticated = !!tokenStorage.getAccessToken();

  return {
    isAuthenticated,
  };
}
