/**
 * LanguageToggle - Switch between English and Urdu
 *
 * Features:
 * - Toggle between EN and UR languages
 * - Triggers content translation
 * - Applies RTL styling for Urdu
 * - Persists language preference
 */

import React, { useState, useEffect } from 'react';
import styles from './LanguageToggle.module.css';

export type Language = 'en' | 'ur';

interface LanguageToggleProps {
  currentLanguage: Language;
  onLanguageChange: (language: Language) => void;
  disabled?: boolean;
}

export const LanguageToggle: React.FC<LanguageToggleProps> = ({
  currentLanguage,
  onLanguageChange,
  disabled = false,
}) => {
  const handleToggle = (language: Language) => {
    if (language !== currentLanguage && !disabled) {
      onLanguageChange(language);
      // Persist preference
      localStorage.setItem('preferredLanguage', language);
    }
  };

  return (
    <div className={styles.languageToggle}>
      <button
        className={`${styles.languageButton} ${
          currentLanguage === 'en' ? styles.active : ''
        }`}
        onClick={() => handleToggle('en')}
        disabled={disabled}
        aria-label="Switch to English"
      >
        <span className={styles.flag}>🇬🇧</span>
        <span className={styles.languageName}>English</span>
      </button>

      <button
        className={`${styles.languageButton} ${
          currentLanguage === 'ur' ? styles.active : ''
        }`}
        onClick={() => handleToggle('ur')}
        disabled={disabled}
        aria-label="Switch to Urdu"
        dir="rtl"
      >
        <span className={styles.flag}>🇵🇰</span>
        <span className={styles.languageName}>اردو</span>
      </button>
    </div>
  );
};

/**
 * Hook for managing language state and translation
 */
export function useLanguage(initialContent: string) {
  const [language, setLanguage] = useState<Language>('en');
  const [content, setContent] = useState<string>(initialContent);
  const [originalContent] = useState<string>(initialContent);
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load preferred language from localStorage
  useEffect(() => {
    const preferred = localStorage.getItem('preferredLanguage') as Language;
    if (preferred && (preferred === 'en' || preferred === 'ur')) {
      setLanguage(preferred);
    }
  }, []);

  const translateContent = async (targetLanguage: Language) => {
    if (targetLanguage === 'en') {
      // Switch back to original English content
      setContent(originalContent);
      setLanguage('en');
      return;
    }

    setIsTranslating(true);
    setError(null);

    try {
      const response = await fetch(
        `${(typeof process !== 'undefined' && process.env?.REACT_APP_API_URL) || 'http://localhost:8000/api'}/translate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            content: originalContent,
            target_language: targetLanguage,
            content_type: 'chapter',
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Translation failed');
      }

      const data = await response.json();
      setContent(data.translated_content);
      setLanguage(targetLanguage);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Translation failed');
      // Revert to previous language on error
    } finally {
      setIsTranslating(false);
    }
  };

  return {
    language,
    content,
    isTranslating,
    error,
    translateContent,
  };
}
