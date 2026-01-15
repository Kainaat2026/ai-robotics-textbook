/**
 * SelectionTooltip - Floating "Ask AI" button for selected text
 *
 * Features:
 * - Shows "Ask AI" button above selected text
 * - Calls text selection API on click
 * - Displays explanation inline or expands to chatbot
 * - Handles loading and error states
 * - Responsive positioning
 */

import React, { useState, useEffect, useRef } from 'react';
import { chatbotService, Language } from '../Chatbot/ChatbotService';
import type { Citation } from '../Chatbot/ChatbotService';
import styles from './SelectionTooltip.module.css';

interface SelectionTooltipProps {
  selectedText: string;
  selectionRect: DOMRect;
  chapterId: string;
  surroundingContext?: string;
  onClose: () => void;
}

export const SelectionTooltip: React.FC<SelectionTooltipProps> = ({
  selectedText,
  selectionRect,
  chapterId,
  surroundingContext,
  onClose,
}) => {
  const [explanation, setExplanation] = useState<string | null>(null);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  /**
   * Calculate tooltip position (above selection)
   */
  const getTooltipPosition = () => {
    const TOOLTIP_OFFSET = 10; // Pixels above selection

    return {
      top: selectionRect.top + window.scrollY - TOOLTIP_OFFSET,
      left: selectionRect.left + selectionRect.width / 2 + window.scrollX,
    };
  };

  /**
   * Handle "Ask AI" button click
   */
  const handleAskAI = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await chatbotService.explainTextSelection(
        selectedText,
        chapterId,
        surroundingContext,
        Language.ENGLISH
      );

      setExplanation(response.explanation);
      setCitations(response.citations);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to get explanation'
      );
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Auto-position tooltip on mount and scroll
   */
  useEffect(() => {
    const updatePosition = () => {
      if (tooltipRef.current) {
        const pos = getTooltipPosition();
        tooltipRef.current.style.top = `${pos.top}px`;
        tooltipRef.current.style.left = `${pos.left}px`;
      }
    };

    updatePosition();
    window.addEventListener('scroll', updatePosition);
    window.addEventListener('resize', updatePosition);

    return () => {
      window.removeEventListener('scroll', updatePosition);
      window.removeEventListener('resize', updatePosition);
    };
  }, [selectionRect]);

  const position = getTooltipPosition();

  return (
    <div
      ref={tooltipRef}
      className={`selection-tooltip ${styles.tooltip} ${
        explanation ? styles.expanded : ''
      }`}
      style={{
        top: `${position.top}px`,
        left: `${position.left}px`,
      }}
    >
      {!explanation ? (
        // Ask AI Button
        <button
          className={styles.askButton}
          onClick={handleAskAI}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className={styles.spinner}></span>
              Loading...
            </>
          ) : (
            <>
              <svg
                className={styles.icon}
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M8 1a7 7 0 100 14A7 7 0 008 1zm0 3a1 1 0 110 2 1 1 0 010-2zm1 9H7V8h2v5z"
                  fill="currentColor"
                />
              </svg>
              Ask AI
            </>
          )}
        </button>
      ) : (
        // Explanation Display
        <div className={styles.explanation}>
          <div className={styles.header}>
            <span className={styles.selectedText}>"{selectedText}"</span>
            <button className={styles.closeButton} onClick={onClose}>
              ✕
            </button>
          </div>

          {error ? (
            <div className={styles.error}>{error}</div>
          ) : (
            <>
              <div className={styles.explanationText}>{explanation}</div>

              {citations.length > 0 && (
                <div className={styles.citations}>
                  <strong>Sources:</strong>
                  <ul>
                    {citations.map((citation, index) => (
                      <li key={index}>
                        <a href={`/docs/${citation.chapter_id}`}>
                          {citation.title} - {citation.section}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};
