/**
 * Signin Form
 * Login form for existing users
 */
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import styles from './AuthForms.module.css';

export default function SigninForm({ onSuccess, onSwitchToSignup }) {
  const { login, error, clearError } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [localError, setLocalError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');
    clearError();

    setIsLoading(true);
    const result = await login({ email, password });
    setIsLoading(false);

    if (result.success) {
      onSuccess?.();
    } else {
      setLocalError(result.error);
    }
  };

  const displayError = localError || error;

  return (
    <div className={styles.formContainer}>
      <h2 className={styles.title}>Welcome Back</h2>
      <p className={styles.subtitle}>
        Sign in to continue your learning journey
      </p>

      {displayError && (
        <div className={styles.error}>{displayError}</div>
      )}

      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.fieldGroup}>
          <label htmlFor="email" className={styles.label}>Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={styles.input}
            placeholder="your@email.com"
            required
          />
        </div>

        <div className={styles.fieldGroup}>
          <label htmlFor="password" className={styles.label}>Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={styles.input}
            placeholder="Your password"
            required
          />
        </div>

        <button
          type="submit"
          className={styles.primaryButton}
          disabled={isLoading}
        >
          {isLoading ? 'Signing In...' : 'Sign In'}
        </button>
      </form>

      <p className={styles.switchText}>
        Don't have an account?{' '}
        <button
          type="button"
          onClick={onSwitchToSignup}
          className={styles.linkButton}
        >
          Create Account
        </button>
      </p>
    </div>
  );
}
