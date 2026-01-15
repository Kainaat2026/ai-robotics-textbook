/**
 * SelectionHandler - Detects text selection and triggers tooltip display
 *
 * Features:
 * - Monitors mouseup events to detect text selection
 * - Extracts selected text and surrounding context
 * - Triggers SelectionTooltip display
 * - Works with both mouse and touch selections
 */

import React, { useEffect, useCallback, useState } from 'react';
import { SelectionTooltip } from './SelectionTooltip';

interface SelectionHandlerProps {
  chapterId: string;
  children: React.ReactNode;
}

interface SelectionState {
  text: string;
  rect: DOMRect;
  surroundingContext: string;
}

export const SelectionHandler: React.FC<SelectionHandlerProps> = ({
  chapterId,
  children,
}) => {
  const [selection, setSelection] = useState<SelectionState | null>(null);

  /**
   * Get surrounding context (200 chars before and after selection)
   */
  const getSurroundingContext = useCallback((node: Node, offset: number): string => {
    const fullText = node.textContent || '';
    const start = Math.max(0, offset - 200);
    const end = Math.min(fullText.length, offset + 200);
    return fullText.substring(start, end);
  }, []);

  /**
   * Handle text selection
   */
  const handleSelection = useCallback(() => {
    const windowSelection = window.getSelection();

    if (!windowSelection || windowSelection.rangeCount === 0) {
      setSelection(null);
      return;
    }

    const selectedText = windowSelection.toString().trim();

    // Only show tooltip if text is selected (at least 2 chars)
    if (selectedText.length < 2) {
      setSelection(null);
      return;
    }

    // Limit selection length to 500 chars (backend validation)
    if (selectedText.length > 500) {
      setSelection(null);
      return;
    }

    // Get selection bounding rect for tooltip positioning
    const range = windowSelection.getRangeAt(0);
    const rect = range.getBoundingClientRect();

    // Get surrounding context
    const anchorNode = windowSelection.anchorNode;
    const surroundingContext = anchorNode
      ? getSurroundingContext(anchorNode, windowSelection.anchorOffset)
      : '';

    setSelection({
      text: selectedText,
      rect,
      surroundingContext,
    });
  }, [getSurroundingContext]);

  /**
   * Handle click outside to close tooltip
   */
  const handleClickOutside = useCallback((e: MouseEvent) => {
    // Close tooltip if clicking outside the selection
    if (selection) {
      const target = e.target as HTMLElement;
      if (!target.closest('.selection-tooltip')) {
        setSelection(null);
      }
    }
  }, [selection]);

  useEffect(() => {
    // Listen for selection changes
    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('touchend', handleSelection);
    document.addEventListener('click', handleClickOutside);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('touchend', handleSelection);
      document.removeEventListener('click', handleClickOutside);
    };
  }, [handleSelection, handleClickOutside]);

  return (
    <>
      {children}
      {selection && (
        <SelectionTooltip
          selectedText={selection.text}
          selectionRect={selection.rect}
          chapterId={chapterId}
          surroundingContext={selection.surroundingContext}
          onClose={() => setSelection(null)}
        />
      )}
    </>
  );
};
