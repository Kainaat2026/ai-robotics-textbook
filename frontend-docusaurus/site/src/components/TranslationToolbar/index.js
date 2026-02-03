/**
 * TranslationToolbar - Browser-based translation and text-to-speech
 * Uses browser's native TTS and Google Translate for translation
 */
import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from '@docusaurus/router';
import { Languages, Volume2, VolumeX, Globe, X } from 'lucide-react';
import styles from './styles.module.css';

// Supported languages for Google Translate
const LANGUAGES = [
  { code: 'en', name: 'English', native: 'English' },
  { code: 'ur', name: 'Urdu', native: 'اردو' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
  { code: 'ar', name: 'Arabic', native: 'العربية' },
  { code: 'es', name: 'Spanish', native: 'Español' },
  { code: 'zh', name: 'Chinese', native: '中文' },
];

export default function TranslationToolbar() {
  const location = useLocation();
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speechError, setSpeechError] = useState(null);
  const [isChapter, setIsChapter] = useState(false);
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const menuRef = useRef(null);

  // Check if on chapter page
  useEffect(() => {
    const pathname = location.pathname;
    const onChapter = pathname.includes('/docs/') && pathname.includes('chapter');
    setIsChapter(onChapter);

    // Reset state when changing pages
    setSpeechError(null);
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  }, [location.pathname]);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowLanguageMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Don't render on non-chapter pages or during SSR
  if (typeof window === 'undefined' || !isChapter) {
    return null;
  }

  // Get page content for TTS
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
        return el.innerText.substring(0, 3000);
      }
    }
    return null;
  };

  // Text-to-Speech using browser's native API
  const handleSpeak = () => {
    if (!window.speechSynthesis) {
      setSpeechError('Speech not supported in this browser');
      return;
    }

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    const text = getPageContent();
    if (!text) {
      setSpeechError('No content found to read');
      return;
    }

    setSpeechError(null);

    // Get available voices
    const voices = window.speechSynthesis.getVoices();

    // Find voice for current language
    const langCode = currentLanguage === 'en' ? 'en-US' :
                     currentLanguage === 'ur' ? 'ur-PK' :
                     currentLanguage === 'hi' ? 'hi-IN' :
                     currentLanguage === 'ar' ? 'ar-SA' :
                     currentLanguage === 'es' ? 'es-ES' :
                     currentLanguage === 'zh' ? 'zh-CN' : 'en-US';

    const preferredVoice = voices.find(v => v.lang.startsWith(currentLanguage)) ||
                          voices.find(v => v.lang.startsWith('en'));

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langCode;
    utterance.rate = 0.9;
    utterance.pitch = 1;

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = (e) => {
      setIsSpeaking(false);
      if (e.error !== 'canceled') {
        setSpeechError('Speech error. Try again.');
      }
    };

    window.speechSynthesis.speak(utterance);
    setIsSpeaking(true);
  };

  // Use Google Translate to translate the page
  const handleTranslate = (langCode) => {
    setCurrentLanguage(langCode);
    setShowLanguageMenu(false);

    if (langCode === 'en') {
      // Remove translation
      const frame = document.querySelector('.goog-te-banner-frame');
      if (frame) {
        frame.remove();
      }
      // Reset page
      document.body.style.top = '0';
      // Clear Google Translate cookie
      document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      window.location.reload();
      return;
    }

    // Set Google Translate cookie
    document.cookie = `googtrans=/en/${langCode}; path=/`;

    // Load Google Translate script if not already loaded
    if (!document.getElementById('google-translate-script')) {
      const script = document.createElement('script');
      script.id = 'google-translate-script';
      script.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
      document.body.appendChild(script);

      // Initialize Google Translate
      window.googleTranslateElementInit = function() {
        new window.google.translate.TranslateElement({
          pageLanguage: 'en',
          includedLanguages: LANGUAGES.map(l => l.code).join(','),
          autoDisplay: false
        }, 'google_translate_element');
      };
    } else {
      // Trigger translation change
      const select = document.querySelector('.goog-te-combo');
      if (select) {
        select.value = langCode;
        select.dispatchEvent(new Event('change'));
      } else {
        // Fallback: reload with cookie set
        window.location.reload();
      }
    }
  };

  const currentLang = LANGUAGES.find(l => l.code === currentLanguage) || LANGUAGES[0];

  return (
    <>
      {/* Hidden Google Translate element */}
      <div id="google_translate_element" style={{ display: 'none' }}></div>

      <div className={styles.toolbar}>
        <div className={styles.toolbarContent}>
          <div className={styles.toolbarLabel}>
            <Languages size={18} />
            <span>Language & Audio:</span>
          </div>

          <div className={styles.actions}>
            {/* Language Selector */}
            <div className={styles.languageSelector} ref={menuRef}>
              <button
                onClick={() => setShowLanguageMenu(!showLanguageMenu)}
                className={`${styles.actionBtn} ${currentLanguage !== 'en' ? styles.active : ''}`}
              >
                <Globe size={16} />
                <span>{currentLang.native}</span>
              </button>

              {showLanguageMenu && (
                <div className={styles.languageMenu}>
                  {LANGUAGES.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => handleTranslate(lang.code)}
                      className={`${styles.languageOption} ${currentLanguage === lang.code ? styles.selected : ''}`}
                    >
                      <span className={styles.langNative}>{lang.native}</span>
                      <span className={styles.langName}>{lang.name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Text-to-Speech */}
            <button
              onClick={handleSpeak}
              className={`${styles.actionBtn} ${isSpeaking ? styles.speaking : ''}`}
              title={isSpeaking ? 'Stop reading' : 'Read aloud'}
            >
              {isSpeaking ? <><VolumeX size={16} /> Stop</> : <><Volume2 size={16} /> Listen</>}
            </button>

            {speechError && <span className={styles.error}>{speechError}</span>}
          </div>
        </div>
      </div>
    </>
  );
}
