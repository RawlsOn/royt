import { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Button,
  Stack,
  Box,
  CircularProgress,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  Search as SearchIcon,
  Save as SaveIcon,
  ExitToApp as ExitIcon,
  Settings as SettingsIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material';
import { useHomeStore } from '@/store/homeStore';

interface ActionBarProps {
  onSearch?: () => Promise<void>;
}

export default function ActionBar({ onSearch }: ActionBarProps) {
  const { channels, keywords, setActiveTab, setResults } = useHomeStore();
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'warning' | 'info',
  });

  const handleSearch = async () => {
    // 유효성 검사
    if (channels.length === 0 && keywords.length === 0) {
      setSnackbar({
        open: true,
        message: '채널 또는 키워드를 먼저 설정해주세요',
        severity: 'warning',
      });
      return;
    }

    setLoading(true);
    try {
      if (onSearch) {
        await onSearch();
      } else {
        // 임시 Mock 데이터 생성
        const mockResults = Array.from({ length: 20 }, (_, i) => ({
          id: `video-${i}`,
          publishedAt: new Date(
            Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000
          ).toISOString(),
          title: `샘플 영상 제목 ${i + 1} - 유튜브 핫튜브 테스트`,
          channelTitle: `채널 ${i % 5 + 1}`,
          viewCount: Math.floor(Math.random() * 1000000),
          likeCount: Math.floor(Math.random() * 50000),
          subscriberCount: Math.floor(Math.random() * 500000),
          rank: i + 1,
          viewsPerHour: Math.random() * 1000,
          thumbnail: '',
          videoId: `test-video-${i}`,
        }));

        setResults(mockResults);
      }

      setSnackbar({
        open: true,
        message: '검색이 완료되었습니다',
        severity: 'success',
      });

      // 결과 탭으로 자동 이동
      setActiveTab('results');
    } catch (error) {
      setSnackbar({
        open: true,
        message: '검색 중 오류가 발생했습니다',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = () => {
    setSnackbar({
      open: true,
      message: '설정이 저장되었습니다',
      severity: 'success',
    });
  };

  const handleExport = () => {
    setSnackbar({
      open: true,
      message: '데이터를 내보냈습니다',
      severity: 'success',
    });
  };

  const handleManageSettings = () => {
    setActiveTab('settings');
  };

  const handleExit = () => {
    if (window.confirm('정말 종료하시겠습니까?')) {
      // TODO: 로그아웃 처리
      window.location.href = '/login';
    }
  };

  return (
    <>
      <AppBar
        position="fixed"
        color="default"
        sx={{
          top: 'auto',
          bottom: 0,
          borderTop: 1,
          borderColor: 'divider',
          bgcolor: 'background.paper',
        }}
      >
        <Toolbar>
          <Box sx={{ flexGrow: 1 }}>
            <Stack direction="row" spacing={1}>
              <Button
                variant="contained"
                color="primary"
                size="large"
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
                onClick={handleSearch}
                disabled={loading}
                sx={{ minWidth: 120 }}
              >
                {loading ? '검색 중...' : '검색 실행'}
              </Button>

              <Button
                variant="outlined"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={loading}
              >
                글로 저장
              </Button>

              <Button
                variant="outlined"
                startIcon={<DescriptionIcon />}
                onClick={handleExport}
                disabled={loading}
              >
                세부내역 저장
              </Button>
            </Stack>
          </Box>

          <Stack direction="row" spacing={1}>
            <Button
              variant="outlined"
              startIcon={<SettingsIcon />}
              onClick={handleManageSettings}
              disabled={loading}
            >
              계열코드 관리
            </Button>

            <Button
              variant="outlined"
              color="error"
              startIcon={<ExitIcon />}
              onClick={handleExit}
              disabled={loading}
            >
              프로그램 종료
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>

      {/* 하단 액션바 공간 확보용 */}
      <Toolbar />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
}
