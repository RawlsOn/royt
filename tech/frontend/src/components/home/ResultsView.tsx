import { useMemo, useState } from 'react';
import {
  Box,
  Button,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Toolbar,
  Typography,
  Chip,
  IconButton,
  Link,
} from '@mui/material';
import {
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  OpenInNew as OpenInNewIcon,
} from '@mui/icons-material';
import { useHomeStore } from '@/store/homeStore';
import * as XLSX from 'xlsx';

interface VideoResult {
  id: string;
  publishedAt: string;
  title: string;
  channelTitle: string;
  viewCount: number;
  likeCount: number;
  subscriberCount: number;
  rank?: number;
  viewsPerHour: number;
  thumbnail: string;
  videoId: string;
}

type SortField = 'publishedAt' | 'viewCount' | 'likeCount' | 'subscriberCount' | 'viewsPerHour';
type SortDirection = 'asc' | 'desc';

export default function ResultsView() {
  const { results, setResults } = useHomeStore();
  const [sortField, setSortField] = useState<SortField>('publishedAt');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const handleSort = (field: SortField) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    setSortDirection(isAsc ? 'desc' : 'asc');
    setSortField(field);
  };

  const sortedResults = useMemo(() => {
    if (results.length === 0) return [];

    const sorted = [...results].sort((a, b) => {
      const aValue = a[sortField] || 0;
      const bValue = b[sortField] || 0;

      if (sortField === 'publishedAt') {
        return sortDirection === 'asc'
          ? new Date(aValue).getTime() - new Date(bValue).getTime()
          : new Date(bValue).getTime() - new Date(aValue).getTime();
      }

      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    });

    return sorted;
  }, [results, sortField, sortDirection]);

  const handleExport = () => {
    const exportData = sortedResults.map((result) => ({
      작성일: new Date(result.publishedAt).toLocaleString('ko-KR'),
      제목: result.title,
      채널명: result.channelTitle,
      조회수: result.viewCount,
      좋아요수: result.likeCount,
      구독자수: result.subscriberCount,
      '시간당 조회수': result.viewsPerHour?.toFixed(2) || 0,
      순위: result.rank || '-',
      'Video ID': result.videoId,
    }));

    const ws = XLSX.utils.json_to_sheet(exportData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Results');
    XLSX.writeFile(wb, `youtube_results_${Date.now()}.xlsx`);
  };

  const handleRefresh = () => {
    // TODO: API 호출하여 결과 갱신
    console.log('Refreshing results...');
  };

  const formatNumber = (num: number) => {
    return num?.toLocaleString('ko-KR') || '0';
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Box>
      <Toolbar sx={{ pl: { sm: 2 }, pr: { xs: 1, sm: 1 }, mb: 2 }}>
        <Typography variant="h6" component="div" sx={{ flex: '1 1 100%' }}>
          검색 결과 ({results.length})
        </Typography>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
          >
            새로고침
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleExport}
            disabled={results.length === 0}
          >
            엑셀 다운로드
          </Button>
        </Stack>
      </Toolbar>

      <TableContainer component={Paper}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>순위</TableCell>
              <TableCell>
                <TableSortLabel
                  active={sortField === 'publishedAt'}
                  direction={sortField === 'publishedAt' ? sortDirection : 'asc'}
                  onClick={() => handleSort('publishedAt')}
                >
                  작성일
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ minWidth: 300 }}>제목</TableCell>
              <TableCell>채널명</TableCell>
              <TableCell align="right">
                <TableSortLabel
                  active={sortField === 'viewCount'}
                  direction={sortField === 'viewCount' ? sortDirection : 'asc'}
                  onClick={() => handleSort('viewCount')}
                >
                  조회수
                </TableSortLabel>
              </TableCell>
              <TableCell align="right">
                <TableSortLabel
                  active={sortField === 'likeCount'}
                  direction={sortField === 'likeCount' ? sortDirection : 'asc'}
                  onClick={() => handleSort('likeCount')}
                >
                  좋아요
                </TableSortLabel>
              </TableCell>
              <TableCell align="right">
                <TableSortLabel
                  active={sortField === 'subscriberCount'}
                  direction={sortField === 'subscriberCount' ? sortDirection : 'asc'}
                  onClick={() => handleSort('subscriberCount')}
                >
                  구독자수
                </TableSortLabel>
              </TableCell>
              <TableCell align="right">
                <TableSortLabel
                  active={sortField === 'viewsPerHour'}
                  direction={sortField === 'viewsPerHour' ? sortDirection : 'asc'}
                  onClick={() => handleSort('viewsPerHour')}
                >
                  시간당 조회수
                </TableSortLabel>
              </TableCell>
              <TableCell align="center">링크</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedResults.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} align="center" sx={{ py: 8 }}>
                  <Typography color="text.secondary" variant="h6">
                    검색 결과가 없습니다
                  </Typography>
                  <Typography color="text.secondary" variant="body2" sx={{ mt: 1 }}>
                    채널과 키워드를 설정한 후 하단의 검색 버튼을 눌러주세요
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              sortedResults.map((result, index) => (
                <TableRow key={result.id} hover>
                  <TableCell>
                    <Chip
                      label={result.rank || index + 1}
                      color="primary"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{formatDate(result.publishedAt)}</TableCell>
                  <TableCell>
                    <Typography
                      variant="body2"
                      sx={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                      }}
                    >
                      {result.title}
                    </Typography>
                  </TableCell>
                  <TableCell>{result.channelTitle}</TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      {formatNumber(result.viewCount)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    {formatNumber(result.likeCount)}
                  </TableCell>
                  <TableCell align="right">
                    {formatNumber(result.subscriberCount)}
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="primary" fontWeight="bold">
                      {result.viewsPerHour?.toFixed(2) || '0'}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      component={Link}
                      href={`https://www.youtube.com/watch?v=${result.videoId}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <OpenInNewIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {results.length > 0 && (
        <Paper sx={{ p: 2, mt: 2, bgcolor: 'success.main', color: 'success.contrastText' }}>
          <Typography variant="body2">
            총 {results.length}개의 영상이 검색되었습니다.
            정렬 기준을 변경하거나 엑셀로 다운로드할 수 있습니다.
          </Typography>
        </Paper>
      )}
    </Box>
  );
}
