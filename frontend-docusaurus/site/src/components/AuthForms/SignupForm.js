/**
 * Signup Form with Background Questions
 * Multi-step signup process: credentials -> background questionnaire
 */
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import styles from './AuthForms.module.css';

const SKILL_LEVELS = [
  { value: 'beginner', label: 'Beginner', description: 'Just starting out' },
  { value: 'intermediate', label: 'Intermediate', description: 'Some experience' },
  { value: 'advanced', label: 'Advanced', description: 'Extensive experience' },
];

export default function SignupForm({ onSuccess, onSwitchToLogin }) {
  const { signup, submitQuestionnaire, error, clearError } = useAuth();
  const [step, setStep] = useState(1); // 1: credentials, 2: questionnaire
  const [isLoading, setIsLoading] = useState(false);
  const [localError, setLocalError] = useState('');

  // Step 1: Credentials
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Step 2: Questionnaire
  const [questionnaire, setQuestionnaire] = useState({
    pythonLevel: 'intermediate',
    aiExperience: 'beginner',
    roboticsExperience: 'beginner',
    hasRtxGpu: false,
    preferredLanguage: 'en',
  });

  const handleCredentialsSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');
    clearError();

    // Validate
    if (password !== confirmPassword) {
      setLocalError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setLocalError('Password must be at least 8 characters');
      return;
    }

    setIsLoading(true);
    const result = await signup({ email, password });
    setIsLoading(false);

    if (result.success) {
      setStep(2); // Move to questionnaire
    } else {
      setLocalError(result.error);
    }
  };

  const handleQuestionnaireSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    const result = await submitQuestionnaire(questionnaire);
    setIsLoading(false);

    if (result.success) {
      onSuccess?.();
    } else {
      setLocalError(result.error);
    }
  };

  const handleSkipQuestionnaire = () => {
    onSuccess?.();
  };

  const handleQuestionnaireChange = (field, value) => {
    setQuestionnaire(prev => ({ ...prev, [field]: value }));
  };

  const displayError = localError || error;

  if (step === 2) {
    return (
      <div className={styles.formContainer}>
        <h2 className={styles.title}>Tell Us About Yourself</h2>
        <p className={styles.subtitle}>
          Help us personalize your learning experience
        </p>

        {displayError && (
          <div className={styles.error}>{displayError}</div>
        )}

        <form onSubmit={handleQuestionnaireSubmit} className={styles.form}>
          {/* Python Experience */}
          <div className={styles.fieldGroup}>
            <label className={styles.label}>Python Programming Experience</label>
            <div className={styles.skillOptions}>
              {SKILL_LEVELS.map(level => (
                <button
                  key={level.value}
                  type="button"
                  className={`${styles.skillOption} ${questionnaire.pythonLevel === level.value ? styles.selected : ''}`}
                  onClick={() => handleQuestionnaireChange('pythonLevel', level.value)}
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
                  className={`${styles.skillOption} ${questionnaire.aiExperience === level.value ? styles.selected : ''}`}
                  onClick={() => handleQuestionnaireChange('aiExperience', level.value)}
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
                  className={`${styles.skillOption} ${questionnaire.roboticsExperience === level.value ? styles.selected : ''}`}
                  onClick={() => handleQuestionnaireChange('roboticsExperience', level.value)}
                >
                  <span className={styles.skillLabel}>{level.label}</span>
                  <span className={styles.skillDesc}>{level.description}</span>
                </button>
              ))}
            </div>
          </div>

          {/* RTX GPU */}
          <div className={styles.fieldGroup}>
            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={questionnaire.hasRtxGpu}
                onChange={(e) => handleQuestionnaireChange('hasRtxGpu', e.target.checked)}
                className={styles.checkbox}
              />
              <span>I have access to an NVIDIA RTX GPU</span>
            </label>
            <p className={styles.helpText}>
              This helps us recommend appropriate simulation exercises
            </p>
          </div>

          {/* Language Preference */}
          <div className={styles.fieldGroup}>
            <label className={styles.label}>Preferred Language</label>
            <select
              value={questionnaire.preferredLanguage}
              onChange={(e) => handleQuestionnaireChange('preferredLanguage', e.target.value)}
              className={styles.select}
            >
              <option value="en">English</option>
              <option value="ur">Urdu</option>
            </select>
          </div>

          <div className={styles.buttonGroup}>
            <button
              type="button"
              onClick={handleSkipQuestionnaire}
              className={styles.secondaryButton}
              disabled={isLoading}
            >
              Skip for Now
            </button>
            <button
              type="submit"
              className={styles.primaryButton}
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : 'Complete Setup'}
            </button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className={styles.formContainer}>
      <h2 className={styles.title}>Create Your Account</h2>
      <p className={styles.subtitle}>
        Start your journey into Physical AI & Robotics
      </p>

      {displayError && (
        <div className={styles.error}>{displayError}</div>
      )}

      <form onSubmit={handleCredentialsSubmit} className={styles.form}>
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
            placeholder="At least 8 characters"
            required
            minLength={8}
          />
          <p className={styles.helpText}>
            Must be 8+ characters with uppercase, lowercase, and number
          </p>
        </div>

        <div className={styles.fieldGroup}>
          <label htmlFor="confirmPassword" className={styles.label}>Confirm Password</label>
          <input
            id="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className={styles.input}
            placeholder="Confirm your password"
            required
          />
        </div>

        <button
          type="submit"
          className={styles.primaryButton}
          disabled={isLoading}
        >
          {isLoading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>

      <p className={styles.switchText}>
        Already have an account?{' '}
        <button
          type="button"
          onClick={onSwitchToLogin}
          className={styles.linkButton}
        >
          Sign In
        </button>
      </p>
    </div>
  );
}
