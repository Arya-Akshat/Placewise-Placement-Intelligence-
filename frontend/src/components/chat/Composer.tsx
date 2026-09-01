import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import { Send, CornerDownLeft } from 'lucide-react';

export const Composer: React.FC = () => {
  const [text, setText] = useState<string>('');
  const { submitMessage, isSending } = useChat();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!isSending && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isSending]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || isSending) return;
    submitMessage(text.trim());
    setText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t border-slate-800/80 bg-slate-950/80 backdrop-blur-md p-4 sticky bottom-0 w-full">
      <div className="max-w-4xl mx-auto">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            disabled={isSending}
            onChange={e => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isSending ? 'Placewise is processing...' : 'Ask Placewise anything about placements, companies, or skills... (Enter to send)'}
            className="w-full bg-slate-900 border border-slate-700/80 focus:border-emerald-500/80 focus:ring-1 focus:ring-emerald-500/80 rounded-xl pl-4 pr-12 py-3 text-sm text-slate-100 placeholder-slate-500 resize-none outline-none transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!text.trim() || isSending}
            aria-label="Send message"
            className="absolute right-2.5 p-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-30 disabled:hover:bg-emerald-600 text-white transition shadow-sm"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2 px-1">
          <span>Grounded in governed Placewise semantic views</span>
          <span className="hidden sm:inline">Shift + Enter for new line</span>
        </div>
      </div>
    </div>
  );
};
