import React from 'react';
import { ClarificationPayload } from '../../types';
import { useChat } from '../../context/ChatContext';
import { HelpCircle } from 'lucide-react';

export const ClarificationPrompt: React.FC<{ clarification: ClarificationPayload }> = ({ clarification }) => {
  const { submitClarification, isSending } = useChat();

  return (
    <div className="bg-amber-950/30 border border-amber-800/60 rounded-xl p-4 my-3 text-slate-200">
      <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm mb-2">
        <HelpCircle className="w-4 h-4" />
        <span>Clarification Required</span>
      </div>
      <p className="text-xs text-slate-300 mb-3">{clarification.prompt}</p>
      <div className="flex flex-wrap gap-2">
        {clarification.options.map(opt => (
          <button
            key={opt.id}
            disabled={isSending}
            onClick={() => submitClarification(opt.value)}
            className="px-3 py-1.5 rounded-lg bg-amber-900/40 hover:bg-amber-800/60 border border-amber-700/60 text-xs font-medium text-amber-200 hover:text-white transition disabled:opacity-50"
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
};
