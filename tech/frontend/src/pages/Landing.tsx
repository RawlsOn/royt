import { Box, Container, Typography } from '@mui/material';
import { env } from '@/config/env';

export default function Landing() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="md">
        <Typography
          variant="h1"
          component="h1"
          align="center"
          sx={{
            color: 'white',
            fontWeight: 'bold',
            fontSize: { xs: '3rem', sm: '4rem', md: '6rem' },
            textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
          }}
        >
          {env.serviceName}
        </Typography>
      </Container>
    </Box>
  );
}
