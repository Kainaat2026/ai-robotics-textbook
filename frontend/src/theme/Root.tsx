/**
 * Root - Docusaurus theme wrapper
 *
 * This component wraps the entire application and allows us to:
 * - Add global providers
 * - Include components that should appear on all pages (like ChatbotWidget)
 * - Add global state management
 *
 * Reference: https://docusaurus.io/docs/swizzling#wrapper-your-site-with-root
 */

import React, { useState, useEffect } from 'react';
import ChatbotWidget from '@site/src/components/Chatbot/ChatbotWidget';
import { Language } from '@site/src/components/Chatbot/ChatbotService';
import { AuthProvider } from '@site/src/contexts/AuthContext';
import { LanguageToggle } from '@site/src/components/Translation/LanguageToggle';
import { TextToSpeech } from '@site/src/components/Translation/TextToSpeech';

// Root wrapper component
export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  const [currentLanguage, setCurrentLanguage] = useState<'en' | 'ur'>('en');
  const [pageContent, setPageContent] = useState<string>('');

  const handleLanguageChange = (language: 'en' | 'ur') => {
    setCurrentLanguage(language);
    // Apply RTL class to body for Urdu
    if (language === 'ur') {
      document.documentElement.setAttribute('dir', 'rtl');
      document.body.classList.add('urdu-mode');
    } else {
      document.documentElement.setAttribute('dir', 'ltr');
      document.body.classList.remove('urdu-mode');
    }
  };

  // Extract text content from main article for TTS
  useEffect(() => {
    const updateContent = () => {
      const article = document.querySelector('article.markdown');
      if (article) {
        // Get text content, remove code blocks and UI elements
        const clonedArticle = article.cloneNode(true) as HTMLElement;
        clonedArticle.querySelectorAll('pre, code, .theme-code-block').forEach(el => el.remove());
        setPageContent(clonedArticle.textContent?.trim() || '');
      }
    };

    // Update content when page changes
    updateContent();

    // Observer for dynamic content
    const observer = new MutationObserver(updateContent);
    observer.observe(document.body, { childList: true, subtree: true });

    return () => observer.disconnect();
  }, [currentLanguage]);

  return (
    <AuthProvider>
      {/* Original Docusaurus content */}
      {children}

      {/* Language Toggle + TTS - floating buttons */}
      <div style={{
        position: 'fixed',
        bottom: '100px',
        right: '24px',
        zIndex: 999,
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        alignItems: 'flex-end',
      }}>
        <LanguageToggle
          currentLanguage={currentLanguage}
          onLanguageChange={handleLanguageChange}
        />

        {/* Show TTS button when Urdu is selected and there's content */}
        {currentLanguage === 'ur' && pageContent && (
          <TextToSpeech
            text={pageContent}
            language="ur"
          />
        )}
      </div>

      {/* Global Chatbot Widget - appears on all pages */}
      <ChatbotWidget language={currentLanguage === 'en' ? Language.ENGLISH : Language.URDU} />
    </AuthProvider>
  );
}
