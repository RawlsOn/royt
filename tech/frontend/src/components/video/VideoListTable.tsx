import { useEffect, useMemo } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Typography,
  Link,
  Skeleton,
  Alert,
} from '@mui/material';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender,
  createColumnHelper,
  type SortingState,
  type ColumnDef,
} from '@tanstack/react-table';
import { useVideoListStore } from '@/store/videoListStore';
import type { YouTubeVideo } from '@/types/youtube';

const columnHelper = createColumnHelper<YouTubeVideo>();

/**
 * 숫자를 천 단위 구분자로 포맷팅
 */
const formatNumber = (num: number): string => {
  return num.toLocaleString('ko-KR');
};

/**
 * 날짜를 YYYY-MM-DD 형식으로 포맷팅
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
};

/**
 * 퍼센트를 소수점 2자리로 포맷팅
 */
const formatPercent = (num: number): string => {
  return `${num.toFixed(2)}%`;
};

/**
 * YouTube 영상 리스트 테이블 컴포넌트
 */
export default function VideoListTable() {
  const { videos, isLoading, error, ordering, setSorting, fetchVideos } =
    useVideoListStore();

  // 컴포넌트 마운트 시 데이터 로드
  useEffect(() => {
    fetchVideos();
  }, [fetchVideos]);

  // 컬럼 정의
  const columns = useMemo<ColumnDef<YouTubeVideo, any>[]>(
    () => [
      columnHelper.display({
        id: 'thumbnail',
        header: '썸네일',
        cell: (info) => (
          <Box
            component="img"
            src={info.row.original.thumbnail_url}
            alt={info.row.original.title}
            loading="lazy"
            sx={{
              width: 120,
              height: 68,
              objectFit: 'cover',
              borderRadius: 1,
            }}
          />
        ),
        enableSorting: false,
      }),
      columnHelper.accessor('title', {
        header: '제목',
        cell: (info) => (
          <Link
            href={info.row.original.youtube_url}
            target="_blank"
            rel="noopener noreferrer"
            underline="hover"
            sx={{
              display: 'block',
              maxWidth: 300,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {info.getValue()}
          </Link>
        ),
        enableSorting: false,
      }),
      columnHelper.accessor('channel_data.channel_title', {
        header: '채널',
        cell: (info) => info.getValue(),
        enableSorting: false,
      }),
      columnHelper.accessor('view_count', {
        header: '조회수',
        cell: (info) => formatNumber(info.getValue()),
        enableSorting: true,
      }),
      columnHelper.accessor('like_count', {
        header: '좋아요',
        cell: (info) => formatNumber(info.getValue()),
        enableSorting: true,
      }),
      columnHelper.accessor('comment_count', {
        header: '댓글',
        cell: (info) => formatNumber(info.getValue()),
        enableSorting: true,
      }),
      columnHelper.accessor('engagement_rate', {
        header: '참여율',
        cell: (info) => formatPercent(info.getValue()),
        enableSorting: true,
      }),
      columnHelper.accessor('views_per_subscriber', {
        header: '구독자당 조회수',
        cell: (info) => formatNumber(info.getValue()),
        enableSorting: true,
      }),
      columnHelper.accessor('published_at', {
        header: '게시일',
        cell: (info) => formatDate(info.getValue()),
        enableSorting: true,
      }),
    ],
    []
  );

  // 현재 정렬 상태를 tanstack table 형식으로 변환
  const sorting = useMemo<SortingState>(() => {
    if (!ordering) return [];

    const isDescending = ordering.startsWith('-');
    const field = isDescending ? ordering.slice(1) : ordering;

    return [
      {
        id: field,
        desc: isDescending,
      },
    ];
  }, [ordering]);

  // 테이블 인스턴스 생성
  const table = useReactTable({
    data: videos,
    columns,
    state: {
      sorting,
    },
    onSortingChange: (updaterOrValue) => {
      const newSorting =
        typeof updaterOrValue === 'function'
          ? updaterOrValue(sorting)
          : updaterOrValue;

      if (newSorting.length > 0) {
        const { id, desc } = newSorting[0];
        const newOrdering = desc ? `-${id}` : id;
        setSorting(newOrdering);
      }
    },
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    manualSorting: true, // 서버 사이드 정렬 사용
  });

  // 로딩 상태
  if (isLoading && videos.length === 0) {
    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              {columns.map((_, index) => (
                <TableCell key={index}>
                  <Skeleton />
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {[...Array(5)].map((_, rowIndex) => (
              <TableRow key={rowIndex}>
                {columns.map((_, cellIndex) => (
                  <TableCell key={cellIndex}>
                    <Skeleton />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  // 에러 상태
  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  // 빈 데이터 상태
  if (!isLoading && videos.length === 0) {
    return (
      <TableContainer component={Paper}>
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            표시할 영상이 없습니다.
          </Typography>
        </Box>
      </TableContainer>
    );
  }

  // 테이블 렌더링
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                const canSort = header.column.getCanSort();
                const sortDirection = header.column.getIsSorted();

                return (
                  <TableCell
                    key={header.id}
                    align={
                      header.id === 'thumbnail' || header.id === 'title'
                        ? 'left'
                        : 'right'
                    }
                  >
                    {canSort ? (
                      <TableSortLabel
                        active={!!sortDirection}
                        direction={sortDirection || 'asc'}
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                      </TableSortLabel>
                    ) : (
                      flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )
                    )}
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
        </TableHead>
        <TableBody>
          {table.getRowModel().rows.map((row) => (
            <TableRow key={row.id} hover>
              {row.getVisibleCells().map((cell) => (
                <TableCell
                  key={cell.id}
                  align={
                    cell.column.id === 'thumbnail' || cell.column.id === 'title'
                      ? 'left'
                      : 'right'
                  }
                >
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
