import { Link } from 'react-router-dom';
import { tokenStorage } from '@/api';

export default function Header() {
  const isAuthenticated = !!tokenStorage.getAccessToken();

  const handleLogout = () => {
    tokenStorage.clearTokens();
    window.location.href = '/login';
  };

  return (
    <header style={styles.header}>
      <div style={styles.container}>
        <Link to="/" style={styles.logo}>
          <h1>Royt</h1>
        </Link>

        <nav style={styles.nav}>
          <Link to="/" style={styles.link}>
            Home
          </Link>

          {isAuthenticated ? (
            <>
              <Link to="/dashboard" style={styles.link}>
                Dashboard
              </Link>
              <button onClick={handleLogout} style={styles.button}>
                Logout
              </button>
            </>
          ) : (
            <Link to="/login" style={styles.link}>
              Login
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}

const styles = {
  header: {
    backgroundColor: '#1a1a1a',
    padding: '1rem 0',
    borderBottom: '1px solid #333',
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 1rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logo: {
    color: '#fff',
    textDecoration: 'none',
  },
  nav: {
    display: 'flex',
    gap: '1.5rem',
    alignItems: 'center',
  },
  link: {
    color: '#fff',
    textDecoration: 'none',
    transition: 'color 0.2s',
  },
  button: {
    background: 'none',
    border: '1px solid #fff',
    color: '#fff',
    padding: '0.5rem 1rem',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
};
