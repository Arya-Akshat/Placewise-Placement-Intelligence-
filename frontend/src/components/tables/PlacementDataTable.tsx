import React, { useState } from 'react';
import { TableData } from '../../types';
import { formatPercentage, formatLpa, formatNumber } from '../../utils/formatters';
import { ChevronLeft, ChevronRight, ArrowUpDown, Download } from 'lucide-react';

export const PlacementDataTable: React.FC<{ data: TableData }> = ({ data }) => {
  const [sortCol, setSortCol] = useState<string | null>(null);
  const [sortAsc, setSortAsc] = useState<boolean>(true);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const pageSize = 8;

  if (!data || !data.rows || data.rows.length === 0) {
    return <div className="text-sm text-slate-500 italic p-3">No tabular rows available.</div>;
  }

  const handleSort = (colName: string) => {
    if (sortCol === colName) {
      setSortAsc(!sortAsc);
    } else {
      setSortCol(colName);
      setSortAsc(true);
    }
  };

  const sortedRows = [...data.rows].sort((a, b) => {
    if (!sortCol) return 0;
    const valA = a[sortCol];
    const valB = b[sortCol];
    if (valA === valB) return 0;
    if (valA === null || valA === undefined) return 1;
    if (valB === null || valB === undefined) return -1;
    if (typeof valA === 'number' && typeof valB === 'number') {
      return sortAsc ? valA - valB : valB - valA;
    }
    return sortAsc ? String(valA).localeCompare(String(valB)) : String(valB).localeCompare(String(valA));
  });

  const totalPages = Math.ceil(sortedRows.length / pageSize);
  const paginatedRows = sortedRows.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const formatCell = (colName: string, val: any) => {
    if (val === null || val === undefined) return '—';
    const c = colName.toLowerCase();
    if (c.includes('rate') || c.includes('percentage') || c.includes('gap') || c.includes('match') || c.includes('ratio')) {
      if (typeof val === 'number') {
        return c.includes('ratio') ? `${(val * 100).toFixed(1)}%` : formatPercentage(val);
      }
    }
    if (c.includes('ctc') || c.includes('lpa') || c.includes('package') || c.includes('salary')) {
      return formatLpa(val);
    }
    if (typeof val === 'number') {
      return formatNumber(val);
    }
    return String(val);
  };

  const exportCsv = () => {
    const headers = data.columns.map(c => c.display_name).join(',');
    const rows = data.rows.map(r => data.columns.map(c => JSON.stringify(r[c.name] ?? '')).join(',')).join('\n');
    const blob = new Blob([`${headers}\n${rows}`], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `placewise_analytics_${Date.now()}.csv`;
    a.click();
  };

  return (
    <div className="w-full bg-slate-900 border border-slate-800 rounded-xl overflow-hidden my-3 shadow-md">
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-900/90 border-b border-slate-800">
        <div className="text-xs text-slate-400 font-medium">
          {data.truncated ? (
            <span className="text-amber-400 font-semibold">
              Showing {data.rows.length} of {data.total_row_count.toLocaleString()} results (Safely Bounded)
            </span>
          ) : (
            <span>{data.total_row_count.toLocaleString()} Records</span>
          )}
        </div>
        <button
          onClick={exportCsv}
          className="flex items-center gap-1.5 text-xs text-slate-300 hover:text-emerald-400 font-medium px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 transition"
        >
          <Download className="w-3.5 h-3.5" />
          Export CSV
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-950/60 border-b border-slate-800 text-slate-400">
              {data.columns.map(col => (
                <th
                  key={col.name}
                  onClick={() => handleSort(col.name)}
                  className="px-4 py-3 font-semibold cursor-pointer hover:text-emerald-400 select-none transition whitespace-nowrap"
                >
                  <div className="flex items-center gap-1.5">
                    <span>{col.display_name}</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-600" />
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {paginatedRows.map((row, idx) => (
              <tr key={idx} className="hover:bg-slate-800/40 transition">
                {data.columns.map(col => (
                  <td key={col.name} className="px-4 py-2.5 text-slate-200 whitespace-nowrap">
                    {formatCell(col.name, row[col.name])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-2 bg-slate-950/50 border-t border-slate-800 text-xs text-slate-400">
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <div className="flex gap-1">
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              className="p-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              className="p-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
