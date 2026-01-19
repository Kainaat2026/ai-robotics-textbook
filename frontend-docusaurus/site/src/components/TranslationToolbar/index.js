/**
 * TranslationToolbar - Translation and text-to-speech for chapters
 */
import React, { useState, useEffect } from 'react';
import { useLocation } from '@docusaurus/router';
import { Languages, Volume2, VolumeX, Loader2, X, Globe } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { translationApi } from '../../api/client';
import styles from './styles.module.css';

export default function TranslationToolbar() {
  const location = useLocation();
  const { isAuthenticated, loading: authLoading } = useAuth();

  const [showTranslation, setShowTranslation] = useState(false);
  const [translatedText, setTranslatedText] = useState('');
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isChapter, setIsChapter] = useState(false);

  // Check if on chapter page (any docs page with chapter in URL)
  useEffect(() => {
    const pathname = location.pathname;
    // Show on any docs page that has chapter in the URL
    const onChapter = pathname.includes('/docs/') && pathname.includes('chapter');
    setIsChapter(onChapter);

    // Reset state when changing pages
    setShowTranslation(false);
    setTranslatedText('');
    setError(null);
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);

    // Debug log
    console.log('[TranslationToolbar] pathname:', pathname, 'isChapter:', onChapter);
  }, [location.pathname]);

  // Don't render on non-chapter pages or during SSR
  if (typeof window === 'undefined' || !isChapter || authLoading) {
    return null;
  }

  // Get page content
  const getPageContent = () => {
    const selectors = [
      'article',
      '.theme-doc-markdown',
      '.markdown',
      '[class*="docItemCol"]'
    ];

    for (const selector of selectors) {
      const el = document.querySelector(selector);
      if (el && el.innerText) {
        return el.innerText.substring(0, 4000);
      }
    }
    return null;
  };

  // Translate to Urdu
  const handleTranslate = async () => {
    console.log('[TranslationToolbar] handleTranslate called, showTranslation:', showTranslation);

    if (showTranslation) {
      setShowTranslation(false);
      return;
    }

    // If already translated, just show
    if (translatedText) {
      console.log('[TranslationToolbar] Using cached translation');
      setShowTranslation(true);
      return;
    }

    setError(null);
    setIsTranslating(true);

    try {
      const content = getPageContent();
      console.log('[TranslationToolbar] Content length:', content?.length || 0);

      if (!content) {
        setError('Could not find page content');
        setIsTranslating(false);
        return;
      }

      console.log('[TranslationToolbar] Calling translation API...');
      const response = await translationApi.translate({
        content: content,
        targetLanguage: 'ur',
      });
      console.log('[TranslationToolbar] API response:', response);

      if (response.translated_content) {
        setTranslatedText(response.translated_content);
        setShowTranslation(true);
        console.log('[TranslationToolbar] Translation successful, length:', response.translated_content.length);
      } else {
        setError('No translation received');
      }
    } catch (err) {
      console.error('[TranslationToolbar] Translation error:', err);
      setError(err.response?.data?.detail || 'Translation failed. Try again.');
    } finally {
      setIsTranslating(false);
    }
  };

  // Text-to-Speech
  const handleSpeak = () => {
    if (!window.speechSynthesis) {
      setError('Speech not supported in this browser');
      return;
    }

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    const isUrdu = showTranslation && translatedText;
    const text = isUrdu ? translatedText : getPageContent();

    if (!text) return;

    // Check for available voices
    const voices = window.speechSynthesis.getVoices();
    const urduVoice = voices.find(v => v.lang.startsWith('ur'));
    const englishVoice = voices.find(v => v.lang.startsWith('en'));

    // If speaking Urdu and no Urdu voice available, warn user
    if (isUrdu && !urduVoice) {
      setError('Urdu voice not available. Try Chrome or Edge with language packs installed.');
      // Fall back to English voice for Urdu text
    }

    const utterance = new SpeechSynthesisUtterance(text.substring(0, 2000));
    utterance.lang = isUrdu ? 'ur-PK' : 'en-US';
    utterance.rate = 0.85;

    // Set voice if available
    if (isUrdu && urduVoice) {
      utterance.voice = urduVoice;
    } else if (!isUrdu && englishVoice) {
      utterance.voice = englishVoice;
    }

    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = (e) => {
      setIsSpeaking(false);
      if (e.error !== 'canceled') {
        setError('Speech error. Try again.');
      }
    };

    window.speechSynthesis.speak(utterance);
    setIsSpeaking(true);
  };

  // Translation available for all users (no login required)

  return (
    <>
      <div className={styles.toolbar}>
        <div className={styles.toolbarContent}>
          <div className={styles.toolbarLabel}>
            <Languages size={18} />
            <span>Personalize:</span>
          </div>

          <div className={styles.actions}>
            <button
              onClick={handleTranslate}
              disabled={isTranslating}
              className={`${styles.actionBtn} ${showTranslation ? styles.active : ''}`}
            >
              {isTranslating ? (
                <><Loader2 size={16} className={styles.spinner} /> Translating...</>
              ) : showTranslation ? (
                'Hide Urdu'
              ) : (
                'Urdu اردو'
              )}
            </button>

            <button
              onClick={handleSpeak}
              className={`${styles.actionBtn} ${isSpeaking ? styles.speaking : ''}`}
            >
              {isSpeaking ? <><VolumeX size={16} /> Stop</> : <><Volume2 size={16} /> Listen</>}
            </button>

            {error && <span className={styles.error}>{error}</span>}
          </div>
        </div>
      </div>

      {showTranslation && translatedText && (
        <div className={styles.urduWrapper}>
          <div className={styles.urduHeader}>
            <span>اردو ترجمہ | Urdu Translation</span>
            <button onClick={() => setShowTranslation(false)} className={styles.actionBtn} style={{padding: '0.3rem 0.8rem', fontSize: '0.8rem'}}>
              <X size={16} /> Close
            </button>
          </div>
          <div className={styles.urduBody}>
            {translatedText.split('\n').map((para, i) => (
              para.trim() && <p key={i}>{para}</p>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
