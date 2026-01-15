/**
 * DocItem Theme Override - Integrates Text Selection AI
 *
 * Wraps default DocItem with SelectionHandler to enable text selection explanations
 */

import React from 'react';
import DocItem from '@theme-original/DocItem';
import { SelectionHandler } from '@site/src/components/TextSelection/SelectionHandler';

export default function DocItemWrapper(props: any) {
  // Get chapter ID from props metadata
  const chapterId = props?.content?.metadata?.id || '';

  return (
    <SelectionHandler chapterId={chapterId}>
      <DocItem {...props} />
    </SelectionHandler>
  );
}
