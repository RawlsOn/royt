import { useState } from 'react';
import {
  Box,
  Button,
  Chip,
  Paper,
  Stack,
  TextField,
  Typography,
  Toolbar,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Clear as ClearIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useHomeStore } from '@/store/homeStore';

export default function KeywordInput() {
  const { keywords, addKeyword, removeKeyword, setKeywords } = useHomeStore();
  const [newKeyword, setNewKeyword] = useState('');

  const handleAddKeyword = () => {
    if (newKeyword.trim() && !keywords.includes(newKeyword.trim())) {
      addKeyword(newKeyword.trim());
      setNewKeyword('');
    }
  };

  const handleClearAll = () => {
    if (window.confirm('모든 키워드를 삭제하시겠습니까?')) {
      setKeywords([]);
    }
  };

  const handleExport = () => {
    const text = keywords.join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'keywords.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result as string;
        const importedKeywords = text
          .split('\n')
          .map((k) => k.trim())
          .filter((k) => k);
        setKeywords([...new Set([...keywords, ...importedKeywords])]);
      };
      reader.readAsText(file);
    }
  };

  return (
    <Box>
      <Toolbar sx={{ pl: { sm: 2 }, pr: { xs: 1, sm: 1 }, mb: 2 }}>
        <Typography variant="h6" component="div" sx={{ flex: '1 1 100%' }}>
          키워드 입력
        </Typography>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<UploadIcon />}
            component="label"
          >
            가져오기
            <input
              type="file"
              hidden
              accept=".txt"
              onChange={handleImport}
            />
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleExport}
            disabled={keywords.length === 0}
          >
            내보내기
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<ClearIcon />}
            onClick={handleClearAll}
            disabled={keywords.length === 0}
          >
            전체 삭제
          </Button>
        </Stack>
      </Toolbar>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          키워드 추가
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <TextField
            fullWidth
            size="small"
            label="키워드"
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleAddKeyword();
              }
            }}
            placeholder="검색할 키워드를 입력하세요"
            helperText="Enter 키를 눌러 추가하거나 추가 버튼을 클릭하세요"
          />
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddKeyword}
            sx={{ minWidth: 100 }}
          >
            추가
          </Button>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              mb: 2,
            }}
          >
            <Typography variant="subtitle1">
              등록된 키워드 ({keywords.length})
            </Typography>
          </Box>

          {keywords.length === 0 ? (
            <Paper
              variant="outlined"
              sx={{
                p: 4,
                textAlign: 'center',
                bgcolor: 'background.default',
              }}
            >
              <Typography color="text.secondary">
                키워드를 추가하거나 파일을 가져오세요
              </Typography>
            </Paper>
          ) : (
            <Paper
              variant="outlined"
              sx={{
                p: 2,
                minHeight: 200,
                maxHeight: 400,
                overflow: 'auto',
                bgcolor: 'background.default',
              }}
            >
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {keywords.map((keyword) => (
                  <Chip
                    key={keyword}
                    label={keyword}
                    onDelete={() => removeKeyword(keyword)}
                    color="primary"
                    variant="outlined"
                    sx={{ mb: 1 }}
                  />
                ))}
              </Stack>
            </Paper>
          )}
        </Box>
      </Paper>

      <Paper sx={{ p: 3, bgcolor: 'info.main', color: 'info.contrastText' }}>
        <Typography variant="subtitle2" gutterBottom>
          💡 사용 팁
        </Typography>
        <Typography variant="body2" component="div">
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            <li>여러 키워드를 추가하여 다양한 검색 결과를 얻을 수 있습니다</li>
            <li>텍스트 파일(.txt)로 키워드를 가져오거나 내보낼 수 있습니다</li>
            <li>중복된 키워드는 자동으로 제거됩니다</li>
            <li>키워드는 OR 조건으로 검색됩니다</li>
          </ul>
        </Typography>
      </Paper>
    </Box>
  );
}
