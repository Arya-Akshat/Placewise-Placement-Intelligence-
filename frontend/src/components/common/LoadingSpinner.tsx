import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner: React.FC<{ label?: string }> = ({ label = 'Analyzing placement data...' }) => {
  return (
    <div className="flex items-center gap-3 text-slate-400 text-sm py-2 px-1">
      <Loader2 className="w-4 h-4 text-emerald-500 animate-spin" />
      <span className="font-medium animate-pulse">{label}</span>
    </div>
  );
};
