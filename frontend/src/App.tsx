import React from 'react';
import { ChatProvider } from './context/ChatContext';
import { AppLayout } from './components/layout/AppLayout';
import { ChatPage } from './pages/ChatPage';

export const App: React.FC = () => {
  return (
    <ChatProvider>
      <AppLayout>
        <ChatPage />
      </AppLayout>
    </ChatProvider>
  );
};
