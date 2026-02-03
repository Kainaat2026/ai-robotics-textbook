/**
 * Navbar User Component
 * Shows sign in link or user menu based on auth state
 */
import React, { useState, useRef, useEffect } from 'react';
import Link from '@docusaurus/Link';
import { useAuth } from '../../contexts/AuthContext';
import styles from './NavbarUser.module.css';

export default function NavbarUser() {
  const { user, isAuthenticated, loading, logout } = useAuth();
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef(null);

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (loading) {
    return <div className={styles.loading}>...</div>;
  }

  if (!isAuthenticated) {
    return (
      <div className={styles.authLinks}>
        <Link to="/signin" className={styles.signInLink}>Sign In</Link>
        <Link to="/signup" className={styles.signUpLink}>Sign Up</Link>
      </div>
    );
  }

  const initials = user?.email?.charAt(0).toUpperCase() || '?';
  const skillLevel = user?.profile ? getSkillBadge(user.profile) : null;

  return (
    <div className={styles.userContainer} ref={menuRef}>
      <button
        className={styles.userButton}
        onClick={() => setShowMenu(!showMenu)}
        aria-expanded={showMenu}
        aria-label="User menu"
      >
        <div className={styles.avatar}>{initials}</div>
        {skillLevel && <span className={styles.skillBadge}>{skillLevel}</span>}
      </button>

      {showMenu && (
        <div className={styles.dropdown}>
          <div className={styles.userInfo}>
            <div className={styles.userEmail}>{user.email}</div>
            {user.profile && (
              <div className={styles.userSkills}>
                <SkillTag label="Python" level={user.profile.python_level} />
                <SkillTag label="AI" level={user.profile.ai_experience} />
                <SkillTag label="Robotics" level={user.profile.robotics_experience} />
              </div>
            )}
          </div>
          <hr className={styles.divider} />
          <Link to="/progress" className={styles.menuItem}>
            My Progress
          </Link>
          <Link to="/profile" className={styles.menuItem}>
            Edit Profile
          </Link>
          <hr className={styles.divider} />
          <button onClick={logout} className={styles.logoutButton}>
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
}

function SkillTag({ label, level }) {
  const colors = {
    beginner: '#4caf50',
    intermediate: '#ff9800',
    advanced: '#9c27b0'
  };

  return (
    <span
      className={styles.skillTag}
      style={{ backgroundColor: colors[level] || colors.intermediate }}
    >
      {label}: {level?.charAt(0).toUpperCase() + level?.slice(1)}
    </span>
  );
}

function getSkillBadge(profile) {
  const levels = { beginner: 1, intermediate: 2, advanced: 3 };
  const avg = (
    levels[profile.python_level] +
    levels[profile.ai_experience] +
    levels[profile.robotics_experience]
  ) / 3;

  if (avg >= 2.5) return 'ADV';
  if (avg >= 1.5) return 'INT';
  return 'BEG';
}
