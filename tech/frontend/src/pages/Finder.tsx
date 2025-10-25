import { Box, Container, Typography, Paper } from '@mui/material';
import { env } from '@/config/env';
import { useHomeStore } from '@/store/homeStore';
import TabNavigation from '@/components/home/TabNavigation';
import ChannelList from '@/components/home/ChannelList';
import KeywordInput from '@/components/home/KeywordInput';
import Settings from '@/components/home/Settings';
import ResultsView from '@/components/home/ResultsView';
import ActionBar from '@/components/home/ActionBar';

export default function Finder() {
  const { activeTab } = useHomeStore();

  const renderTabContent = () => {
    switch (activeTab) {
      case 'channels':
        return <ChannelList />;
      case 'keywords':
        return <KeywordInput />;
      case 'settings':
        return <Settings />;
      case 'results':
        return <ResultsView />;
      default:
        return <ChannelList />;
    }
  };

  return (
    <Box sx={{ pb: 10 }}>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        {/* 헤더 */}
        <Paper
          elevation={0}
          sx={{
            p: 3,
            mb: 3,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
          }}
        >
          <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
            YouTube Hot Finder
          </Typography>
          <Typography variant="subtitle1">
            {env.serviceName} - 유튜브 채널 및 인기 급상승 영상 관리 시스템
          </Typography>
        </Paper>

        {/* 탭 네비게이션 */}
        <TabNavigation />

        {/* 탭 컨텐츠 */}
        <Box sx={{ minHeight: '60vh' }}>{renderTabContent()}</Box>
      </Container>

      {/* 하단 액션 바 */}
      <ActionBar />
    </Box>
  );
}
