import React, { useEffect, useRef } from 'react';
import { useChat } from '../context/ChatContext';
import { ChatMessage } from '../components/chat/ChatMessage';
import { EmptyState } from '../components/chat/EmptyState';
import { Composer } from '../components/chat/Composer';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const ChatPage: React.FC = () => {
  const { messages, isSending } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  return (
    <div className="flex flex-col flex-1 h-full justify-between">
      <div className="max-w-4xl w-full mx-auto px-4 py-6 flex-1">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          <div>
            {messages.map(msg => (
              <ChatMessage key={msg.message_id} message={msg} />
            ))}
            {isSending && <LoadingSpinner />}
            <div ref={bottomRef} />
          </div>
        )}
      </div>
      <Composer />
    </div>
  );
};
