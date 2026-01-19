/**
 * useProgress hook for tracking user progress
 */
import { useState, useCallback, useEffect } from 'react';
import { progressApi } from '../api/client';

/**
 * Custom hook for progress tracking
 * @param {string} chapterId - Optional chapter ID for chapter-specific progress
 * @returns {Object} Progress state and methods
 */
export function useProgress(chapterId = null) {
  const [overallProgress, setOverallProgress] = useState(null);
  const [chapterProgress, setChapterProgress] = useState(null);
  const [bookmarks, setBookmarks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Fetch overall progress
   */
  const fetchProgress = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await progressApi.getProgress();
      setOverallProgress(data);
    } catch (err) {
      // Don't set error for 401 (not authenticated) - just means user not logged in
      if (err.response?.status !== 401) {
        setError(err.response?.data?.detail || 'Failed to fetch progress');
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Fetch chapter-specific progress
   */
  const fetchChapterProgress = useCallback(async () => {
    if (!chapterId) return;

    try {
      const data = await progressApi.getChapterProgress(chapterId);
      setChapterProgress(data);
    } catch (err) {
      // Silently fail for chapter progress - user might not be logged in
      console.debug('Chapter progress not available:', err.message);
    }
  }, [chapterId]);

  /**
   * Fetch bookmarks
   */
  const fetchBookmarks = useCallback(async () => {
    try {
      const data = await progressApi.getBookmarks();
      setBookmarks(data);
    } catch (err) {
      // Silently fail for bookmarks
      console.debug('Bookmarks not available:', err.message);
    }
  }, []);

  /**
   * Mark current chapter as complete
   */
  const markComplete = useCallback(async () => {
    if (!chapterId) return;

    try {
      const data = await progressApi.markComplete(chapterId);
      setChapterProgress((prev) => ({
        ...prev,
        is_completed: true,
        completed_at: new Date().toISOString(),
      }));
      // Refresh overall progress
      fetchProgress();
      return data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to mark chapter complete');
      throw err;
    }
  }, [chapterId, fetchProgress]);

  /**
   * Update reading progress
   * @param {number} percentage - Progress percentage (0-100)
   */
  const updateReadingProgress = useCallback(async (percentage) => {
    if (!chapterId) return;

    try {
      await progressApi.updateReadingProgress(chapterId, percentage);
      setChapterProgress((prev) => ({
        ...prev,
        reading_progress: percentage,
      }));
    } catch (err) {
      // Silently fail - don't interrupt reading
      console.debug('Failed to update reading progress:', err.message);
    }
  }, [chapterId]);

  /**
   * Toggle bookmark for current chapter
   */
  const toggleBookmark = useCallback(async () => {
    if (!chapterId) return;

    try {
      const data = await progressApi.toggleBookmark(chapterId);
      setChapterProgress((prev) => ({
        ...prev,
        is_bookmarked: data.is_bookmarked,
      }));
      fetchBookmarks();
      return data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to toggle bookmark');
      throw err;
    }
  }, [chapterId, fetchBookmarks]);

  /**
   * Check if chapter is bookmarked
   */
  const isBookmarked = chapterProgress?.is_bookmarked || false;

  /**
   * Check if chapter is completed
   */
  const isCompleted = chapterProgress?.is_completed || false;

  /**
   * Get reading progress percentage
   */
  const readingProgress = chapterProgress?.reading_progress || 0;

  // Fetch data on mount
  useEffect(() => {
    fetchProgress();
    fetchBookmarks();
  }, [fetchProgress, fetchBookmarks]);

  // Fetch chapter progress when chapterId changes
  useEffect(() => {
    if (chapterId) {
      fetchChapterProgress();
    }
  }, [chapterId, fetchChapterProgress]);

  return {
    overallProgress,
    chapterProgress,
    bookmarks,
    isLoading,
    error,
    isBookmarked,
    isCompleted,
    readingProgress,
    fetchProgress,
    fetchChapterProgress,
    markComplete,
    updateReadingProgress,
    toggleBookmark,
  };
}

export default useProgress;
