/**
 * Root component wrapper for Docusaurus
 * This wraps the entire application and allows us to add global components
 */
import React from 'react';
import { AuthProvider } from '../contexts/AuthContext';
import ChatbotWidget from '../components/ChatbotWidget';
import ChapterToolbar from '../components/ChapterToolbar';
import TranslationToolbar from '../components/TranslationToolbar';

export default function Root({ children }) {
  return (
    <AuthProvider>
      <TranslationToolbar />
      {children}
      <ChapterToolbar />
      <ChatbotWidget />
    </AuthProvider>
  );
}
