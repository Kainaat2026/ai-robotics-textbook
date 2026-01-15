/**
 * ChatbotInterface - Main chatbot UI component
 *
 * Features:
 * - Message list with scrolling
 * - User and assistant message bubbles
 * - Input field and send button
 * - Loading states
 * - Citation display
 * - Error handling
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  chatbotService,
  ChatMessageResponse,
  MessageRole,
  Language,
  Citation,
} from './ChatbotService';
import styles from './ChatbotInterface.module.css';

interface Message {
  id: string;
  role: MessageRole;
  content: string;
  citations?: Citation[];
  timestamp: Date;
}

interface ChatbotInterfaceProps {
  isOpen: boolean;
  onClose: () => void;
  language?: Language;
}

export default function ChatbotInterface({
  isOpen,
  onClose,
  language = Language.ENGLISH,
}: ChatbotInterfaceProps): JSX.Element | null {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Don't render if closed
  if (!isOpen) {
    return null;
  }

  /**
   * Handle sending a message
   */
  const handleSendMessage = async () => {
    const trimmedMessage = inputValue.trim();
    if (!trimmedMessage || isLoading) {
      return;
    }

    // Clear input and error
    setInputValue('');
    setError(null);

    // Add user message to UI immediately
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: MessageRole.USER,
      content: trimmedMessage,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Set loading state
    setIsLoading(true);

    try {
      // Send message to backend
      const response: ChatMessageResponse = await chatbotService.sendMessage(
        trimmedMessage,
        conversationId,
        language
      );

      // Update conversation ID if this is first message
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response to UI
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: MessageRole.ASSISTANT,
        content: response.message,
        citations: response.citations,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);

      // Remove the user message on error
      setMessages((prev) => prev.slice(0, -1));

      // Restore input value
      setInputValue(trimmedMessage);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle Enter key to send (Shift+Enter for newline)
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  /**
   * Start a new conversation
   */
  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    setInputValue('');
  };

  /**
   * Format citation for display
   */
  const formatCitation = (citation: Citation, index: number) => {
    return (
      <div key={index} className={styles.citation}>
        <span className={styles.citationNumber}>[{index + 1}]</span>
        <span className={styles.citationText}>
          {citation.title} - {citation.section}
        </span>
      </div>
    );
  };

  return (
    <div className={styles.chatbotContainer}>
      {/* Header */}
      <div className={styles.chatbotHeader}>
        <div className={styles.headerTitle}>
          <span className={styles.headerIcon}>🤖</span>
          <span>Physical AI Assistant</span>
        </div>
        <div className={styles.headerActions}>
          <button
            className={styles.newChatButton}
            onClick={handleNewConversation}
            title="New conversation"
            aria-label="Start new conversation"
          >
            ➕
          </button>
          <button
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Close chatbot"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className={styles.messagesContainer}>
        {messages.length === 0 && (
          <div className={styles.welcomeMessage}>
            <h3>Welcome! 👋</h3>
            <p>
              Ask me anything about Physical AI and Humanoid Robotics. I can help
              with:
            </p>
            <ul>
              <li>ROS 2 concepts and tutorials</li>
              <li>Gazebo simulation</li>
              <li>NVIDIA Isaac platform</li>
              <li>VLA systems</li>
            </ul>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={
              message.role === MessageRole.USER
                ? styles.userMessage
                : styles.assistantMessage
            }
          >
            <div className={styles.messageContent}>{message.content}</div>

            {/* Citations for assistant messages */}
            {message.role === MessageRole.ASSISTANT && message.citations && message.citations.length > 0 && (
              <div className={styles.citationsContainer}>
                <div className={styles.citationsLabel}>Sources:</div>
                {message.citations.map((citation, index) =>
                  formatCitation(citation, index)
                )}
              </div>
            )}
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className={styles.assistantMessage}>
            <div className={styles.loadingDots}>
              <span>●</span>
              <span>●</span>
              <span>●</span>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className={styles.errorMessage}>
            <span className={styles.errorIcon}>⚠️</span>
            {error}
          </div>
        )}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className={styles.inputContainer}>
        <textarea
          ref={inputRef}
          className={styles.messageInput}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question..."
          rows={1}
          maxLength={2000}
          disabled={isLoading}
          aria-label="Message input"
        />
        <button
          className={styles.sendButton}
          onClick={handleSendMessage}
          disabled={isLoading || !inputValue.trim()}
          aria-label="Send message"
        >
          {isLoading ? '⏳' : '➤'}
        </button>
      </div>
    </div>
  );
}
