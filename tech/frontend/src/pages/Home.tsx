import { Link } from 'react-router-dom';
import { env } from '@/config/env';

export default function Home() {
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>{env.serviceName}</h1>
      <p style={styles.description}>
        YouTube 채널 및 인기 급상승 영상 관리 시스템
      </p>

      <div style={styles.features}>
        <div style={styles.card}>
          <h3>⚛️ React 19</h3>
          <p>Latest version of React with modern features</p>
        </div>
        <div style={styles.card}>
          <h3>⚡ Vite</h3>
          <p>Lightning fast HMR and build times</p>
        </div>
        <div style={styles.card}>
          <h3>📘 TypeScript</h3>
          <p>Type-safe development experience</p>
        </div>
        <div style={styles.card}>
          <h3>🔒 JWT Auth</h3>
          <p>Secure authentication with JWT tokens</p>
        </div>
        <div style={styles.card}>
          <h3>🐳 Docker</h3>
          <p>Containerized development and deployment</p>
        </div>
        <div style={styles.card}>
          <h3>🎨 Django API</h3>
          <p>RESTful API with Django backend</p>
        </div>
      </div>

      <div style={styles.actions}>
        <Link to="/login" style={styles.button}>
          Get Started
        </Link>
      </div>
    </div>
  );
}

const styles = {
  container: {
    textAlign: 'center' as const,
  },
  title: {
    fontSize: '3rem',
    marginBottom: '1rem',
    background: 'linear-gradient(to right, #646cff, #747bff)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  description: {
    fontSize: '1.2rem',
    color: '#888',
    marginBottom: '3rem',
  },
  features: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '1.5rem',
    marginBottom: '3rem',
  },
  card: {
    padding: '2rem',
    backgroundColor: '#1a1a1a',
    borderRadius: '8px',
    border: '1px solid #333',
  },
  actions: {
    marginTop: '2rem',
  },
  button: {
    display: 'inline-block',
    padding: '0.75rem 2rem',
    backgroundColor: '#646cff',
    color: '#fff',
    textDecoration: 'none',
    borderRadius: '8px',
    fontSize: '1.1rem',
    transition: 'background-color 0.2s',
  },
};
