'use client';

import { useState, useEffect } from 'react';
import styles from './Dashboard.module.css';

export default function Dashboard({ user }) {
  const [stats, setStats] = useState(null);
  const [recentTasks, setRecentTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };

      // Fetch dashboard stats
      const statsResponse = await fetch('/api/dashboard/stats', { headers });
      const statsData = await statsResponse.json();

      // Fetch tasks (recent ones)
      const tasksResponse = await fetch('/api/tasks', { headers });
      const tasksData = await tasksResponse.json();

      // Fetch projects
      const projectsResponse = await fetch('/api/projects', { headers });
      const projectsData = await projectsResponse.json();

      setStats(statsData);
      setRecentTasks(tasksData.slice(0, 5)); // Show only 5 recent tasks
      setProjects(projectsData);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status.toLowerCase()) {
      case 'completed': return 'badge badge-completed';
      case 'in progress': return 'badge badge-progress';
      case 'pending': return 'badge badge-pending';
      default: return 'badge badge-pending';
    }
  };

  const getPriorityBadgeClass = (priority) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'badge badge-high';
      case 'medium': return 'badge badge-medium';
      case 'low': return 'badge badge-low';
      default: return 'badge badge-medium';
    }
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className="loading"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className={styles.dashboard}>
      <div className={styles.header}>
        <h2>Dashboard Overview</h2>
        <p>Welcome back, {user.name}! Here's what's happening with your work.</p>
      </div>

      {/* Stats Cards */}
      <div className={styles.statsGrid}>
        <div className="stats-card">
          <div className="stats-number">{stats?.total_tasks || 0}</div>
          <div className="stats-label">Total Tasks</div>
        </div>
        <div className="stats-card">
          <div className="stats-number">{stats?.completed_tasks || 0}</div>
          <div className="stats-label">Completed</div>
        </div>
        <div className="stats-card">
          <div className="stats-number">{stats?.pending_tasks || 0}</div>
          <div className="stats-label">Pending</div>
        </div>
        <div className="stats-card">
          <div className="stats-number">{stats?.total_hours || 0}h</div>
          <div className="stats-label">Hours Logged</div>
        </div>
      </div>

      <div className={styles.content}>
        {/* Recent Tasks */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <h3>Recent Tasks</h3>
            <span className={styles.sectionCount}>({recentTasks.length})</span>
          </div>
          
          {recentTasks.length > 0 ? (
            <div className={styles.tasksList}>
              {recentTasks.map(task => (
                <div key={task.task_id} className={styles.taskCard}>
                  <div className={styles.taskHeader}>
                    <h4 className={styles.taskTitle}>{task.title}</h4>
                    <div className={styles.taskBadges}>
                      <span className={getStatusBadgeClass(task.status)}>
                        {task.status}
                      </span>
                      <span className={getPriorityBadgeClass(task.priority)}>
                        {task.priority}
                      </span>
                    </div>
                  </div>
                  <p className={styles.taskDescription}>{task.description}</p>
                  <div className={styles.taskFooter}>
                    <span className={styles.taskTime}>
                      📅 Created: {new Date(task.created_at).toLocaleDateString()}
                    </span>
                    {task.total_hours > 0 && (
                      <span className={styles.taskHours}>
                        ⏱️ {task.total_hours}h logged
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className={styles.emptyState}>
              <p>No tasks found. Start by creating your first task!</p>
            </div>
          )}
        </div>

        {/* Projects Overview */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <h3>Projects</h3>
            <span className={styles.sectionCount}>({projects.length})</span>
          </div>
          
          {projects.length > 0 ? (
            <div className={styles.projectsList}>
              {projects.map(project => (
                <div key={project.project_id} className={styles.projectCard}>
                  <h4 className={styles.projectName}>{project.name}</h4>
                  <p className={styles.projectDescription}>{project.description}</p>
                  <div className={styles.projectFooter}>
                    <span className={styles.projectDate}>
                      📅 Created: {new Date(project.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className={styles.emptyState}>
              <p>
                {user.role === 'Manager' 
                  ? 'No projects yet. Create your first project!' 
                  : 'No projects available yet.'
                }
              </p>
            </div>
          )}
        </div>

        {/* Quick Stats */}
        {stats && (
          <div className={styles.section}>
            <div className={styles.sectionHeader}>
              <h3>Performance Summary</h3>
            </div>
            
            <div className={styles.performanceGrid}>
              <div className={styles.performanceCard}>
                <h4>Completion Rate</h4>
                <div className={styles.progressBar}>
                  <div 
                    className={styles.progressFill}
                    style={{ width: `${stats.completion_rate || 0}%` }}
                  ></div>
                </div>
                <span className={styles.progressText}>{stats.completion_rate || 0}%</span>
              </div>
              
              <div className={styles.performanceCard}>
                <h4>Priority Breakdown</h4>
                <div className={styles.priorityStats}>
                  <div className={styles.priorityItem}>
                    <span className="badge badge-high">High</span>
                    <span>{stats.priority_breakdown?.high || 0}</span>
                  </div>
                  <div className={styles.priorityItem}>
                    <span className="badge badge-medium">Medium</span>
                    <span>{stats.priority_breakdown?.medium || 0}</span>
                  </div>
                  <div className={styles.priorityItem}>
                    <span className="badge badge-low">Low</span>
                    <span>{stats.priority_breakdown?.low || 0}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}