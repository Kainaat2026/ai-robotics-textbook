/**
 * useQuiz hook for quiz state management
 */
import { useState, useCallback } from 'react';
import { quizApi } from '../api/client';

/**
 * Quiz status enum
 */
export const QuizStatus = {
  IDLE: 'idle',
  LOADING: 'loading',
  READY: 'ready',
  IN_PROGRESS: 'in_progress',
  SUBMITTING: 'submitting',
  COMPLETED: 'completed',
  ERROR: 'error',
};

/**
 * Custom hook for quiz functionality
 * @param {string} chapterId - Chapter ID for the quiz
 * @returns {Object} Quiz state and methods
 */
export function useQuiz(chapterId) {
  const [status, setStatus] = useState(QuizStatus.IDLE);
  const [quiz, setQuiz] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [startTime, setStartTime] = useState(null);

  /**
   * Load quiz (preview without starting session)
   */
  const loadQuiz = useCallback(async () => {
    setStatus(QuizStatus.LOADING);
    setError(null);

    try {
      const quizData = await quizApi.getQuiz(chapterId);
      setQuiz(quizData);
      setQuestions(quizData.questions);
      setStatus(QuizStatus.READY);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load quiz');
      setStatus(QuizStatus.ERROR);
    }
  }, [chapterId]);

  /**
   * Start quiz session
   */
  const startQuiz = useCallback(async () => {
    setStatus(QuizStatus.LOADING);
    setError(null);

    try {
      const session = await quizApi.startQuiz(chapterId);
      setSessionId(session.session_id);
      setQuiz({
        id: session.quiz_id,
        chapter_id: session.chapter_id,
        title: session.title,
        instructions: session.instructions,
        passing_score: session.passing_score,
        total_questions: session.total_questions,
        total_points: session.total_points,
      });
      setQuestions(session.questions);
      setCurrentIndex(0);
      setAnswers({});
      setResults(null);
      setStartTime(Date.now());
      setStatus(QuizStatus.IN_PROGRESS);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start quiz');
      setStatus(QuizStatus.ERROR);
    }
  }, [chapterId]);

  /**
   * Answer current question
   * @param {string} answer - Selected answer
   */
  const answerQuestion = useCallback((answer) => {
    const currentQuestion = questions[currentIndex];
    if (!currentQuestion) return;

    setAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: answer,
    }));
  }, [questions, currentIndex]);

  /**
   * Go to next question
   */
  const nextQuestion = useCallback(() => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  }, [currentIndex, questions.length]);

  /**
   * Go to previous question
   */
  const prevQuestion = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  }, [currentIndex]);

  /**
   * Jump to specific question
   * @param {number} index - Question index
   */
  const goToQuestion = useCallback((index) => {
    if (index >= 0 && index < questions.length) {
      setCurrentIndex(index);
    }
  }, [questions.length]);

  /**
   * Submit quiz
   */
  const submitQuiz = useCallback(async () => {
    if (!sessionId) {
      setError('No active quiz session');
      return;
    }

    setStatus(QuizStatus.SUBMITTING);
    setError(null);

    try {
      // Convert answers to submission format
      const formattedAnswers = Object.entries(answers).map(([questionId, answer]) => ({
        question_id: questionId,
        user_answer: answer,
      }));

      const result = await quizApi.submitQuiz({
        attemptId: sessionId,
        answers: formattedAnswers,
      });

      setResults(result);
      setStatus(QuizStatus.COMPLETED);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit quiz');
      setStatus(QuizStatus.ERROR);
    }
  }, [sessionId, answers]);

  /**
   * Reset quiz to initial state
   */
  const resetQuiz = useCallback(() => {
    setStatus(QuizStatus.IDLE);
    setQuiz(null);
    setSessionId(null);
    setQuestions([]);
    setCurrentIndex(0);
    setAnswers({});
    setResults(null);
    setError(null);
    setStartTime(null);
  }, []);

  /**
   * Calculate progress
   */
  const progress = {
    current: currentIndex + 1,
    total: questions.length,
    percentage: questions.length > 0 ? ((currentIndex + 1) / questions.length) * 100 : 0,
    answeredCount: Object.keys(answers).length,
    isComplete: Object.keys(answers).length === questions.length,
  };

  /**
   * Get current question
   */
  const currentQuestion = questions[currentIndex] || null;

  /**
   * Get elapsed time in seconds
   */
  const elapsedTime = startTime ? Math.floor((Date.now() - startTime) / 1000) : 0;

  return {
    status,
    quiz,
    questions,
    currentQuestion,
    currentIndex,
    answers,
    results,
    error,
    progress,
    elapsedTime,
    loadQuiz,
    startQuiz,
    answerQuestion,
    nextQuestion,
    prevQuestion,
    goToQuestion,
    submitQuiz,
    resetQuiz,
  };
}

export default useQuiz;
