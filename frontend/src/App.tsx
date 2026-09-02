import React from 'react';
import { ChatProvider, useChat } from './context/ChatContext';
import { AppLayout } from './components/layout/AppLayout';
import { ChatPage } from './pages/ChatPage';
import { DashboardPage } from './pages/DashboardPage';

const AppContent: React.FC = () => {
  const { currentView } = useChat();
  return (
    <AppLayout>
      {currentView === 'dashboard' ? <DashboardPage /> : <ChatPage />}
    </AppLayout>
  );
};

export const App: React.FC = () => {
  return (
    <ChatProvider>
      <AppContent />
    </ChatProvider>
  );
};
