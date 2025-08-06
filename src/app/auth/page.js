'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import styles from './auth.module.css';

export default function AuthPage() {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    role: 'Employee'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const modeParam = searchParams.get('mode');
    if (modeParam === 'register' || modeParam === 'login') {
      setMode(modeParam);
    }
  }, [searchParams]);

  useEffect(() => {
    // Check if already authenticated
    const token = localStorage.getItem('token');
    if (token) {
      router.push('/employee');
    }
  }, [router]);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const endpoint = mode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const payload = mode === 'login' 
        ? { email: formData.email, password: formData.password }
        : formData;

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        if (mode === 'login') {
          localStorage.setItem('token', data.token);
          localStorage.setItem('user', JSON.stringify({
            employee_id: data.employee_id,
            name: data.name,
            email: data.email,
            role: data.role
          }));
          router.push('/employee');
        } else {
          setSuccess('Registration successful! Please login.');
          setMode('login');
          setFormData({
            email: formData.email,
            password: '',
            name: '',
            role: 'Employee'
          });
        }
      } else {
        setError(data.detail || 'Authentication failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    setError('');
    setSuccess('');
    setFormData({
      email: '',
      password: '',
      name: '',
      role: 'Employee'
    });
  };

  return (
    <div className={styles.container}>
      <div className={styles.authCard}>
        <div className={styles.header}>
          <h1 className={styles.title}>
            {mode === 'login' ? 'Welcome Back' : 'Create Account'}
          </h1>
          <p className={styles.subtitle}>
            {mode === 'login' 
              ? 'Sign in to your employee account' 
              : 'Join the employee management system'
            }
          </p>
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className={styles.form}>
          {mode === 'register' && (
            <div className="form-group">
              <label htmlFor="name" className="form-label">Full Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className="input"
                required
                placeholder="Enter your full name"
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email" className="form-label">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className="input"
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              className="input"
              required
              placeholder="Enter your password"
              minLength={6}
            />
          </div>

          {mode === 'register' && (
            <div className="form-group">
              <label htmlFor="role" className="form-label">Role</label>
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleInputChange}
                className="select"
              >
                <option value="Employee">Employee</option>
                <option value="Manager">Manager</option>
              </select>
            </div>
          )}

          <button
            type="submit"
            className="button button-primary"
            style={{ width: '100%' }}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="loading"></span>
                {mode === 'login' ? 'Signing In...' : 'Creating Account...'}
              </>
            ) : (
              mode === 'login' ? 'Sign In' : 'Create Account'
            )}
          </button>
        </form>

        <div className={styles.switchMode}>
          <p>
            {mode === 'login' ? "Don't have an account?" : "Already have an account?"}
            {' '}
            <button
              type="button"
              onClick={toggleMode}
              className={styles.switchButton}
            >
              {mode === 'login' ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>

        <div className={styles.backHome}>
          <button
            type="button"
            onClick={() => router.push('/')}
            className="button button-secondary"
            style={{ width: '100%' }}
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}