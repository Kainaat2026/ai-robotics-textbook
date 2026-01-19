/**
 * ChapterToolbar - Toolbar for chapter pages with Quiz, Translation, Progress features
 */
import React, { useState, useEffect } from 'react';
import { useLocation } from '@docusaurus/router';
import {
  BookOpen,
  Globe,
  CheckCircle,
  Bookmark,
  BookmarkCheck,
  ClipboardList,
  Loader2,
  X,
} from 'lucide-react';
import { useProgress } from '../../hooks/useProgress';
import { useTranslation } from '../../hooks/useTranslation';
import QuizInterface from '../QuizInterface';
import styles from './styles.module.css';

/**
 * Extract chapter ID from pathname
 */
function getChapterIdFromPath(pathname) {
  // Match patterns like /docs/module-01/chapter-01-introduction
  const match = pathname.match(/chapter-(\d+)-([a-z0-9-]+)/);
  if (match) {
    return `chapter-${match[1]}-${match[2]}`;
  }
  return null;
}

/**
 * ChapterToolbar component
 */
export default function ChapterToolbar() {
  const location = useLocation();
  const [showQuiz, setShowQuiz] = useState(false);
  const [showTranslation, setShowTranslation] = useState(false);

  // Get chapter ID from current path
  const chapterId = getChapterIdFromPath(location.pathname);

  // Only render on chapter pages
  if (!chapterId) {
    return null;
  }

  return (
    <>
      <div className={styles.toolbar}>
        <ToolbarContent
          chapterId={chapterId}
          showQuiz={showQuiz}
          setShowQuiz={setShowQuiz}
          showTranslation={showTranslation}
          setShowTranslation={setShowTranslation}
        />
      </div>

      {/* Quiz Modal */}
      {showQuiz && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <button
              className={styles.closeButton}
              onClick={() => setShowQuiz(false)}
            >
              <X size={24} />
            </button>
            <QuizInterface chapterId={chapterId} />
          </div>
        </div>
      )}

      {/* Translation Panel */}
      {showTranslation && (
        <TranslationPanel onClose={() => setShowTranslation(false)} />
      )}
    </>
  );
}

/**
 * Toolbar content component
 */
function ToolbarContent({
  chapterId,
  showQuiz,
  setShowQuiz,
  showTranslation,
  setShowTranslation,
}) {
  const {
    isBookmarked,
    isCompleted,
    isLoading,
    toggleBookmark,
    markComplete,
  } = useProgress(chapterId);

  const { language, toggleLanguage, isTranslating } = useTranslation();

  const handleBookmark = async () => {
    try {
      await toggleBookmark();
    } catch (err) {
      console.error('Failed to toggle bookmark:', err);
    }
  };

  const handleMarkComplete = async () => {
    try {
      await markComplete();
    } catch (err) {
      console.error('Failed to mark complete:', err);
    }
  };

  return (
    <div className={styles.actions}>
      {/* Language Toggle */}
      <button
        className={`${styles.actionButton} ${language === 'ur' ? styles.active : ''}`}
        onClick={toggleLanguage}
        title={`Switch to ${language === 'en' ? 'Urdu' : 'English'}`}
        disabled={isTranslating}
      >
        <Globe size={18} />
        <span>{language === 'en' ? 'EN' : 'UR'}</span>
      </button>

      {/* Bookmark */}
      <button
        className={`${styles.actionButton} ${isBookmarked ? styles.active : ''}`}
        onClick={handleBookmark}
        title={isBookmarked ? 'Remove bookmark' : 'Add bookmark'}
        disabled={isLoading}
      >
        {isBookmarked ? <BookmarkCheck size={18} /> : <Bookmark size={18} />}
        <span>Bookmark</span>
      </button>

      {/* Mark Complete */}
      <button
        className={`${styles.actionButton} ${isCompleted ? styles.completed : ''}`}
        onClick={handleMarkComplete}
        title={isCompleted ? 'Completed' : 'Mark as complete'}
        disabled={isLoading || isCompleted}
      >
        <CheckCircle size={18} />
        <span>{isCompleted ? 'Completed' : 'Mark Complete'}</span>
      </button>

      {/* Take Quiz */}
      <button
        className={`${styles.actionButton} ${styles.quizButton}`}
        onClick={() => setShowQuiz(true)}
        title="Take chapter quiz"
      >
        <ClipboardList size={18} />
        <span>Take Quiz</span>
      </button>
    </div>
  );
}

/**
 * Translation panel component
 */
function TranslationPanel({ onClose }) {
  const { language, isTranslating, translate, error } = useTranslation();
  const [translatedHtml, setTranslatedHtml] = useState(null);

  useEffect(() => {
    if (language === 'ur') {
      // Get the main content and translate it
      const contentEl = document.querySelector('.markdown');
      if (contentEl) {
        const text = contentEl.innerText;
        translate(text, 'ur')
          .then((translated) => {
            setTranslatedHtml(translated);
          })
          .catch(console.error);
      }
    }
  }, [language, translate]);

  return (
    <div className={styles.translationPanel}>
      <div className={styles.panelHeader}>
        <h3>Urdu Translation</h3>
        <button onClick={onClose}>
          <X size={20} />
        </button>
      </div>
      <div className={styles.panelContent} dir="rtl">
        {isTranslating ? (
          <div className={styles.loading}>
            <Loader2 className={styles.spinner} size={24} />
            <span>Translating...</span>
          </div>
        ) : error ? (
          <div className={styles.error}>{error}</div>
        ) : translatedHtml ? (
          <div className={styles.translatedText}>{translatedHtml}</div>
        ) : (
          <p>Click the language button to translate this chapter to Urdu.</p>
        )}
      </div>
    </div>
  );
}
