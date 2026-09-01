import React from 'react';
import { KpiItem } from '../../types';

export const KpiCard: React.FC<{ item: KpiItem }> = ({ item }) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-sm">
      <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{item.label}</span>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-2xl font-bold text-slate-100 tracking-tight">{item.value}</span>
        {item.change && (
          <span className={`text-xs font-semibold ${item.change.startsWith('+') ? 'text-emerald-400' : 'text-amber-400'}`}>
            {item.change}
          </span>
        )}
      </div>
      {item.subtext && <span className="text-xs text-slate-500 mt-1">{item.subtext}</span>}
    </div>
  );
};
