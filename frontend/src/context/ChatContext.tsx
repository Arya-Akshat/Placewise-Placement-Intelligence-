import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Message, ConversationSummary, ApiError } from '../types';
import * as api from '../services/placewiseApi';

interface ChatContextType {
  currentConversationId: string | null;
  conversations: ConversationSummary[];
  messages: Message[];
  isLoading: boolean;
  isSending: boolean;
  error: string | null;
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  newConversation: () => void;
  selectConversation: (id: string) => Promise<void>;
  submitMessage: (content: string) => Promise<void>;
  submitClarification: (value: string) => Promise<void>;
  retryLastMessage: () => Promise<void>;
  clearError: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);

  const loadConversations = useCallback(async () => {
    try {
      const list = await api.fetchConversations();
      setConversations(list);
    } catch (err) {
      console.error('Error fetching conversation summaries:', err);
    }
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const toggleSidebar = () => setIsSidebarOpen(prev => !prev);

  const newConversation = () => {
    setCurrentConversationId(null);
    setMessages([]);
    setError(null);
  };

  const selectConversation = async (id: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const conv = await api.getConversation(id);
      setCurrentConversationId(conv.conversation_id);
      setMessages(conv.messages || []);
      if (window.innerWidth < 768) {
        setIsSidebarOpen(false);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  };

  const submitMessage = async (content: string) => {
    if (!content.trim() || isSending) return;
    setIsSending(true);
    setError(null);

    const clientReqId = `req_${Date.now()}`;
    const userMsg: Message = {
      message_id: `msg_user_${Date.now()}`,
      role: 'user',
      content: content.trim(),
      status: 'COMPLETED',
      created_at: new Date().toISOString(),
      client_request_id: clientReqId
    };

    setMessages(prev => [...prev, userMsg]);

    try {
      if (!currentConversationId) {
        const newConv = await api.startConversation(content.trim(), clientReqId);
        setCurrentConversationId(newConv.conversation_id);
        setMessages(newConv.messages || []);
        loadConversations();
      } else {
        const asstMsg = await api.sendMessage(currentConversationId, content.trim(), clientReqId);
        setMessages(prev => [...prev, asstMsg]);
        loadConversations();
      }
    } catch (err: any) {
      setError(err.message || 'Error executing placement intelligence query.');
      setMessages(prev => [
        ...prev,
        {
          message_id: `msg_err_${Date.now()}`,
          role: 'assistant',
          content: 'An error occurred while connecting to Placewise Placement Intelligence. Please verify network connectivity and retry.',
          status: 'FAILED',
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const submitClarification = async (value: string) => {
    await submitMessage(value);
  };

  const retryLastMessage = async () => {
    const lastUserMsg = [...messages].reverse().find(m => m.role === 'user');
    if (lastUserMsg) {
      // Remove failed assistant message if present
      setMessages(prev => prev.filter(m => m.status !== 'FAILED'));
      await submitMessage(lastUserMsg.content);
    }
  };

  const clearError = () => setError(null);

  return (
    <ChatContext.Provider
      value={{
        currentConversationId,
        conversations,
        messages,
        isLoading,
        isSending,
        error,
        isSidebarOpen,
        toggleSidebar,
        newConversation,
        selectConversation,
        submitMessage,
        submitClarification,
        retryLastMessage,
        clearError
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) throw new Error('useChat must be used within a ChatProvider');
  return context;
};
