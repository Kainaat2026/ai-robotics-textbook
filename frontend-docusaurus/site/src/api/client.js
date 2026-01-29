/**
 * API client for backend communication
 */
import axios from 'axios';

// API base URL - uses environment variable or falls back to HF Spaces production URL
const API_BASE_URL = typeof window !== 'undefined'
  ? (process.env.REACT_APP_API_URL || window.ENV?.API_URL || 'https://kainat2026-ai-robotics-textbook-api.hf.space/api')
  : (process.env.API_URL || 'https://kainat2026-ai-robotics-textbook-api.hf.space/api');

// Create axios instance with defaults
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor for auth token
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log errors in development
    if (process.env.NODE_ENV === 'development') {
      console.error('API Error:', error.response?.data || error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Chat API
 */
export const chatApi = {
  /**
   * Send a message to the chatbot
   * @param {Object} params - Message parameters
   * @param {string|null} params.conversationId - Existing conversation ID or null for new
   * @param {string} params.message - User's message
   * @param {string} params.language - Language code (en/ur)
   * @returns {Promise<Object>} Chat response with citations
   */
  sendMessage: async ({ conversationId = null, message, language = 'en' }) => {
    const response = await apiClient.post('/chat', {
      conversation_id: conversationId,
      message,
      language,
    });
    return response.data;
  },

  /**
   * Get conversation history
   * @param {string} conversationId - Conversation ID
   * @returns {Promise<Object>} Conversation with messages
   */
  getConversation: async (conversationId) => {
    const response = await apiClient.get(`/chat/conversation/${conversationId}`);
    return response.data;
  },

  /**
   * Get explanation for selected text
   * @param {Object} params - Text selection parameters
   * @returns {Promise<Object>} Explanation response
   */
  explainSelection: async ({ selectedText, chapterId, surroundingContext, language = 'en' }) => {
    const response = await apiClient.post('/chat/text-selection', {
      selected_text: selectedText,
      chapter_id: chapterId,
      surrounding_context: surroundingContext,
      language,
    });
    return response.data;
  },
};

/**
 * Quiz API
 */
export const quizApi = {
  /**
   * Get list of available quizzes
   * @returns {Promise<Array>} List of quizzes
   */
  listQuizzes: async () => {
    const response = await apiClient.get('/quiz');
    return response.data;
  },

  /**
   * Get quiz for a chapter
   * @param {string} chapterId - Chapter ID
   * @returns {Promise<Object>} Quiz with questions
   */
  getQuiz: async (chapterId) => {
    const response = await apiClient.get(`/quiz/${chapterId}`);
    return response.data;
  },

  /**
   * Start a quiz session
   * @param {string} chapterId - Chapter ID
   * @returns {Promise<Object>} Quiz session with questions
   */
  startQuiz: async (chapterId) => {
    const response = await apiClient.post(`/quiz/${chapterId}/start`);
    return response.data;
  },

  /**
   * Submit quiz answers
   * @param {Object} submission - Quiz submission
   * @param {string} submission.attemptId - Session ID
   * @param {Array} submission.answers - Array of {question_id, user_answer}
   * @returns {Promise<Object>} Quiz results
   */
  submitQuiz: async ({ attemptId, answers }) => {
    const response = await apiClient.post('/quiz/submit', {
      attempt_id: attemptId,
      answers,
    });
    return response.data;
  },

  /**
   * Get quiz history
   * @param {string} chapterId - Optional chapter filter
   * @returns {Promise<Array>} Quiz attempts
   */
  getHistory: async (chapterId = null) => {
    const params = chapterId ? { chapter_id: chapterId } : {};
    const response = await apiClient.get('/quiz/history', { params });
    return response.data;
  },

  /**
   * Get quiz summary for a chapter
   * @param {string} chapterId - Chapter ID
   * @returns {Promise<Object>} Quiz summary
   */
  getSummary: async (chapterId) => {
    const response = await apiClient.get(`/quiz/summary/${chapterId}`);
    return response.data;
  },
};

/**
 * Translation API
 */
export const translationApi = {
  /**
   * Translate content
   * @param {Object} params - Translation parameters
   * @param {string} params.content - Content to translate
   * @param {string} params.targetLanguage - Target language code
   * @returns {Promise<Object>} Translated content
   */
  translate: async ({ content, targetLanguage = 'ur' }) => {
    const response = await apiClient.post('/translate', {
      content,
      target_language: targetLanguage,
    });
    return response.data;
  },
};

/**
 * Auth API
 */
export const authApi = {
  /**
   * Sign up a new user
   * @param {Object} params - Signup parameters
   * @param {string} params.email - User email
   * @param {string} params.password - User password
   * @returns {Promise<Object>} Auth token
   */
  signup: async ({ email, password }) => {
    const response = await apiClient.post('/auth/signup', { email, password });
    return response.data;
  },

  /**
   * Login user
   * @param {Object} params - Login parameters
   * @param {string} params.email - User email
   * @param {string} params.password - User password
   * @returns {Promise<Object>} Auth token
   */
  login: async ({ email, password }) => {
    const response = await apiClient.post('/auth/login', { email, password });
    return response.data;
  },

  /**
   * Get current user info
   * @returns {Promise<Object>} User data with profile
   */
  getMe: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  /**
   * Submit background questionnaire
   * @param {Object} params - Questionnaire data
   * @returns {Promise<Object>} Updated profile
   */
  submitQuestionnaire: async ({ pythonLevel, aiExperience, roboticsExperience, hasRtxGpu, preferredLanguage }) => {
    const response = await apiClient.post('/auth/questionnaire', {
      python_level: pythonLevel,
      ai_experience: aiExperience,
      robotics_experience: roboticsExperience,
      has_rtx_gpu: hasRtxGpu,
      preferred_language: preferredLanguage,
    });
    return response.data;
  },

  /**
   * Change password
   * @param {Object} params - Password change parameters
   * @returns {Promise<void>}
   */
  changePassword: async ({ currentPassword, newPassword }) => {
    await apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },
};

/**
 * Progress API
 */
export const progressApi = {
  /**
   * Get user's overall progress
   * @returns {Promise<Object>} Progress data
   */
  getProgress: async () => {
    const response = await apiClient.get('/progress');
    return response.data;
  },

  /**
   * Mark chapter as complete
   * @param {string} chapterId - Chapter ID
   * @returns {Promise<Object>} Updated progress
   */
  markComplete: async (chapterId) => {
    const response = await apiClient.post(`/progress/chapter/${chapterId}/complete`);
    return response.data;
  },

  /**
   * Update reading progress for a chapter
   * @param {string} chapterId - Chapter ID
   * @param {number} progress - Progress percentage (0-100)
   * @returns {Promise<Object>} Updated progress
   */
  updateReadingProgress: async (chapterId, progress) => {
    const response = await apiClient.post(`/progress/chapter/${chapterId}/reading`, {
      progress_percentage: progress,
    });
    return response.data;
  },

  /**
   * Toggle bookmark for a chapter
   * @param {string} chapterId - Chapter ID
   * @returns {Promise<Object>} Bookmark status
   */
  toggleBookmark: async (chapterId) => {
    const response = await apiClient.post(`/progress/bookmark/${chapterId}`);
    return response.data;
  },

  /**
   * Get bookmarks
   * @returns {Promise<Array>} List of bookmarks
   */
  getBookmarks: async () => {
    const response = await apiClient.get('/progress/bookmarks');
    return response.data;
  },

  /**
   * Get chapter progress
   * @param {string} chapterId - Chapter ID
   * @returns {Promise<Object>} Chapter progress details
   */
  getChapterProgress: async (chapterId) => {
    const response = await apiClient.get(`/progress/chapter/${chapterId}`);
    return response.data;
  },
};

export default apiClient;
