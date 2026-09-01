import React, { useState } from 'react';
import { AgentAnalysisData } from '../../types';
import { BrainCircuit, CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react';

export const AgentAnalysis: React.FC<{ analysis: AgentAnalysisData }> = ({ analysis }) => {
  const [showEvidence, setShowEvidence] = useState<boolean>(true);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 my-3 shadow-md">
      <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm mb-3">
        <BrainCircuit className="w-4 h-4" />
        <span>Executive Analysis & Key Findings</span>
      </div>

      <p className="text-xs text-slate-200 leading-relaxed mb-3 bg-slate-950/60 p-3 rounded-lg border border-slate-800">
        {analysis.summary}
      </p>

      {analysis.findings && analysis.findings.length > 0 && (
        <div className="space-y-1.5 mb-3">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Key Observed Drivers:</span>
          {analysis.findings.map((f, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-slate-300">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
              <span>{f}</span>
            </div>
          ))}
        </div>
      )}

      {analysis.evidence && analysis.evidence.length > 0 && (
        <div className="mt-3 pt-3 border-t border-slate-800">
          <button
            onClick={() => setShowEvidence(!showEvidence)}
            className="flex items-center justify-between w-full text-xs font-semibold text-slate-400 hover:text-slate-200 mb-2"
          >
            <span>Evidence Cards ({analysis.evidence.length})</span>
            {showEvidence ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showEvidence && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
              {analysis.evidence.map((ev, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                  <div className="flex justify-between items-baseline mb-1">
                    <span className="text-xs font-semibold text-slate-300">{ev.title}</span>
                    <span className="text-xs font-bold text-emerald-400">{ev.value}</span>
                  </div>
                  <p className="text-[11px] text-slate-400">{ev.description}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
