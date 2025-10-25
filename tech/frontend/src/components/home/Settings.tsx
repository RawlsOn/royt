import {
  Box,
  Checkbox,
  FormControl,
  FormControlLabel,
  FormGroup,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
  Typography,
  Divider,
} from '@mui/material';
import { useHomeStore } from '@/store/homeStore';

export default function Settings() {
  const { settings, updateSettings } = useHomeStore();

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
        검색 및 필터 설정
      </Typography>

      <Grid container spacing={3}>
        {/* 채널명동명 섹션 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              채널명동명
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>정렬 기준</InputLabel>
              <Select
                value={settings.sortBy}
                label="정렬 기준"
                onChange={(e) =>
                  updateSettings({
                    sortBy: e.target.value as 'newest' | 'views' | 'subscribers',
                  })
                }
              >
                <MenuItem value="newest">최신순</MenuItem>
                <MenuItem value="views">조회수순</MenuItem>
                <MenuItem value="subscribers">구독자순</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              type="number"
              label="최근 N일간의 영상은 보지않기"
              value={settings.daysFilter}
              onChange={(e) =>
                updateSettings({ daysFilter: parseInt(e.target.value) || 0 })
              }
              sx={{ mb: 2 }}
              helperText="지정한 일수 이전의 영상만 검색"
            />

            <TextField
              fullWidth
              type="number"
              label="재생될 최대 검색 수"
              defaultValue={10}
              sx={{ mb: 2 }}
              helperText="최대 검색 결과 개수"
            />

            <TextField
              fullWidth
              type="number"
              label="최소 시간별 조회수"
              value={settings.minViewsPerHour}
              onChange={(e) =>
                updateSettings({
                  minViewsPerHour: parseFloat(e.target.value) || 0,
                })
              }
              sx={{ mb: 2 }}
              helperText="시간당 최소 조회수 (소수점 가능)"
            />
          </Paper>
        </Grid>

        {/* 키워드 입력 섹션 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              키워드 입력
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>조즈/농호</InputLabel>
              <Select defaultValue="all" label="조즈/농호">
                <MenuItem value="all">전체</MenuItem>
                <MenuItem value="short">숏폼</MenuItem>
                <MenuItem value="long">롱폼</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              type="number"
              label="대상국가"
              value={settings.region}
              onChange={(e) => updateSettings({ region: e.target.value })}
              sx={{ mb: 2 }}
              helperText="검색 대상 국가 코드"
            />

            <TextField
              fullWidth
              type="number"
              label="검색영역 최대 검색 수"
              defaultValue={50}
              sx={{ mb: 2 }}
              helperText="검색 영역당 최대 결과 수"
            />

            <FormGroup>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={settings.showWaitNotification}
                    onChange={(e) =>
                      updateSettings({ showWaitNotification: e.target.checked })
                    }
                  />
                }
                label="재생별 업기제 보기"
              />
            </FormGroup>
          </Paper>
        </Grid>

        {/* 설정 섹션 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              설정
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>순공도(조)</InputLabel>
              <Select defaultValue="all" label="순공도(조)">
                <MenuItem value="all">전체</MenuItem>
                <MenuItem value="180">180</MenuItem>
                <MenuItem value="360">360</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              type="number"
              label="언어"
              value={settings.language}
              onChange={(e) => updateSettings({ language: e.target.value })}
              sx={{ mb: 2 }}
              helperText="검색 언어 (예: ko, en)"
            />

            <TextField
              fullWidth
              type="number"
              label="최소 조회수"
              value={settings.minViews}
              onChange={(e) =>
                updateSettings({ minViews: parseInt(e.target.value) || 0 })
              }
              sx={{ mb: 2 }}
              helperText="최소 조회수 필터"
            />

            <TextField
              fullWidth
              type="number"
              label="최대 조회수"
              value={settings.maxViews}
              onChange={(e) =>
                updateSettings({ maxViews: parseInt(e.target.value) || 0 })
              }
              sx={{ mb: 2 }}
              helperText="최대 조회수 필터"
            />
          </Paper>
        </Grid>

        {/* API 설정 */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              API 설정
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="API 키 대기 소요 시 대기시간 (분)"
                  value={settings.apiKeyWaitTime}
                  onChange={(e) =>
                    updateSettings({
                      apiKeyWaitTime: parseInt(e.target.value) || 0,
                    })
                  }
                  helperText="API 키 할당량 초과 시 대기 시간"
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="API 키 대기 상태"
                  defaultValue=""
                  helperText="현재 API 키 상태"
                  InputProps={{
                    readOnly: true,
                  }}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="대기 중일 알림"
                  defaultValue=""
                  helperText="대기 중 알림 설정 (예: 다음 키로 이동)"
                  placeholder="다음 조로 이동"
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* 정보 안내 */}
        <Grid item xs={12}>
          <Paper
            sx={{ p: 3, bgcolor: 'warning.main', color: 'warning.contrastText' }}
          >
            <Typography variant="subtitle2" gutterBottom>
              ⚠️ 설정 안내
            </Typography>
            <Typography variant="body2" component="div">
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                <li>
                  설정은 자동으로 저장되며 다음 검색 시 적용됩니다
                </li>
                <li>
                  API 키 할당량을 초과하면 설정한 시간만큼 대기합니다
                </li>
                <li>
                  필터 설정은 검색 결과에 즉시 반영됩니다
                </li>
                <li>
                  잘못된 설정은 검색 결과에 영향을 줄 수 있으니 주의하세요
                </li>
              </ul>
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
