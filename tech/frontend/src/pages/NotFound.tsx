import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>404</h1>
      <p style={styles.description}>Page Not Found</p>
      <Link to="/" style={styles.link}>
        Go Home
      </Link>
    </div>
  );
}

const styles = {
  container: {
    textAlign: 'center' as const,
    padding: '4rem 1rem',
  },
  title: {
    fontSize: '6rem',
    margin: '0',
    color: '#646cff',
  },
  description: {
    fontSize: '1.5rem',
    color: '#888',
    marginBottom: '2rem',
  },
  link: {
    display: 'inline-block',
    padding: '0.75rem 2rem',
    backgroundColor: '#646cff',
    color: '#fff',
    textDecoration: 'none',
    borderRadius: '8px',
    fontSize: '1.1rem',
  },
};
