/**
 * ChatbotWidget - Floating chatbot for AI assistance
 */
import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Trash2, Loader2, Globe } from 'lucide-react';
import { useChat } from '../../hooks/useChat';
import styles from './styles.module.css';

/**
 * Message bubble component
 */
function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';
  const isError = message.isError;

  return (
    <div className={`${styles.message} ${isUser ? styles.userMessage : styles.assistantMessage} ${isError ? styles.errorMessage : ''}`}>
      <div className={styles.messageContent}>
        {message.message}
      </div>

      {/* Citations */}
      {message.citations && message.citations.length > 0 && (
        <div className={styles.citations}>
          <span className={styles.citationLabel}>Sources:</span>
          {message.citations.map((citation, index) => (
            <span key={index} className={styles.citation}>
              {citation.title} ({citation.section})
            </span>
          ))}
        </div>
      )}

      {/* Response metadata */}
      {message.response_time_ms && (
        <div className={styles.metadata}>
          {(message.response_time_ms / 1000).toFixed(1)}s
        </div>
      )}
    </div>
  );
}

/**
 * Main ChatbotWidget component
 */
export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const {
    messages,
    isLoading,
    error,
    language,
    setLanguage,
    sendMessage,
    clearConversation,
  } = useChat();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      sendMessage(inputValue);
      setInputValue('');
    }
  };

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === 'en' ? 'ur' : 'en'));
  };

  return (
    <>
      {/* Floating button */}
      <button
        className={`${styles.floatingButton} ${isOpen ? styles.hidden : ''}`}
        onClick={() => setIsOpen(true)}
        aria-label="Open chatbot"
      >
        <MessageCircle size={24} />
      </button>

      {/* Chat window */}
      <div className={`${styles.chatWindow} ${isOpen ? styles.open : ''}`}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerTitle}>
            <MessageCircle size={20} />
            <span>AI Assistant</span>
          </div>
          <div className={styles.headerActions}>
            <button
              className={styles.iconButton}
              onClick={toggleLanguage}
              title={`Switch to ${language === 'en' ? 'Urdu' : 'English'}`}
            >
              <Globe size={18} />
              <span className={styles.langLabel}>{language.toUpperCase()}</span>
            </button>
            <button
              className={styles.iconButton}
              onClick={clearConversation}
              title="Clear conversation"
            >
              <Trash2 size={18} />
            </button>
            <button
              className={styles.iconButton}
              onClick={() => setIsOpen(false)}
              title="Close"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className={styles.messagesContainer}>
          {messages.length === 0 ? (
            <div className={styles.emptyState}>
              <MessageCircle size={48} className={styles.emptyIcon} />
              <p>Ask me anything about robotics, ROS 2, or this course!</p>
              <div className={styles.suggestedQuestions}>
                <button onClick={() => sendMessage('What are ROS 2 topics?')}>
                  What are ROS 2 topics?
                </button>
                <button onClick={() => sendMessage('How does NVIDIA Isaac work?')}>
                  How does NVIDIA Isaac work?
                </button>
                <button onClick={() => sendMessage('Explain URDF format')}>
                  Explain URDF format
                </button>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))
          )}

          {/* Loading indicator */}
          {isLoading && (
            <div className={styles.loadingIndicator}>
              <Loader2 size={20} className={styles.spinner} />
              <span>Thinking...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input form */}
        <form className={styles.inputForm} onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={language === 'ur' ? 'اپنا سوال لکھیں...' : 'Type your question...'}
            disabled={isLoading}
            className={styles.input}
            dir={language === 'ur' ? 'rtl' : 'ltr'}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className={styles.sendButton}
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </>
  );
}
