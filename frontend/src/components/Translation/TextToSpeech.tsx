/**
 * TextToSpeech - Read text aloud with browser's speech synthesis
 *
 * Features:
 * - Uses Web Speech API (FREE, built into browsers)
 * - Supports Urdu pronunciation
 * - Play/pause/stop controls
 * - Works on all modern browsers
 */

import React, { useState, useEffect } from 'react';
import styles from './TextToSpeech.module.css';

interface TextToSpeechProps {
  text: string;
  language: 'en' | 'ur';
  autoPlay?: boolean;
}

export const TextToSpeech: React.FC<TextToSpeechProps> = ({
  text,
  language,
  autoPlay = false,
}) => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    // Check if browser supports speech synthesis
    setIsSupported('speechSynthesis' in window);
  }, []);

  useEffect(() => {
    if (autoPlay && isSupported && text) {
      handleSpeak();
    }

    // Cleanup on unmount
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, [autoPlay, text]);

  const handleSpeak = () => {
    if (!isSupported || !text) return;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    // Set language code
    utterance.lang = language === 'ur' ? 'ur-PK' : 'en-US';

    // Configure speech parameters
    utterance.rate = 0.9; // Slightly slower for clarity
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    // Event listeners
    utterance.onstart = () => {
      setIsSpeaking(true);
      setIsPaused(false);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setIsPaused(false);
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setIsSpeaking(false);
      setIsPaused(false);
    };

    window.speechSynthesis.speak(utterance);
  };

  const handlePause = () => {
    if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
      window.speechSynthesis.pause();
      setIsPaused(true);
    }
  };

  const handleResume = () => {
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
    }
  };

  const handleStop = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setIsPaused(false);
  };

  if (!isSupported) {
    return null; // Don't show button if not supported
  }

  return (
    <div className={styles.ttsContainer}>
      {!isSpeaking ? (
        <button
          className={styles.ttsButton}
          onClick={handleSpeak}
          title={language === 'ur' ? 'اردو میں سنیں' : 'Listen'}
          aria-label="Read text aloud"
        >
          <span className={styles.icon}>🔊</span>
          <span className={styles.label}>
            {language === 'ur' ? 'سنیں' : 'Listen'}
          </span>
        </button>
      ) : (
        <div className={styles.controls}>
          {isPaused ? (
            <button
              className={styles.controlButton}
              onClick={handleResume}
              title="Resume"
              aria-label="Resume reading"
            >
              <span className={styles.icon}>▶️</span>
            </button>
          ) : (
            <button
              className={styles.controlButton}
              onClick={handlePause}
              title="Pause"
              aria-label="Pause reading"
            >
              <span className={styles.icon}>⏸️</span>
            </button>
          )}
          <button
            className={styles.controlButton}
            onClick={handleStop}
            title="Stop"
            aria-label="Stop reading"
          >
            <span className={styles.icon}>⏹️</span>
          </button>
        </div>
      )}
    </div>
  );
};
