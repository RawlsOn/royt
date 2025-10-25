import { useState } from 'react';
import {
  Box,
  Button,
  Checkbox,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Toolbar,
  Typography,
  Stack,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useHomeStore } from '@/store/homeStore';
import * as XLSX from 'xlsx';

interface Channel {
  id: string;
  name: string;
  subscribers: number;
  videoCount: number;
  selected?: boolean;
}

export default function ChannelList() {
  const { channels, setChannels } = useHomeStore();
  const [newChannelName, setNewChannelName] = useState('');

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newChannels = channels.map((channel) => ({
      ...channel,
      selected: event.target.checked,
    }));
    setChannels(newChannels);
  };

  const handleSelectOne = (id: string) => {
    const newChannels = channels.map((channel) =>
      channel.id === id ? { ...channel, selected: !channel.selected } : channel
    );
    setChannels(newChannels);
  };

  const handleAddChannel = () => {
    if (newChannelName.trim()) {
      const newChannel: Channel = {
        id: Date.now().toString(),
        name: newChannelName.trim(),
        subscribers: 0,
        videoCount: 0,
        selected: false,
      };
      setChannels([...channels, newChannel]);
      setNewChannelName('');
    }
  };

  const handleDeleteSelected = () => {
    const newChannels = channels.filter((channel) => !channel.selected);
    setChannels(newChannels);
  };

  const handleExport = () => {
    const ws = XLSX.utils.json_to_sheet(channels);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Channels');
    XLSX.writeFile(wb, 'channels.xlsx');
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const data = e.target?.result;
        const workbook = XLSX.read(data, { type: 'binary' });
        const sheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(sheet);
        setChannels(
          jsonData.map((row: any) => ({
            id: row.id || Date.now().toString(),
            name: row.name || '',
            subscribers: row.subscribers || 0,
            videoCount: row.videoCount || 0,
            selected: false,
          }))
        );
      };
      reader.readAsBinaryString(file);
    }
  };

  const selectedCount = channels.filter((c) => c.selected).length;
  const allSelected = channels.length > 0 && selectedCount === channels.length;
  const someSelected = selectedCount > 0 && selectedCount < channels.length;

  return (
    <Box>
      <Toolbar sx={{ pl: { sm: 2 }, pr: { xs: 1, sm: 1 }, mb: 2 }}>
        <Typography variant="h6" component="div" sx={{ flex: '1 1 100%' }}>
          채널 목록
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
              accept=".xlsx,.xls"
              onChange={handleImport}
            />
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleExport}
            disabled={channels.length === 0}
          >
            내보내기
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleDeleteSelected}
            disabled={selectedCount === 0}
          >
            삭제 ({selectedCount})
          </Button>
        </Stack>
      </Toolbar>

      <Box sx={{ mb: 2, display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          size="small"
          label="채널명"
          value={newChannelName}
          onChange={(e) => setNewChannelName(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleAddChannel();
            }
          }}
          placeholder="채널명을 입력하세요"
        />
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddChannel}
          sx={{ minWidth: 100 }}
        >
          추가
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={someSelected}
                  checked={allSelected}
                  onChange={handleSelectAll}
                />
              </TableCell>
              <TableCell>채널명</TableCell>
              <TableCell align="right">구독자수</TableCell>
              <TableCell align="right">영상수</TableCell>
              <TableCell align="center">작업</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {channels.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">
                    채널을 추가하거나 파일을 가져오세요
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              channels.map((channel) => (
                <TableRow
                  key={channel.id}
                  hover
                  selected={channel.selected}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={channel.selected || false}
                      onChange={() => handleSelectOne(channel.id)}
                    />
                  </TableCell>
                  <TableCell>{channel.name}</TableCell>
                  <TableCell align="right">
                    {channel.subscribers.toLocaleString()}
                  </TableCell>
                  <TableCell align="right">
                    {channel.videoCount.toLocaleString()}
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => {
                        setChannels(channels.filter((c) => c.id !== channel.id));
                      }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
