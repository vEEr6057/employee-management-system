'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import styles from './employee.module.css';

// Sub-components
import Dashboard from './components/Dashboard';
import TaskManagement from './components/TaskManagement';
import ProjectManagement from './components/ProjectManagement';
import TimeTracking from './components/TimeTracking';

export default function EmployeePage() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth');
      return;
    }

    // Verify token and get user info
    fetch('/api/employees/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Invalid token');
      }
      return response.json();
    })
    .then(userData => {
      setUser(userData);
    })
    .catch(() => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      router.push('/auth');
    })
    .finally(() => {
      setLoading(false);
    });
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/');
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className="loading"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'tasks', label: 'Tasks', icon: '📋' },
    { id: 'projects', label: 'Projects', icon: '📁' },
    { id: 'time', label: 'Time Tracking', icon: '⏱️' }
  ];

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.headerLeft}>
            <h1 className={styles.appTitle}>Employee Management System</h1>
            <div className={styles.userInfo}>
              <span className={styles.userName}>Welcome, {user.name}</span>
              <span className={styles.userRole}>
                {user.role === 'Manager' ? '👨‍💼' : '👨‍💻'} {user.role}
              </span>
            </div>
          </div>
          <div className={styles.headerRight}>
            <button
              onClick={() => router.push('/')}
              className="button button-secondary"
            >
              Home
            </button>
            <button
              onClick={handleLogout}
              className="button button-danger"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className={styles.main}>
        <nav className={styles.sidebar}>
          <div className={styles.navTabs}>
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${styles.navTab} ${activeTab === tab.id ? styles.navTabActive : ''}`}
              >
                <span className={styles.tabIcon}>{tab.icon}</span>
                <span className={styles.tabLabel}>{tab.label}</span>
              </button>
            ))}
          </div>
        </nav>

        <div className={styles.content}>
          {activeTab === 'dashboard' && <Dashboard user={user} />}
          {activeTab === 'tasks' && <TaskManagement user={user} />}
          {activeTab === 'projects' && <ProjectManagement user={user} />}
          {activeTab === 'time' && <TimeTracking user={user} />}
        </div>
      </div>
    </div>
  );
}