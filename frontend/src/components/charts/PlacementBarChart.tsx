import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { TableData } from '../../types';

export const PlacementBarChart: React.FC<{ data: TableData }> = ({ data }) => {
  if (!data || !data.rows || data.rows.length === 0) return null;

  // Identify primary X category and numeric Y measure
  const xCol = data.columns.find(c => ['department_code', 'company_name', 'skill_name', 'industry', 'batch_label'].includes(c.name))?.name || data.columns[0].name;
  const yCol = data.columns.find(c => ['placement_rate', 'placements_count', 'average_ctc_lpa', 'job_posting_count', 'placement_rate_change_points'].includes(c.name))?.name || data.columns.find(c => typeof data.rows[0][c.name] === 'number')?.name;

  if (!yCol) return null;

  const chartData = data.rows.slice(0, 10).map(r => ({
    name: String(r[xCol] || ''),
    value: Number(r[yCol] || 0)
  }));

  const yLabel = data.columns.find(c => c.name === yCol)?.display_name || yCol;

  return (
    <div className="w-full h-64 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 my-3 shadow-sm transition-colors">
      <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-2 uppercase tracking-wider">{yLabel} Breakdown</h4>
      <ResponsiveContainer width="100%" height="88%">
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" className="dark:stroke-slate-700" opacity={0.5} />
          <XAxis dataKey="name" stroke="#64748b" className="dark:stroke-slate-400" tick={{ fontSize: 11 }} interval={0} angle={-25} textAnchor="end" />
          <YAxis stroke="#64748b" className="dark:stroke-slate-400" tick={{ fontSize: 11 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f8fafc', fontSize: '12px' }}
            formatter={(val: any) => [`${val}`, yLabel]}
          />
          <Bar dataKey="value" fill="#10b981" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
