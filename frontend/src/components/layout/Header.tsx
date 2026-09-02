import React from 'react';
import { useChat } from '../../context/ChatContext';
import { useTheme } from '../../context/ThemeContext';
import { Menu, GraduationCap, ShieldCheck, Sun, Moon } from 'lucide-react';

export const Header: React.FC = () => {
  const { toggleSidebar, currentView, setCurrentView } = useChat();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="h-14 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md px-4 flex items-center justify-between sticky top-0 z-20 transition-colors duration-150">
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          aria-label="Toggle navigation sidebar"
          className="md:hidden p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 transition"
        >
          <Menu className="w-4 h-4" />
        </button>
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
            <GraduationCap className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight leading-none">PLACEWISE</h1>
            <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium">Placement Intelligence</span>
          </div>
        </div>
      </div>

      {/* Center Navigation Tabs */}
      <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-1 rounded-xl transition-colors">
        <button
          onClick={() => setCurrentView('dashboard')}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition ${
            currentView === 'dashboard'
              ? 'bg-emerald-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
          }`}
        >
          <span>📊 Dashboard</span>
        </button>
        <button
          onClick={() => setCurrentView('chat')}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition ${
            currentView === 'chat'
              ? 'bg-emerald-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
          }`}
        >
          <span>💬 Genie Chat</span>
        </button>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-[11px] text-slate-600 dark:text-slate-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span>Unity Catalog:</span>
          <span className="font-semibold text-slate-800 dark:text-slate-200">placewise.semantic</span>
        </div>
        <div className="hidden sm:flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/50 text-[11px] text-emerald-700 dark:text-emerald-400 font-medium">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Genie Certified</span>
        </div>

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          aria-label="Toggle light and dark theme"
          className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 transition"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? (
            <Sun className="w-4 h-4 text-amber-400 hover:rotate-45 transition-transform" />
          ) : (
            <Moon className="w-4 h-4 text-slate-700" />
          )}
        </button>
      </div>
    </header>
  );
};
