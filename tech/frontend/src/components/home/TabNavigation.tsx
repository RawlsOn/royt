import { Tabs, Tab, Box } from '@mui/material';
import {
  List as ListIcon,
  Search as SearchIcon,
  Settings as SettingsIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { useHomeStore } from '@/store/homeStore';
import type { TabType } from '@/store/homeStore';

const tabs = [
  { value: 'channels' as TabType, label: '채널명동명', icon: <ListIcon /> },
  { value: 'keywords' as TabType, label: '키워드 입력', icon: <SearchIcon /> },
  { value: 'settings' as TabType, label: '설정', icon: <SettingsIcon /> },
  { value: 'results' as TabType, label: '결과', icon: <AssessmentIcon /> },
];

export default function TabNavigation() {
  const { activeTab, setActiveTab } = useHomeStore();

  const handleChange = (_event: React.SyntheticEvent, newValue: TabType) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
      <Tabs
        value={activeTab}
        onChange={handleChange}
        aria-label="home tabs"
        variant="fullWidth"
        sx={{
          '& .MuiTab-root': {
            minHeight: 64,
            fontSize: '1rem',
            fontWeight: 500,
          },
        }}
      >
        {tabs.map((tab) => (
          <Tab
            key={tab.value}
            value={tab.value}
            label={tab.label}
            icon={tab.icon}
            iconPosition="start"
          />
        ))}
      </Tabs>
    </Box>
  );
}
