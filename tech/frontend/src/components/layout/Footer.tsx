export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer style={styles.footer}>
      <div style={styles.container}>
        <p style={styles.text}>
          &copy; {currentYear} Royt. All rights reserved.
        </p>
        <p style={styles.text}>
          Built with React + Vite + TypeScript
        </p>
      </div>
    </footer>
  );
}

const styles = {
  footer: {
    backgroundColor: '#1a1a1a',
    padding: '2rem 0',
    marginTop: 'auto',
    borderTop: '1px solid #333',
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 1rem',
    textAlign: 'center' as const,
  },
  text: {
    color: '#888',
    margin: '0.5rem 0',
    fontSize: '0.9rem',
  },
};
