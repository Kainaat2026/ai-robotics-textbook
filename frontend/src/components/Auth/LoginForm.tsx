/**
 * LoginForm Component
 *
 * User login form with email and password validation.
 */

import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import styles from './AuthForms.module.css';

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToSignup?: () => void;
}

export default function LoginForm({
  onSuccess,
  onSwitchToSignup,
}: LoginFormProps): JSX.Element {
  const { login, loading, error } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    // Validation
    if (!email || !password) {
      setLocalError('Please enter both email and password');
      return;
    }

    try {
      await login(email, password);
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      // Error is already set in context
    }
  };

  return (
    <div className={styles.authFormContainer}>
      <div className={styles.authFormCard}>
        <h2 className={styles.authFormTitle}>Login</h2>
        <p className={styles.authFormSubtitle}>
          Welcome back! Please login to continue.
        </p>

        <form onSubmit={handleSubmit} className={styles.authForm}>
          {/* Email Input */}
          <div className={styles.formGroup}>
            <label htmlFor="email" className={styles.formLabel}>
              Email
            </label>
            <input
              type="email"
              id="email"
              className={styles.formInput}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@example.com"
              required
              autoComplete="email"
              disabled={loading}
            />
          </div>

          {/* Password Input */}
          <div className={styles.formGroup}>
            <label htmlFor="password" className={styles.formLabel}>
              Password
            </label>
            <input
              type="password"
              id="password"
              className={styles.formInput}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              autoComplete="current-password"
              disabled={loading}
            />
          </div>

          {/* Error Message */}
          {(error || localError) && (
            <div className={styles.errorMessage}>
              {error || localError}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className={styles.submitButton}
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        {/* Switch to Signup */}
        {onSwitchToSignup && (
          <p className={styles.switchForm}>
            Don't have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToSignup}
              className={styles.switchFormLink}
            >
              Sign up
            </button>
          </p>
        )}
      </div>
    </div>
  );
}
