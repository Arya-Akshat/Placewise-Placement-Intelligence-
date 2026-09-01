import React, { useState } from 'react';
import { QueryAttachment } from '../../types';
import { Database, ChevronDown, ChevronUp } from 'lucide-react';

export const EvidencePanel: React.FC<{ attachment: QueryAttachment }> = ({ attachment }) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  return (
    <div className="border border-slate-800/80 rounded-lg overflow-hidden bg-slate-950/40 mt-3 text-xs">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-3 py-2 text-slate-400 hover:text-slate-200 hover:bg-slate-900/40 transition select-none"
      >
        <div className="flex items-center gap-2">
          <Database className="w-3.5 h-3.5 text-emerald-400" />
          <span className="font-semibold">View Analysis Metadata & Source Object</span>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {isOpen && (
        <div className="p-3 border-t border-slate-800/80 bg-slate-950/80 space-y-2 text-slate-300">
          <div>
            <span className="text-slate-500 font-medium">Source Semantic Object: </span>
            <span className="font-mono text-emerald-400">{attachment.source_object}</span>
          </div>
          {attachment.target_metric && (
            <div>
              <span className="text-slate-500 font-medium">Target Metric: </span>
              <span className="font-semibold text-slate-200">{attachment.target_metric}</span>
            </div>
          )}
          {attachment.query_text && (
            <div>
              <span className="text-slate-500 font-medium block mb-1">Governed SQL Query:</span>
              <pre className="p-2.5 rounded bg-slate-900 border border-slate-800 text-slate-300 font-mono text-[11px] overflow-x-auto">
                {attachment.query_text}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
