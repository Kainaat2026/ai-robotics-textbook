/**
 * ChapterTranslation - Inline translation component for chapter content
 * Shows a translation banner at the start of each chapter for logged-in users
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from '@docusaurus/router';
import { Globe, Loader2, RotateCcw, Languages } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { translationApi } from '../../api/client';
import styles from './styles.module.css';

/**
 * Check if current page is a chapter page
 */
function isChapterPage(pathname) {
  return pathname.includes('/docs/') && pathname.includes('chapter-');
}

/**
 * ChapterTranslation component - adds translation banner to chapter pages
 */
export default function ChapterTranslation() {
  const location = useLocation();
  const { user, isAuthenticated } = useAuth();
  const [isUrdu, setIsUrdu] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [translatedContent, setTranslatedContent] = useState(null);
  const [originalContent, setOriginalContent] = useState(null);
  const [error, setError] = useState(null);

  // Get user's preferred language from profile
  const preferredLanguage = user?.profile?.preferred_language || 'en';

  // Only show on chapter pages
  if (!isChapterPage(location.pathname)) {
    return null;
  }

  // Only show for authenticated users
  if (!isAuthenticated) {
    return (
      <div className={styles.banner}>
        <div className={styles.bannerContent}>
          <Languages size={20} />
          <span>Sign in to translate this chapter to Urdu</span>
          <a href="/signin" className={styles.signInLink}>Sign In</a>
        </div>
      </div>
    );
  }

  const handleTranslate = async () => {
    setError(null);
    setIsTranslating(true);

    try {
      // Get the main article content
      const contentEl = document.querySelector('article.markdown');
      if (!contentEl) {
        throw new Error('Could not find chapter content');
      }

      // Save original content if not saved
      if (!originalContent) {
        setOriginalContent(contentEl.innerHTML);
      }

      // Get text content for translation
      const textContent = contentEl.innerText;

      // Translate via API
      const response = await translationApi.translate({
        content: textContent,
        targetLanguage: 'ur',
      });

      const translated = response.translated_content || response.content;
      setTranslatedContent(translated);

      // Apply translation to the page
      applyTranslation(contentEl, translated);
      setIsUrdu(true);
    } catch (err) {
      console.error('Translation failed:', err);
      setError(err.response?.data?.detail || 'Translation failed. Please try again.');
    } finally {
      setIsTranslating(false);
    }
  };

  const handleRevert = () => {
    const contentEl = document.querySelector('article.markdown');
    if (contentEl && originalContent) {
      contentEl.innerHTML = originalContent;
      contentEl.removeAttribute('dir');
      contentEl.classList.remove(styles.urduContent);
    }
    setIsUrdu(false);
    setError(null);
  };

  const applyTranslation = (contentEl, translated) => {
    // Create a styled container for the translation
    const translatedHtml = `
      <div class="${styles.translatedWrapper}">
        <div class="${styles.translatedHeader}">
          <span class="${styles.urduBadge}">اردو ترجمہ</span>
          <span>Urdu Translation</span>
        </div>
        <div class="${styles.translatedBody}" dir="rtl" lang="ur">
          ${translated.split('\n').map(p => p.trim() ? `<p>${p}</p>` : '').join('')}
        </div>
      </div>
    `;

    contentEl.innerHTML = translatedHtml;
    contentEl.setAttribute('dir', 'rtl');
    contentEl.classList.add(styles.urduContent);
  };

  return (
    <div className={styles.banner}>
      <div className={styles.bannerContent}>
        <Globe size={20} className={styles.icon} />

        {isUrdu ? (
          <>
            <span className={styles.statusText}>
              Viewing in <strong>Urdu (اردو)</strong>
            </span>
            <button
              onClick={handleRevert}
              className={styles.revertButton}
              disabled={isTranslating}
            >
              <RotateCcw size={16} />
              <span>Back to English</span>
            </button>
          </>
        ) : (
          <>
            <span className={styles.statusText}>
              Personalize your learning experience
            </span>
            <button
              onClick={handleTranslate}
              className={styles.translateButton}
              disabled={isTranslating}
            >
              {isTranslating ? (
                <>
                  <Loader2 size={16} className={styles.spinner} />
                  <span>Translating...</span>
                </>
              ) : (
                <>
                  <Languages size={16} />
                  <span>Translate to Urdu (اردو)</span>
                </>
              )}
            </button>
          </>
        )}
      </div>

      {error && (
        <div className={styles.error}>
          {error}
        </div>
      )}
    </div>
  );
}
