import { Conversation, Message, ConversationSummary } from '../types';
import { getMockResponse, MOCK_CONVERSATIONS } from './mockData';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const USE_MOCK = import.meta.env.VITE_USE_MOCK_API === 'true';

export async function fetchHealth(): Promise<{ status: string; database_connected: boolean }> {
  if (USE_MOCK) return { status: 'HEALTHY (MOCK)', database_connected: true };
  const res = await fetch(`${BASE_URL}/api/v1/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchConversations(): Promise<ConversationSummary[]> {
  if (USE_MOCK) return MOCK_CONVERSATIONS;
  try {
    const res = await fetch(`${BASE_URL}/api/v1/conversations`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.conversations || [];
  } catch (err) {
    console.warn('Could not fetch conversations, falling back to empty list:', err);
    return [];
  }
}

export async function startConversation(prompt?: string, clientRequestId?: string): Promise<Conversation> {
  if (USE_MOCK) {
    const cid = `conv_mock_${Date.now()}`;
    const msgs: Message[] = [];
    if (prompt) {
      msgs.push({
        message_id: `msg_user_${Date.now()}`,
        role: 'user',
        content: prompt,
        status: 'COMPLETED',
        created_at: new Date().toISOString()
      });
      msgs.push(getMockResponse(prompt));
    }
    return {
      conversation_id: cid,
      title: prompt ? prompt.slice(0, 30) : 'New Conversation',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      messages: msgs
    };
  }

  const res = await fetch(`${BASE_URL}/api/v1/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content: prompt, client_request_id: clientRequestId })
  });
  if (!res.ok) throw new Error(`Failed to start conversation: ${res.statusText}`);
  return res.json();
}

export async function getConversation(conversationId: string): Promise<Conversation> {
  if (USE_MOCK) {
    return {
      conversation_id: conversationId,
      title: 'Mock Conversation',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      messages: []
    };
  }

  const res = await fetch(`${BASE_URL}/api/v1/conversations/${conversationId}`);
  if (!res.ok) throw new Error(`Failed to fetch conversation: ${res.statusText}`);
  return res.json();
}

export async function sendMessage(conversationId: string, content: string, clientRequestId?: string): Promise<Message> {
  if (USE_MOCK) {
    return new Promise((resolve) => {
      setTimeout(() => resolve(getMockResponse(content)), 400);
    });
  }

  const res = await fetch(`${BASE_URL}/api/v1/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, client_request_id: clientRequestId })
  });
  if (!res.ok) throw new Error(`Failed to send message: ${res.statusText}`);
  return res.json();
}
