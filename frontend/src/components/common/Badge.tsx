import React from 'react';
import clsx from 'clsx';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'emerald' | 'blue' | 'amber' | 'purple' | 'red' | 'slate';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'slate', size = 'md' }) => {
  const styles = {
    emerald: 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60',
    blue: 'bg-blue-950/60 text-blue-400 border-blue-800/60',
    amber: 'bg-amber-950/60 text-amber-400 border-amber-800/60',
    purple: 'bg-purple-950/60 text-purple-400 border-purple-800/60',
    red: 'bg-red-950/60 text-red-400 border-red-800/60',
    slate: 'bg-slate-800/80 text-slate-300 border-slate-700'
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium border rounded-full',
        styles[variant],
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs'
      )}
    >
      {children}
    </span>
  );
};
