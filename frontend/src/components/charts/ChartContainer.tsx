import React, { useState } from 'react';
import { QueryAttachment } from '../../types';
import { PlacementBarChart } from './PlacementBarChart';
import { PlacementLineChart } from './PlacementLineChart';
import { PlacementDataTable } from '../tables/PlacementDataTable';
import { KpiCard } from '../analytics/KpiCard';
import { BarChart3, Table, TrendingUp } from 'lucide-react';

export const ChartContainer: React.FC<{ attachment: QueryAttachment }> = ({ attachment }) => {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');
  const rec = attachment.recommended_visualization;
  const tableData = attachment.table_data;

  const showChart = rec === 'BAR' || rec === 'LINE';

  return (
    <div className="w-full my-3">
      {/* KPI Cards */}
      {attachment.kpis && attachment.kpis.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 my-3">
          {attachment.kpis.map((kpi, idx) => (
            <KpiCard key={idx} item={kpi} />
          ))}
        </div>
      )}

      {/* View Toggle Toolbar if both chart and table are available */}
      {showChart && tableData && (
        <div className="flex justify-end gap-1 mb-1">
          <button
            onClick={() => setViewMode('chart')}
            className={`flex items-center gap-1 px-2.5 py-1 text-xs rounded font-medium transition ${
              viewMode === 'chart' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            {rec === 'LINE' ? <TrendingUp className="w-3.5 h-3.5" /> : <BarChart3 className="w-3.5 h-3.5" />}
            Chart View
          </button>
          <button
            onClick={() => setViewMode('table')}
            className={`flex items-center gap-1 px-2.5 py-1 text-xs rounded font-medium transition ${
              viewMode === 'table' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            <Table className="w-3.5 h-3.5" />
            Table View
          </button>
        </div>
      )}

      {/* Render Chart or Table */}
      {viewMode === 'chart' && showChart && tableData ? (
        rec === 'LINE' ? <PlacementLineChart data={tableData} /> : <PlacementBarChart data={tableData} />
      ) : tableData ? (
        <PlacementDataTable data={tableData} />
      ) : null}
    </div>
  );
};
