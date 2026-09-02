import React from 'react';
import { useChat } from '../../context/ChatContext';
import { GraduationCap, Building2, Cpu, Users, Award, TrendingUp } from 'lucide-react';

export const EmptyState: React.FC = () => {
  const { submitMessage, isSending } = useChat();

  const prompts = [
    {
      icon: GraduationCap,
      category: 'Placement Benchmarks',
      prompt: 'What is the placement rate for CSE in 2024?',
      subtext: 'Department eligibility, placements & batch rate'
    },
    {
      icon: Building2,
      category: 'Recruiter Analytics',
      prompt: 'Which companies hired the most students?',
      subtext: 'Volume, package ranges & conversion'
    },
    {
      icon: Cpu,
      category: 'Skill Market',
      prompt: 'What are the top 10 demanded skills?',
      subtext: 'Recruiter demand vs student supply gaps'
    },
    {
      icon: Users,
      category: 'Student Discovery',
      prompt: 'Show high-readiness students without offers',
      subtext: 'Top unplaced candidates with strong capability'
    },
    {
      icon: Award,
      category: 'Candidate Matching',
      prompt: 'Find the best candidates for Data Engineering',
      subtext: 'Ranked by readiness, skills & mandatory gates'
    },
    {
      icon: TrendingUp,
      category: 'Historical Trends',
      prompt: 'Which departments improved placement rate?',
      subtext: 'Year-over-year percentage point analysis'
    }
  ];

  return (
    <div className="flex flex-col items-center justify-center max-w-3xl mx-auto py-12 px-4 text-center transition-colors">
      <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400 mb-4 shadow-inner">
        <GraduationCap className="w-7 h-7" />
      </div>
      <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">Placewise Placement Intelligence</h2>
      <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 max-w-lg leading-relaxed">
        Conversational intelligence powered by Databricks Genie and governed semantic placement models. Ask any institutional or recruiting analytics question below.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-8 w-full text-left">
        {prompts.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              disabled={isSending}
              onClick={() => submitMessage(item.prompt)}
              className="p-3.5 rounded-xl bg-white dark:bg-slate-900/80 hover:bg-slate-50 dark:hover:bg-slate-800/80 border border-slate-200 dark:border-slate-800 hover:border-emerald-500/40 transition group shadow-sm flex flex-col justify-between text-left"
            >
              <div className="flex items-center gap-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400 mb-1">
                <Icon className="w-3.5 h-3.5" />
                <span>{item.category}</span>
              </div>
              <span className="text-xs font-medium text-slate-800 dark:text-slate-200 group-hover:text-slate-950 dark:group-hover:text-white transition">
                "{item.prompt}"
              </span>
              <span className="text-[11px] text-slate-500 dark:text-slate-500 mt-1">{item.subtext}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
