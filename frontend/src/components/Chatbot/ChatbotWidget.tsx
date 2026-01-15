/**
 * ChatbotWidget - Floating chatbot button and container
 *
 * Features:
 * - Floating action button (bottom-right corner)
 * - Toggle open/close state
 * - Notification badge (optional)
 * - Responsive positioning
 */

import React, { useState } from 'react';
import ChatbotInterface from './ChatbotInterface';
import { Language } from './ChatbotService';
import styles from './ChatbotWidget.module.css';

interface ChatbotWidgetProps {
  /** Default language for chatbot */
  language?: Language;
  /** Initial open state */
  initialOpen?: boolean;
}

export default function ChatbotWidget({
  language = Language.ENGLISH,
  initialOpen = false,
}: ChatbotWidgetProps): JSX.Element {
  const [isOpen, setIsOpen] = useState(initialOpen);

  /**
   * Toggle chatbot open/close
   */
  const toggleChatbot = () => {
    setIsOpen((prev) => !prev);
  };

  return (
    <>
      {/* Chatbot Interface */}
      <div
        className={`${styles.chatbotWrapper} ${isOpen ? styles.open : ''}`}
        aria-hidden={!isOpen}
      >
        <ChatbotInterface
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          language={language}
        />
      </div>

      {/* Floating Action Button */}
      {!isOpen && (
        <button
          className={styles.floatingButton}
          onClick={toggleChatbot}
          aria-label="Open chatbot"
          title="Ask AI Assistant"
        >
          <span className={styles.buttonIcon}>🤖</span>
          <span className={styles.buttonLabel}>Ask AI</span>
        </button>
      )}
    </>
  );
}
