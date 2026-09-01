import React from 'react';
import { Message } from '../../types';
import { ChartContainer } from '../charts/ChartContainer';
import { ClarificationPrompt } from './ClarificationPrompt';
import { AgentAnalysis } from './AgentAnalysis';
import { EvidencePanel } from './EvidencePanel';
import { ErrorBoundary } from '../common/ErrorBoundary';
import { useChat } from '../../context/ChatContext';
import { User, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';

export const ChatMessage: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === 'user';
  const { submitMessage, retryLastMessage, isSending } = useChat();

  return (
    <div className={`flex gap-3.5 my-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-emerald-600/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0 mt-0.5 shadow-sm">
          <Sparkles className="w-4 h-4" />
        </div>
      )}

      <div className={`flex flex-col max-w-3xl ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? 'bg-emerald-600 text-white rounded-br-sm shadow-md font-medium'
              : 'bg-slate-900 border border-slate-800 text-slate-100 rounded-tl-sm shadow-md'
          }`}
        >
          {message.content}
        </div>

        {/* Assistant Attachments */}
        {!isUser && (
          <div className="w-full mt-1">
            {message.clarification && (
              <ErrorBoundary>
                <ClarificationPrompt clarification={message.clarification} />
              </ErrorBoundary>
            )}

            {message.agent_analysis && (
              <ErrorBoundary>
                <AgentAnalysis analysis={message.agent_analysis} />
              </ErrorBoundary>
            )}

            {message.attachment && (
              <ErrorBoundary>
                <ChartContainer attachment={message.attachment} />
                <EvidencePanel attachment={message.attachment} />
              </ErrorBoundary>
            )}

            {message.status === 'FAILED' && (
              <div className="flex items-center gap-2 mt-2 text-xs text-red-400">
                <AlertCircle className="w-4 h-4" />
                <span>Failed to complete query.</span>
                <button
                  disabled={isSending}
                  onClick={retryLastMessage}
                  className="flex items-center gap-1 font-semibold text-red-300 hover:text-white underline ml-1"
                >
                  <RefreshCw className="w-3 h-3" /> Retry
                </button>
              </div>
            )}

            {/* Follow-up suggestions */}
            {message.follow_up_suggestions && message.follow_up_suggestions.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-3">
                {message.follow_up_suggestions.map((sug, i) => (
                  <button
                    key={i}
                    disabled={isSending}
                    onClick={() => submitMessage(sug)}
                    className="px-2.5 py-1 rounded-full bg-slate-800/80 hover:bg-slate-700 border border-slate-700/80 text-xs text-slate-300 hover:text-emerald-300 transition disabled:opacity-50"
                  >
                    {sug}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-0.5 shadow-sm">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
};
