/**
 * UserMenu Component
 *
 * Displays user information and logout option.
 * Shows login/signup buttons for unauthenticated users.
 */

import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import LoginForm from './LoginForm';
import SignupForm from './SignupForm';
import styles from './UserMenu.module.css';

export default function UserMenu(): JSX.Element {
  const { user, logout, isAuthenticated } = useAuth();
  const [showMenu, setShowMenu] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');

  const handleLogout = () => {
    logout();
    setShowMenu(false);
  };

  const handleShowLogin = () => {
    setAuthMode('login');
    setShowAuthModal(true);
  };

  const handleShowSignup = () => {
    setAuthMode('signup');
    setShowAuthModal(true);
  };

  const handleAuthSuccess = () => {
    setShowAuthModal(false);
  };

  if (!isAuthenticated) {
    return (
      <>
        <div className={styles.authButtons}>
          <button onClick={handleShowLogin} className={styles.loginButton}>
            Login
          </button>
          <button onClick={handleShowSignup} className={styles.signupButton}>
            Sign Up
          </button>
        </div>

        {/* Auth Modal */}
        {showAuthModal && (
          <div
            className={styles.modalOverlay}
            onClick={() => setShowAuthModal(false)}
          >
            <div
              className={styles.modalContent}
              onClick={(e) => e.stopPropagation()}
            >
              {authMode === 'login' ? (
                <LoginForm
                  onSuccess={handleAuthSuccess}
                  onSwitchToSignup={() => setAuthMode('signup')}
                />
              ) : (
                <SignupForm
                  onSuccess={handleAuthSuccess}
                  onSwitchToLogin={() => setAuthMode('login')}
                />
              )}
            </div>
          </div>
        )}
      </>
    );
  }

  return (
    <div className={styles.userMenuContainer}>
      <button
        className={styles.userButton}
        onClick={() => setShowMenu(!showMenu)}
        aria-label="User menu"
      >
        <span className={styles.userIcon}>👤</span>
        <span className={styles.userEmail}>{user?.email}</span>
      </button>

      {showMenu && (
        <>
          <div
            className={styles.menuOverlay}
            onClick={() => setShowMenu(false)}
          />
          <div className={styles.dropdown}>
            <div className={styles.dropdownHeader}>
              <div className={styles.dropdownEmail}>{user?.email}</div>
              {user?.profile && (
                <div className={styles.dropdownProfile}>
                  <div className={styles.skillBadge}>
                    Python: {user.profile.python_level}
                  </div>
                  <div className={styles.skillBadge}>
                    AI: {user.profile.ai_experience}
                  </div>
                </div>
              )}
            </div>

            <div className={styles.dropdownDivider} />

            <button onClick={handleLogout} className={styles.dropdownItem}>
              Logout
            </button>
          </div>
        </>
      )}
    </div>
  );
}
