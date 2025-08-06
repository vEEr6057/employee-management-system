'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from './page.module.css';

export default function HomePage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token with backend
      fetch('/api/employees/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Invalid token');
      })
      .then(userData => {
        setIsAuthenticated(true);
        setUser(userData);
      })
      .catch(() => {
        localStorage.removeItem('token');
      })
      .finally(() => {
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, []);

  const handleGetStarted = () => {
    if (isAuthenticated) {
      router.push('/employee');
    } else {
      router.push('/auth');
    }
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className="loading"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <nav className={styles.nav}>
          <h1 className={styles.logo}>EMS</h1>
          <div className={styles.navActions}>
            {isAuthenticated ? (
              <div className={styles.userInfo}>
                <span>Welcome, {user?.name}</span>
                <button 
                  className="button button-primary"
                  onClick={() => router.push('/employee')}
                >
                  Go to Dashboard
                </button>
              </div>
            ) : (
              <div className={styles.authButtons}>
                <button 
                  className="button button-secondary"
                  onClick={() => router.push('/auth?mode=login')}
                >
                  Login
                </button>
                <button 
                  className="button button-primary"
                  onClick={() => router.push('/auth?mode=register')}
                >
                  Register
                </button>
              </div>
            )}
          </div>
        </nav>
      </header>

      <main className={styles.main}>
        <section className={styles.hero}>
          <div className={styles.heroContent}>
            <h1 className={styles.heroTitle}>
              Employee Management System
            </h1>
            <p className={styles.heroDescription}>
              Comprehensive task management, time tracking, and project organization 
              for teams of all sizes. Streamline your workflow with powerful analytics 
              and role-based access control.
            </p>
            <button 
              className={`button button-primary ${styles.ctaButton}`}
              onClick={handleGetStarted}
            >
              {isAuthenticated ? 'Go to Dashboard' : 'Get Started'}
            </button>
          </div>
          <div className={styles.heroImage}>
            <div className={styles.mockupCard}>
              <div className={styles.mockupHeader}>
                <div className={styles.mockupDots}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
              <div className={styles.mockupContent}>
                <div className={styles.mockupRow}>
                  <div className={styles.mockupIcon}></div>
                  <div className={styles.mockupText}>
                    <div className={styles.mockupTitle}></div>
                    <div className={styles.mockupDesc}></div>
                  </div>
                </div>
                <div className={styles.mockupRow}>
                  <div className={styles.mockupIcon}></div>
                  <div className={styles.mockupText}>
                    <div className={styles.mockupTitle}></div>
                    <div className={styles.mockupDesc}></div>
                  </div>
                </div>
                <div className={styles.mockupRow}>
                  <div className={styles.mockupIcon}></div>
                  <div className={styles.mockupText}>
                    <div className={styles.mockupTitle}></div>
                    <div className={styles.mockupDesc}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.features}>
          <div className="container">
            <h2 className={styles.featuresTitle}>Key Features</h2>
            <div className={styles.featuresGrid}>
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>📋</div>
                <h3>Task Management</h3>
                <p>Create, assign, and track tasks with priority levels and status updates. Keep your team organized and productive.</p>
              </div>
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>⏱️</div>
                <h3>Time Tracking</h3>
                <p>Log time spent on tasks with detailed descriptions. Get insights into productivity and project costs.</p>
              </div>
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>📊</div>
                <h3>Project Management</h3>
                <p>Organize tasks into projects with comprehensive analytics and progress tracking.</p>
              </div>
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>👥</div>
                <h3>Role-based Access</h3>
                <p>Manager and Employee roles with appropriate permissions and access controls.</p>
              </div>
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>📈</div>
                <h3>Analytics Dashboard</h3>
                <p>Visual insights into task completion, time tracking, and team performance metrics.</p>
              </div>
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>🔐</div>
                <h3>Secure Authentication</h3>
                <p>JWT-based authentication with secure password hashing and token management.</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className={styles.footer}>
        <div className="container">
          <p>&copy; 2024 Employee Management System. Built with Next.js and FastAPI.</p>
        </div>
      </footer>
    </div>
  );
}