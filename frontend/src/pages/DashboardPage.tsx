import React, { useState, useEffect } from 'react';
import { useChat } from '../context/ChatContext';
import { fetchAnalyticsOverview } from '../services/placewiseApi';
import { KpiCard } from '../components/analytics/KpiCard';
import { PlacementBarChart } from '../components/charts/PlacementBarChart';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { 
  GraduationCap, 
  Building2, 
  Cpu, 
  Award, 
  ArrowUpRight, 
  Sparkles, 
  AlertTriangle,
  RefreshCw,
  Search
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { submitMessage, setCurrentView } = useChat();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'departments' | 'companies' | 'skills' | 'candidates'>('departments');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const loadData = async () => {
    setIsLoading(true);
    try {
      const res = await fetchAnalyticsOverview();
      setData(res);
    } catch (err) {
      console.error('Failed to load analytics overview:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAskGenie = (prompt: string) => {
    setCurrentView('chat');
    submitMessage(prompt);
  };

  if (isLoading || !data) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <LoadingSpinner label="Loading placement intelligence analytics..." />
        </div>
      </div>
    );
  }

  // Build chart TableData for Department breakdown
  const deptChartData = {
    columns: [
      { name: 'department_code', type_text: 'STRING', display_name: 'Department' },
      { name: 'placement_rate', type_text: 'DOUBLE', display_name: 'Placement Rate (%)' }
    ],
    rows: data.departments.map((d: any) => ({
      department_code: d.department_code,
      placement_rate: d.placement_rate
    })),
    total_row_count: data.departments.length,
    truncated: false
  };

  // Filter lists based on search
  const filteredDepartments = data.departments.filter((d: any) => 
    d.department_name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    d.department_code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredCompanies = data.top_companies.filter((c: any) =>
    c.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.industry.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredSkills = data.skills.filter((s: any) =>
    s.skill_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.skill_category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredCandidates = data.candidates.filter((c: any) =>
    c.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.department_code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 max-w-7xl mx-auto w-full transition-colors">
      {/* Dashboard Top Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800/80">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <span>Executive Placement Intelligence Dashboard</span>
            <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30">
              Live Governed
            </span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Grounded directly in Unity Catalog (<code className="text-emerald-600 dark:text-emerald-400 font-mono">placewise.semantic.*</code>) • Batch 2024
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadData}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs text-slate-700 dark:text-slate-300 transition shadow-sm"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => handleAskGenie('Give me an executive summary of placement trends.')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white shadow-sm transition"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Ask Genie AI</span>
          </button>
        </div>
      </div>

      {/* Top Level Metric KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 md:gap-4">
        {data.kpis.map((item: any, idx: number) => (
          <KpiCard key={idx} item={item} />
        ))}
      </div>

      {/* Domain Tabs Navigation */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-2">
        <div className="flex items-center gap-1.5 bg-slate-200/70 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 p-1 rounded-xl transition-colors">
          <button
            onClick={() => setActiveTab('departments')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'departments'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-white/50 dark:hover:bg-slate-800/50'
            }`}
          >
            <GraduationCap className="w-3.5 h-3.5" />
            <span>Departments</span>
          </button>
          <button
            onClick={() => setActiveTab('companies')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'companies'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-white/50 dark:hover:bg-slate-800/50'
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>Top Recruiters</span>
          </button>
          <button
            onClick={() => setActiveTab('skills')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'skills'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-white/50 dark:hover:bg-slate-800/50'
            }`}
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>Skill Market</span>
          </button>
          <button
            onClick={() => setActiveTab('candidates')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'candidates'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-white/50 dark:hover:bg-slate-800/50'
            }`}
          >
            <Award className="w-3.5 h-3.5" />
            <span>Candidate Finder</span>
          </button>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Filter current view..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-emerald-500/60 shadow-sm transition-colors"
          />
        </div>
      </div>

      {/* TAB 1: DEPARTMENTS */}
      {activeTab === 'departments' && (
        <div className="space-y-4">
          <PlacementBarChart data={deptChartData} />

          <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm transition-colors">
            <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider">
                Department Performance Matrix (AY 2023–24)
              </h3>
              <span className="text-[11px] text-slate-500 dark:text-slate-400">{filteredDepartments.length} Departments</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
                <thead className="bg-slate-50 dark:bg-slate-950/60 text-slate-500 dark:text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-200 dark:border-slate-800">
                  <tr>
                    <th className="py-2.5 px-4">Code</th>
                    <th className="py-2.5 px-4">Department</th>
                    <th className="py-2.5 px-4">Placement Rate</th>
                    <th className="py-2.5 px-4">Placed / Eligible</th>
                    <th className="py-2.5 px-4">Avg CTC</th>
                    <th className="py-2.5 px-4">YoY Change</th>
                    <th className="py-2.5 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60 font-mono text-[11px]">
                  {filteredDepartments.map((dept: any, idx: number) => {
                    const isPositive = dept.placement_rate_change_points >= 0;
                    return (
                      <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                        <td className="py-2.5 px-4 font-bold text-emerald-600 dark:text-emerald-400">{dept.department_code}</td>
                        <td className="py-2.5 px-4 text-slate-900 dark:text-slate-100 font-sans">{dept.department_name}</td>
                        <td className="py-2.5 px-4 font-bold">{dept.placement_rate}%</td>
                        <td className="py-2.5 px-4 text-slate-500 dark:text-slate-400">{dept.placed_students} / {dept.eligible_students}</td>
                        <td className="py-2.5 px-4 text-slate-800 dark:text-slate-200 font-sans">₹{dept.average_ctc_lpa} LPA</td>
                        <td className="py-2.5 px-4 font-bold">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] ${isPositive ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-rose-500/10 text-rose-600 dark:text-rose-400'}`}>
                            {isPositive ? `+${dept.placement_rate_change_points}` : dept.placement_rate_change_points} pp
                          </span>
                        </td>
                        <td className="py-2.5 px-4 text-right">
                          <button
                            onClick={() => handleAskGenie(`What is the placement performance and trend for ${dept.department_code}?`)}
                            className="inline-flex items-center gap-1 text-[10px] text-emerald-600 dark:text-emerald-400 hover:text-emerald-500 underline font-sans"
                          >
                            <span>Analyze</span>
                            <ArrowUpRight className="w-3 h-3" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: TOP RECRUITERS */}
      {activeTab === 'companies' && (
        <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm transition-colors">
          <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider">
              Top Corporate Hiring Partners
            </h3>
            <span className="text-[11px] text-slate-500 dark:text-slate-400">{filteredCompanies.length} Employers</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
              <thead className="bg-slate-50 dark:bg-slate-950/60 text-slate-500 dark:text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="py-2.5 px-4">Company Name</th>
                  <th className="py-2.5 px-4">Industry</th>
                  <th className="py-2.5 px-4">Type</th>
                  <th className="py-2.5 px-4">Placements</th>
                  <th className="py-2.5 px-4">Avg CTC</th>
                  <th className="py-2.5 px-4">Interview Conversion</th>
                  <th className="py-2.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60 font-mono text-[11px]">
                {filteredCompanies.map((comp: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                    <td className="py-2.5 px-4 font-bold text-slate-900 dark:text-slate-100 font-sans">{comp.company_name}</td>
                    <td className="py-2.5 px-4 text-slate-500 dark:text-slate-400 font-sans">{comp.industry}</td>
                    <td className="py-2.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[10px] text-slate-700 dark:text-slate-300 font-sans">
                        {comp.company_type}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 font-bold text-emerald-600 dark:text-emerald-400">{comp.placements_count}</td>
                    <td className="py-2.5 px-4 text-slate-800 dark:text-slate-200 font-sans">₹{comp.average_ctc_lpa} LPA</td>
                    <td className="py-2.5 px-4 text-slate-700 dark:text-slate-300">{comp.interview_to_offer_rate}%</td>
                    <td className="py-2.5 px-4 text-right">
                      <button
                        onClick={() => handleAskGenie(`Show hiring breakdown and roles for ${comp.company_name}.`)}
                        className="inline-flex items-center gap-1 text-[10px] text-emerald-600 dark:text-emerald-400 hover:text-emerald-500 underline font-sans"
                      >
                        <span>Details</span>
                        <ArrowUpRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: SKILL MARKET */}
      {activeTab === 'skills' && (
        <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm transition-colors">
          <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider">
              Recruiter Skill Demand & Supply Gaps
            </h3>
            <span className="text-[11px] text-slate-500 dark:text-slate-400">{filteredSkills.length} Technical Skills</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
              <thead className="bg-slate-50 dark:bg-slate-950/60 text-slate-500 dark:text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="py-2.5 px-4">Skill / Technology</th>
                  <th className="py-2.5 px-4">Category</th>
                  <th className="py-2.5 px-4">Job Postings</th>
                  <th className="py-2.5 px-4">Market Demand</th>
                  <th className="py-2.5 px-4">Student Supply</th>
                  <th className="py-2.5 px-4">Gap Status</th>
                  <th className="py-2.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60 font-mono text-[11px]">
                {filteredSkills.map((sk: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                    <td className="py-2.5 px-4 font-bold text-slate-900 dark:text-slate-100 font-sans">{sk.skill_name}</td>
                    <td className="py-2.5 px-4 text-slate-500 dark:text-slate-400 font-sans">{sk.skill_category}</td>
                    <td className="py-2.5 px-4 font-bold text-emerald-600 dark:text-emerald-400">{sk.job_posting_count}</td>
                    <td className="py-2.5 px-4 text-slate-800 dark:text-slate-200">{sk.market_demand_ratio}%</td>
                    <td className="py-2.5 px-4 text-slate-700 dark:text-slate-300">{sk.student_supply_ratio}%</td>
                    <td className="py-2.5 px-4 font-sans">
                      {sk.high_demand_low_supply_flag ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/30 text-[10px] font-semibold">
                          <AlertTriangle className="w-2.5 h-2.5" />
                          High Gap
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-[10px]">
                          Balanced
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      <button
                        onClick={() => handleAskGenie(`Which companies are demanding ${sk.skill_name}?`)}
                        className="inline-flex items-center gap-1 text-[10px] text-emerald-600 dark:text-emerald-400 hover:text-emerald-500 underline font-sans"
                      >
                        <span>Analyze</span>
                        <ArrowUpRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: CANDIDATE FINDER */}
      {activeTab === 'candidates' && (
        <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm transition-colors">
          <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider">
              High Placement Readiness Candidate Directory
            </h3>
            <span className="text-[11px] text-slate-500 dark:text-slate-400">{filteredCandidates.length} Candidates</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
              <thead className="bg-slate-50 dark:bg-slate-950/60 text-slate-500 dark:text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="py-2.5 px-4">Student ID</th>
                  <th className="py-2.5 px-4">Candidate Name</th>
                  <th className="py-2.5 px-4">Dept</th>
                  <th className="py-2.5 px-4">CGPA</th>
                  <th className="py-2.5 px-4">Readiness Score</th>
                  <th className="py-2.5 px-4">Readiness Band</th>
                  <th className="py-2.5 px-4">Placement Status</th>
                  <th className="py-2.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60 font-mono text-[11px]">
                {filteredCandidates.map((cand: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                    <td className="py-2.5 px-4 text-slate-500 dark:text-slate-400">{cand.student_id}</td>
                    <td className="py-2.5 px-4 font-bold text-slate-900 dark:text-slate-100 font-sans">{cand.full_name}</td>
                    <td className="py-2.5 px-4 text-emerald-600 dark:text-emerald-400">{cand.department_code}</td>
                    <td className="py-2.5 px-4">{cand.cgpa}</td>
                    <td className="py-2.5 px-4 font-bold text-emerald-600 dark:text-emerald-300">{cand.placement_readiness_score} / 100</td>
                    <td className="py-2.5 px-4 font-sans">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        cand.readiness_band === 'EXCELLENT' ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400' : 'bg-blue-500/20 text-blue-600 dark:text-blue-400'
                      }`}>
                        {cand.readiness_band}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 font-sans text-slate-500 dark:text-slate-400">{cand.placement_status}</td>
                    <td className="py-2.5 px-4 text-right">
                      <button
                        onClick={() => handleAskGenie(`Find suitable job postings for student ${cand.student_id}.`)}
                        className="inline-flex items-center gap-1 text-[10px] text-emerald-600 dark:text-emerald-400 hover:text-emerald-500 underline font-sans"
                      >
                        <span>Match</span>
                        <ArrowUpRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
