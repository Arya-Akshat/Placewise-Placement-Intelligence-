import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { TableData } from '../../types';

export const PlacementLineChart: React.FC<{ data: TableData }> = ({ data }) => {
  if (!data || !data.rows || data.rows.length === 0) return null;

  const xCol = data.columns.find(c => ['graduation_year', 'admission_year'].includes(c.name))?.name || data.columns[0].name;
  const yCol = data.columns.find(c => ['placement_rate', 'average_ctc_lpa'].includes(c.name))?.name || data.columns.find(c => typeof data.rows[0][c.name] === 'number')?.name;

  if (!yCol) return null;

  const chartData = data.rows.map(r => ({
    name: String(r[xCol] || ''),
    value: Number(r[yCol] || 0)
  }));

  const yLabel = data.columns.find(c => c.name === yCol)?.display_name || yCol;

  return (
    <div className="w-full h-64 bg-slate-900 border border-slate-800 rounded-xl p-4 my-3 shadow-md">
      <h4 className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">{yLabel} Historical Trend</h4>
      <ResponsiveContainer width="100%" height="88%">
        <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
          <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f8fafc', fontSize: '12px' }}
            formatter={(val: any) => [`${val}`, yLabel]}
          />
          <Line type="monotone" dataKey="value" stroke="#38bdf8" strokeWidth={2.5} dot={{ fill: '#38bdf8', r: 4 }} activeDot={{ r: 6 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
