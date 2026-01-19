/**
 * useChat hook for chatbot state management
 */
import { useState, useCallback } from 'react';
import { chatApi } from '../api/client';

/**
 * Custom hook for chatbot functionality
 * @returns {Object} Chat state and methods
 */
export function useChat() {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [language, setLanguage] = useState('en');

  /**
   * Send a message to the chatbot
   * @param {string} message - User's message
   */
  const sendMessage = useCallback(async (message) => {
    if (!message.trim()) return;

    // Add user message to state immediately
    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      message: message.trim(),
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await chatApi.sendMessage({
        conversationId,
        message: message.trim(),
        language,
      });

      // Update conversation ID
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response to state
      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        message: response.message,
        citations: response.citations || [],
        tokens_used: response.tokens_used,
        response_time_ms: response.response_time_ms,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to send message';
      setError(errorMessage);

      // Add error message to chat
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: 'system',
          message: `Error: ${errorMessage}`,
          isError: true,
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [conversationId, language]);

  /**
   * Clear conversation and start fresh
   */
  const clearConversation = useCallback(() => {
    setConversationId(null);
    setMessages([]);
    setError(null);
  }, []);

  /**
   * Load existing conversation
   * @param {string} convId - Conversation ID to load
   */
  const loadConversation = useCallback(async (convId) => {
    setIsLoading(true);
    setError(null);

    try {
      const conversation = await chatApi.getConversation(convId);
      setConversationId(conversation.conversation_id);
      setLanguage(conversation.language);
      setMessages(conversation.messages.map((msg) => ({
        ...msg,
        id: msg.id || `msg-${Date.now()}-${Math.random()}`,
      })));
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Explain selected text
   * @param {Object} params - Selection parameters
   */
  const explainSelection = useCallback(async ({ selectedText, chapterId, surroundingContext }) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await chatApi.explainSelection({
        selectedText,
        chapterId,
        surroundingContext,
        language,
      });

      // Add explanation as a message
      setMessages((prev) => [
        ...prev,
        {
          id: `selection-${Date.now()}`,
          role: 'user',
          message: `Explain: "${selectedText}"`,
          isSelection: true,
          created_at: new Date().toISOString(),
        },
        {
          id: `explanation-${Date.now()}`,
          role: 'assistant',
          message: response.explanation,
          citations: response.citations || [],
          response_time_ms: response.response_time_ms,
          created_at: new Date().toISOString(),
        },
      ]);

      return response;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to explain selection');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [language]);

  return {
    conversationId,
    messages,
    isLoading,
    error,
    language,
    setLanguage,
    sendMessage,
    clearConversation,
    loadConversation,
    explainSelection,
  };
}

export default useChat;
