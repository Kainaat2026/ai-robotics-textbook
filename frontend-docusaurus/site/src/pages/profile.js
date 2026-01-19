/**
 * Profile page - Update user background and preferences
 */
import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import { useHistory } from '@docusaurus/router';
import { useAuth } from '../contexts/AuthContext';
import styles from './profile.module.css';

const SKILL_LEVELS = [
  { value: 'beginner', label: 'Beginner', description: 'Just starting out' },
  { value: 'intermediate', label: 'Intermediate', description: 'Some experience' },
  { value: 'advanced', label: 'Advanced', description: 'Extensive experience' },
];

export default function ProfilePage() {
  const history = useHistory();
  const { user, isAuthenticated, loading, submitQuestionnaire, logout } = useAuth();
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const [formData, setFormData] = useState({
    pythonLevel: 'intermediate',
    aiExperience: 'beginner',
    roboticsExperience: 'beginner',
    hasRtxGpu: false,
    preferredLanguage: 'en',
  });

  // Redirect if not logged in
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      history.push('/signin');
    }
  }, [loading, isAuthenticated, history]);

  // Load user profile data
  useEffect(() => {
    if (user?.profile) {
      setFormData({
        pythonLevel: user.profile.python_level || 'intermediate',
        aiExperience: user.profile.ai_experience || 'beginner',
        roboticsExperience: user.profile.robotics_experience || 'beginner',
        hasRtxGpu: user.profile.has_rtx_gpu || false,
        preferredLanguage: user.profile.preferred_language || 'en',
      });
    }
  }, [user]);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage({ type: '', text: '' });

    const result = await submitQuestionnaire(formData);

    setIsSaving(false);
    if (result.success) {
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
    } else {
      setMessage({ type: 'error', text: result.error || 'Failed to update profile' });
    }
  };

  if (loading) {
    return (
      <Layout title="Profile">
        <main className={styles.container}>
          <div className={styles.loading}>Loading...</div>
        </main>
      </Layout>
    );
  }

  return (
    <Layout
      title="My Profile"
      description="Update your learning profile and preferences"
    >
      <main className={styles.container}>
        <div className={styles.card}>
          <h1 className={styles.title}>My Profile</h1>

          {user && (
            <div className={styles.userInfo}>
              <div className={styles.avatar}>
                {user.email?.charAt(0).toUpperCase()}
              </div>
              <div className={styles.userDetails}>
                <span className={styles.email}>{user.email}</span>
                <span className={styles.memberSince}>
                  Member since {new Date(user.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          )}

          {message.text && (
            <div className={`${styles.message} ${styles[message.type]}`}>
              {message.text}
            </div>
          )}

          <form onSubmit={handleSubmit} className={styles.form}>
            <h2 className={styles.sectionTitle}>Learning Background</h2>

            {/* Python Experience */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Python Programming Experience</label>
              <div className={styles.skillOptions}>
                {SKILL_LEVELS.map(level => (
                  <button
                    key={level.value}
                    type="button"
                    className={`${styles.skillOption} ${formData.pythonLevel === level.value ? styles.selected : ''}`}
                    onClick={() => handleChange('pythonLevel', level.value)}
                  >
                    <span className={styles.skillLabel}>{level.label}</span>
                    <span className={styles.skillDesc}>{level.description}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* AI/ML Experience */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>AI/Machine Learning Experience</label>
              <div className={styles.skillOptions}>
                {SKILL_LEVELS.map(level => (
                  <button
                    key={level.value}
                    type="button"
                    className={`${styles.skillOption} ${formData.aiExperience === level.value ? styles.selected : ''}`}
                    onClick={() => handleChange('aiExperience', level.value)}
                  >
                    <span className={styles.skillLabel}>{level.label}</span>
                    <span className={styles.skillDesc}>{level.description}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Robotics Experience */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Robotics Experience</label>
              <div className={styles.skillOptions}>
                {SKILL_LEVELS.map(level => (
                  <button
                    key={level.value}
                    type="button"
                    className={`${styles.skillOption} ${formData.roboticsExperience === level.value ? styles.selected : ''}`}
                    onClick={() => handleChange('roboticsExperience', level.value)}
                  >
                    <span className={styles.skillLabel}>{level.label}</span>
                    <span className={styles.skillDesc}>{level.description}</span>
                  </button>
                ))}
              </div>
            </div>

            <h2 className={styles.sectionTitle}>Preferences</h2>

            {/* RTX GPU */}
            <div className={styles.fieldGroup}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={formData.hasRtxGpu}
                  onChange={(e) => handleChange('hasRtxGpu', e.target.checked)}
                  className={styles.checkbox}
                />
                <span>I have access to an NVIDIA RTX GPU</span>
              </label>
              <p className={styles.helpText}>
                Enables advanced simulation exercises with NVIDIA Isaac Sim
              </p>
            </div>

            {/* Language Preference */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Preferred Language</label>
              <select
                value={formData.preferredLanguage}
                onChange={(e) => handleChange('preferredLanguage', e.target.value)}
                className={styles.select}
              >
                <option value="en">English</option>
                <option value="ur">Urdu</option>
              </select>
            </div>

            <div className={styles.actions}>
              <button
                type="submit"
                className={styles.saveButton}
                disabled={isSaving}
              >
                {isSaving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>

          <hr className={styles.divider} />

          <div className={styles.dangerZone}>
            <h3 className={styles.dangerTitle}>Account Actions</h3>
            <button onClick={logout} className={styles.logoutButton}>
              Sign Out
            </button>
          </div>
        </div>
      </main>
    </Layout>
  );
}
