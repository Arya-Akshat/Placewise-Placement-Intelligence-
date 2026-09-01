import React from 'react';
import { useChat } from '../../context/ChatContext';
import { Plus, MessageSquare, GraduationCap, Building2, Cpu, Award, TrendingUp, X } from 'lucide-react';
import { formatRelativeTime } from '../../utils/formatters';

export const Sidebar: React.FC = () => {
  const {
    conversations,
    currentConversationId,
    selectConversation,
    newConversation,
    isSidebarOpen,
    toggleSidebar,
    submitMessage,
    isSending
  } = useChat();

  const domains = [
    { label: 'Placement Rate', prompt: 'What is the placement rate by department?', icon: GraduationCap },
    { label: 'Top Recruiters', prompt: 'Which companies hired the most students?', icon: Building2 },
    { label: 'Skill Market', prompt: 'What are the top demanded skills?', icon: Cpu },
    { label: 'Candidate Match', prompt: 'Find the best candidates for Data Engineering', icon: Award },
    { label: 'Batch Trends', prompt: 'Which departments improved placement rate?', icon: TrendingUp }
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isSidebarOpen && (
        <div
          onClick={toggleSidebar}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 md:hidden"
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 z-40 w-64 bg-slate-950 border-r border-slate-800 flex flex-col justify-between transition-transform duration-200 ease-in-out ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="p-3">
          <div className="flex items-center justify-between md:hidden mb-2">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Navigation</span>
            <button onClick={toggleSidebar} className="p-1 rounded text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>

          <button
            onClick={newConversation}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs shadow-md transition"
          >
            <Plus className="w-4 h-4" />
            <span>New Conversation</span>
          </button>

          {/* Quick Analysis Domains */}
          <div className="mt-5">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-2 block mb-2">
              Analysis Domains
            </span>
            <div className="space-y-1">
              {domains.map((d, i) => {
                const Icon = d.icon;
                return (
                  <button
                    key={i}
                    disabled={isSending}
                    onClick={() => submitMessage(d.prompt)}
                    className="w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-xs text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition text-left"
                  >
                    <Icon className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span className="truncate">{d.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Recent Conversations */}
          <div className="mt-6">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-2 block mb-2">
              Recent Conversations
            </span>
            <div className="space-y-1 max-h-60 overflow-y-auto pr-1">
              {conversations.length === 0 ? (
                <span className="text-xs text-slate-600 px-2 italic">No previous chats</span>
              ) : (
                conversations.map(c => (
                  <button
                    key={c.conversation_id}
                    onClick={() => selectConversation(c.conversation_id)}
                    className={`w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs text-left transition ${
                      currentConversationId === c.conversation_id
                        ? 'bg-slate-800 text-emerald-300 font-semibold'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <MessageSquare className="w-3.5 h-3.5 shrink-0" />
                      <span className="truncate">{c.title}</span>
                    </div>
                    <span className="text-[10px] text-slate-600 ml-1 shrink-0">
                      {formatRelativeTime(c.updated_at)}
                    </span>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-950 text-[11px] text-slate-500">
          <div className="flex items-center justify-between">
            <span>Placewise v2.0</span>
            <span className="text-emerald-500 font-mono">ONLINE</span>
          </div>
        </div>
      </aside>
    </>
  );
};
