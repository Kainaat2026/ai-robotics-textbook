/**
 * ChatbotService - API client for RAG chatbot endpoints
 *
 * Handles:
 * - Sending messages to chatbot
 * - Retrieving conversation history
 * - Error handling and retries
 */

import axios, { AxiosError } from 'axios';

// API Base URL - configurable via environment variable
const API_BASE_URL = (typeof process !== 'undefined' && process.env?.REACT_APP_API_URL) || 'http://localhost:8000/api';

// TypeScript interfaces matching backend Pydantic models

export enum Language {
  ENGLISH = 'en',
  URDU = 'ur',
}

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
}

export interface Citation {
  chapter_id: string;
  section: string;
  title: string;
}

export interface ChatMessageCreate {
  conversation_id: string | null;
  message: string;
  language: Language;
}

export interface ChatMessageResponse {
  conversation_id: string;
  message: string;
  citations: Citation[];
  tokens_used?: number;
  response_time_ms?: number;
}

export interface MessageHistoryItem {
  id: string;
  role: MessageRole;
  message: string;
  citations?: Citation[];
  created_at: string;
}

export interface ConversationHistoryResponse {
  conversation_id: string;
  language: Language;
  messages: MessageHistoryItem[];
  created_at: string;
  updated_at: string;
}

export interface TextSelectionRequest {
  selected_text: string;
  chapter_id: string;
  surrounding_context?: string;
  language: Language;
}

export interface TextSelectionResponse {
  explanation: string;
  citations: Citation[];
  response_time_ms?: number;
}

/**
 * ChatbotService class for API communication
 */
class ChatbotService {
  private axiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000, // 30 second timeout for AI responses
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        return this.handleError(error);
      }
    );
  }

  /**
   * Send a message to the chatbot
   */
  async sendMessage(
    message: string,
    conversationId: string | null = null,
    language: Language = Language.ENGLISH
  ): Promise<ChatMessageResponse> {
    const payload: ChatMessageCreate = {
      conversation_id: conversationId,
      message,
      language,
    };

    try {
      const response = await this.axiosInstance.post<ChatMessageResponse>(
        '/chat',
        payload
      );
      return response.data;
    } catch (error) {
      throw this.formatError(error);
    }
  }

  /**
   * Get full conversation history
   */
  async getConversationHistory(
    conversationId: string
  ): Promise<ConversationHistoryResponse> {
    try {
      const response = await this.axiosInstance.get<ConversationHistoryResponse>(
        `/chat/conversation/${conversationId}`
      );
      return response.data;
    } catch (error) {
      throw this.formatError(error);
    }
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: string): Promise<void> {
    try {
      await this.axiosInstance.delete(`/chat/conversation/${conversationId}`);
    } catch (error) {
      throw this.formatError(error);
    }
  }

  /**
   * Get explanation for selected text (User Story 3)
   */
  async explainTextSelection(
    selectedText: string,
    chapterId: string,
    surroundingContext?: string,
    language: Language = Language.ENGLISH
  ): Promise<TextSelectionResponse> {
    const payload: TextSelectionRequest = {
      selected_text: selectedText,
      chapter_id: chapterId,
      surrounding_context: surroundingContext,
      language,
    };

    try {
      const response = await this.axiosInstance.post<TextSelectionResponse>(
        '/chat/text-selection',
        payload
      );
      return response.data;
    } catch (error) {
      throw this.formatError(error);
    }
  }

  /**
   * Handle axios errors with retries for network issues
   */
  private async handleError(error: AxiosError): Promise<never> {
    // Network error - retry once after 1 second
    if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      // Retry the request once
      if (error.config) {
        try {
          const response = await axios.request(error.config);
          return response as never;
        } catch (retryError) {
          throw retryError;
        }
      }
    }

    throw error;
  }

  /**
   * Format error messages for UI display
   */
  private formatError(error: unknown): Error {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;

      // Server returned error response
      if (axiosError.response) {
        const status = axiosError.response.status;
        const detail = (axiosError.response.data as any)?.detail;

        if (status === 404) {
          return new Error(detail || 'Conversation not found');
        } else if (status === 422) {
          return new Error(detail || 'Invalid request format');
        } else if (status >= 500) {
          return new Error('Server error. Please try again later.');
        } else {
          return new Error(detail || 'An error occurred');
        }
      }

      // Network error
      if (axiosError.code === 'ECONNABORTED') {
        return new Error('Request timeout. The server took too long to respond.');
      } else if (axiosError.code === 'ERR_NETWORK') {
        return new Error(
          'Network error. Please check your internet connection and try again.'
        );
      }

      return new Error('Failed to communicate with the chatbot server');
    }

    // Unknown error
    return new Error('An unexpected error occurred');
  }
}

// Export singleton instance
export const chatbotService = new ChatbotService();
