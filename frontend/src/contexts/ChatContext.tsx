/**
 * Chat Context
 *
 * Provides global chat state and text selection integration.
 * Manages conversation state, chatbot visibility, and text selection actions.
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface TextSelection {
  text: string;
  chapterId: string;
  surroundingContext?: string;
}

interface ChatContextType {
  // Conversation state
  conversationId: string | null;
  setConversationId: (id: string | null) => void;

  // Chatbot visibility
  isChatbotOpen: boolean;
  openChatbot: () => void;
  closeChatbot: () => void;
  toggleChatbot: () => void;

  // Text selection integration (T049)
  selectedText: TextSelection | null;
  setSelectedText: (selection: TextSelection | null) => void;

  // Open chatbot with pre-filled text selection question
  askAboutSelection: (selection: TextSelection) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

interface ChatProviderProps {
  children: ReactNode;
}

export function ChatProvider({ children }: ChatProviderProps): JSX.Element {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const [selectedText, setSelectedText] = useState<TextSelection | null>(null);

  /**
   * Open chatbot
   */
  const openChatbot = (): void => {
    setIsChatbotOpen(true);
  };

  /**
   * Close chatbot
   */
  const closeChatbot = (): void => {
    setIsChatbotOpen(false);
  };

  /**
   * Toggle chatbot visibility
   */
  const toggleChatbot = (): void => {
    setIsChatbotOpen((prev) => !prev);
  };

  /**
   * Open chatbot with text selection context
   * User can ask follow-up questions about selected text
   */
  const askAboutSelection = (selection: TextSelection): void => {
    setSelectedText(selection);
    openChatbot();
  };

  const value: ChatContextType = {
    conversationId,
    setConversationId,
    isChatbotOpen,
    openChatbot,
    closeChatbot,
    toggleChatbot,
    selectedText,
    setSelectedText,
    askAboutSelection,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

/**
 * Hook to use chat context
 */
export function useChat(): ChatContextType {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
