/**
 * PersonalizeButton - One-click content personalization
 *
 * Features:
 * - Triggers AI content adaptation based on user profile
 * - Shows loading state during personalization
 * - Handles errors gracefully
 * - Requires authentication
 */

import React, { useState } from 'react';
import { useAuth } from '@site/src/contexts/AuthContext';
import styles from './PersonalizeButton.module.css';

interface PersonalizeButtonProps {
  chapterId: string;
  content: string;
  onPersonalized: (personalizedContent: string) => void;
}

export const PersonalizeButton: React.FC<PersonalizeButtonProps> = ({
  chapterId,
  content,
  onPersonalized,
}) => {
  const { isAuthenticated, user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePersonalize = async () => {
    if (!isAuthenticated) {
      setError('Please sign in to personalize content');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${(typeof process !== 'undefined' && process.env?.REACT_APP_API_URL) || 'http://localhost:8000/api'}/personalize`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            chapter_id: chapterId,
            content: content,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to personalize content');
      }

      const data = await response.json();
      onPersonalized(data.personalized_content);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Personalization failed');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className={styles.notAuthenticated}>
        <span>Sign in to unlock personalized content</span>
      </div>
    );
  }

  return (
    <div className={styles.personalizeContainer}>
      <button
        className={styles.personalizeButton}
        onClick={handlePersonalize}
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <span className={styles.spinner}></span>
            Personalizing...
          </>
        ) : (
          <>
            <svg
              className={styles.icon}
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M8 1C4.13 1 1 4.13 1 8s3.13 7 7 7 7-3.13 7-7-3.13-7-7-7zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 10H6v-1h1V9H6V8h2v4h1v1z"
                fill="currentColor"
              />
            </svg>
            Personalize for Me
          </>
        )}
      </button>

      {error && <div className={styles.error}>{error}</div>}

      {user && (
        <div className={styles.profileInfo}>
          Adapted for: {user.email}
        </div>
      )}
    </div>
  );
};
