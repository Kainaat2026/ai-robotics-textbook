/**
 * useTranslation hook for content translation
 */
import { useState, useCallback } from 'react';
import { translationApi } from '../api/client';

/**
 * Custom hook for translation functionality
 * @returns {Object} Translation state and methods
 */
export function useTranslation() {
  const [language, setLanguage] = useState('en');
  const [translatedContent, setTranslatedContent] = useState(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState(null);
  const [cache, setCache] = useState({}); // Cache translations

  /**
   * Translate content
   * @param {string} content - Content to translate
   * @param {string} targetLanguage - Target language code
   * @returns {Promise<string>} Translated content
   */
  const translate = useCallback(async (content, targetLanguage = 'ur') => {
    if (!content) return content;

    // Check cache first
    const cacheKey = `${content.substring(0, 100)}_${targetLanguage}`;
    if (cache[cacheKey]) {
      return cache[cacheKey];
    }

    setIsTranslating(true);
    setError(null);

    try {
      const response = await translationApi.translate({
        content,
        targetLanguage,
      });

      const translated = response.translated_content || response.content;

      // Update cache
      setCache((prev) => ({
        ...prev,
        [cacheKey]: translated,
      }));

      setTranslatedContent(translated);
      return translated;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Translation failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsTranslating(false);
    }
  }, [cache]);

  /**
   * Toggle between languages
   */
  const toggleLanguage = useCallback(() => {
    setLanguage((prev) => (prev === 'en' ? 'ur' : 'en'));
  }, []);

  /**
   * Clear translation cache
   */
  const clearCache = useCallback(() => {
    setCache({});
    setTranslatedContent(null);
  }, []);

  /**
   * Check if current language is RTL
   */
  const isRTL = language === 'ur' || language === 'ar';

  return {
    language,
    setLanguage,
    translatedContent,
    isTranslating,
    error,
    isRTL,
    translate,
    toggleLanguage,
    clearCache,
  };
}

export default useTranslation;
