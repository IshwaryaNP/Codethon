import React, { useEffect, useState } from 'react';
import { dashboardApi } from '../api/dashboard';
import { sessionsApi } from '../api/sessions';
import { DashboardData, TriageRecommendation } from '../types';
import {
  Sparkles,
  TrendingUp,
  Clock,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Brain,
  HelpCircle,
  ArrowRight,
  ShieldAlert,
  BarChart3,
  RefreshCw
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, PieChart, Pie } from 'recharts';
import { useNavigate } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [dailySummary, setDailySummary] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [triageModalOpen, setTriageModalOpen] = useState(false);
  const [triageData, setTriageData] = useState<any>(null);
  const [triageLoading, setTriageLoading] = useState(false);
  const navigate = useNavigate();

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const res = await dashboardApi.getSummary();
      setData(res);
      const dailyRes = await dashboardApi.getDailySummary();
      setDailySummary(dailyRes.summary);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleSessionAction = async (sessionId: string, status: 'done' | 'missed', actualMins?: number) => {
    try {
      await sessionsApi.updateStatus(sessionId, status, actualMins);
      // Reload dashboard after automatic replan
      await loadDashboard();
    } catch (err) {
      console.error('Failed to update session:', err);
    }
  };

  const openTriageAnalysis = async () => {
    try {
      setTriageLoading(true);
      setTriageModalOpen(true);
      const feasibility = await sessionsApi.getFeasibility();
      setTriageData(feasibility);
    } catch (err) {
      console.error('Failed to load triage feasibility:', err);
    } finally {
      setTriageLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-sky-600"></div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Pitch Banner & Daily AI Summary */}
      <div className="bg-gradient-to-r from-slate-900 via-sky-950 to-indigo-950 text-white rounded-2xl p-6 shadow-lg border border-slate-800 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
          <Sparkles className="w-48 h-48 text-sky-400" />
        </div>
        <div className="relative z-10">
          <div className="flex items-center gap-2 text-sky-400 font-semibold text-xs uppercase tracking-wider mb-2">
            <Sparkles className="w-4 h-4" /> Daily Adaptive Summary & Pitch
          </div>
          <h1 className="text-xl sm:text-2xl font-black tracking-tight mb-2">
            "We tell you whether you'll be ready for each exam, and re-plan when you won't."
          </h1>
          <p className="text-slate-300 text-sm leading-relaxed max-w-3xl bg-slate-800/60 p-3.5 rounded-xl border border-slate-700/60 mt-3">
            {dailySummary}
          </p>
        </div>
      </div>

      {/* Warnings & Infeasibility Alerts */}
      {data.warnings && data.warnings.length > 0 && (
        <div className="space-y-3">
          {data.warnings.map((warn, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xs ${
                warn.severity === 'critical'
                  ? 'bg-rose-50 border-rose-200 text-rose-900'
                  : 'bg-amber-50 border-amber-200 text-amber-900'
              }`}
            >
              <div className="flex items-start gap-3">
                <ShieldAlert
                  className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                    warn.severity === 'critical' ? 'text-rose-600' : 'text-amber-600'
                  }`}
                />
                <div>
                  <h4 className="font-bold text-sm">{warn.title}</h4>
                  <p className="text-xs opacity-90 leading-normal">{warn.message}</p>
                </div>
              </div>
              {warn.type === 'infeasible_exam' && (
                <button
                  onClick={openTriageAnalysis}
                  className="px-3.5 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-bold shadow-xs flex items-center gap-1.5 whitespace-nowrap transition"
                >
                  <Brain className="w-3.5 h-3.5" /> View Triage Advisor
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Top Key Statistics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Overall Progress</p>
            <h3 className="text-2xl font-black text-slate-900 mt-1">{data.stats.overall_progress_pct}%</h3>
            <p className="text-xs text-slate-500 mt-1">{data.stats.completed_topics} / {data.stats.total_topics} topics completed</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center font-bold">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Weekly Study</p>
            <h3 className="text-2xl font-black text-slate-900 mt-1">{data.stats.weekly_study_hours}h</h3>
            <p className="text-xs text-slate-500 mt-1">Completed last 7 days</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
            <Clock className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Upcoming Exams</p>
            <h3 className="text-2xl font-black text-slate-900 mt-1">{data.stats.upcoming_exams_count}</h3>
            <p className="text-xs text-slate-500 mt-1">Active scheduled exams</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
            <Calendar className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">At Risk Exams</p>
            <h3 className="text-2xl font-black text-rose-600 mt-1">
              {data.exam_readiness.filter(r => !r.feasible || r.status !== 'Ready').length}
            </h3>
            <p className="text-xs text-slate-500 mt-1">Require triage or study boost</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Main Focus Card: EXAM READINESS (Monte Carlo Probability) */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Brain className="w-5 h-5 text-sky-600" /> Exam Readiness Assessment (Monte Carlo 1,000 Runs)
            </h3>
            <p className="text-xs text-slate-500">
              Deterministic probability simulations based on remaining workload, study availability & student velocity.
            </p>
          </div>
          <button
            onClick={openTriageAnalysis}
            className="text-xs font-bold text-sky-600 hover:text-sky-700 underline self-start sm:self-auto"
          >
            Check Feasibility & Triage Advisor
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.exam_readiness.map((exam) => {
            const isReady = exam.status === 'Ready';
            const isAtRisk = exam.status === 'At Risk';
            const isInfeasible = exam.status === 'Infeasible';

            return (
              <div
                key={exam.exam_id}
                className={`p-5 rounded-2xl border transition-all ${
                  isInfeasible
                    ? 'bg-rose-50/50 border-rose-200'
                    : isAtRisk
                    ? 'bg-amber-50/50 border-amber-200'
                    : 'bg-emerald-50/50 border-emerald-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-extrabold text-slate-900 text-sm">{exam.exam_title}</h4>
                    <p className="text-xs text-slate-500 mt-0.5">Exam Date: {exam.exam_date}</p>
                  </div>
                  <span
                    className={`px-2.5 py-1 rounded-full text-[11px] font-black uppercase tracking-wide ${
                      isInfeasible
                        ? 'bg-rose-100 text-rose-800'
                        : isAtRisk
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-emerald-100 text-emerald-800'
                    }`}
                  >
                    {exam.status}
                  </span>
                </div>

                <div className="mt-4 flex items-baseline gap-2">
                  <span
                    className={`text-3xl font-black ${
                      isInfeasible ? 'text-rose-600' : isAtRisk ? 'text-amber-600' : 'text-emerald-600'
                    }`}
                  >
                    {exam.readiness_probability}%
                  </span>
                  <span className="text-xs font-semibold text-slate-600">Readiness Score</span>
                </div>

                <div className="w-full bg-slate-200 rounded-full h-2 mt-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      isInfeasible ? 'bg-rose-600' : isAtRisk ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(100, exam.readiness_probability)}%` }}
                  />
                </div>

                <div className="mt-4 pt-3 border-t border-slate-200/60 grid grid-cols-2 text-xs text-slate-600">
                  <div>
                    <p className="text-[10px] text-slate-400 uppercase font-bold">Required Time</p>
                    <p className="font-semibold text-slate-800">{exam.remaining_hours} hours</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-slate-400 uppercase font-bold">Available Usable</p>
                    <p className="font-semibold text-slate-800">{exam.available_hours} hours</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Grid: Today's Plan & Visual Recharts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Schedule */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Clock className="w-4 h-4 text-sky-600" /> Today's Adaptive Schedule
              </h3>
              <p className="text-xs text-slate-500">Marking sessions complete recalculates velocity & auto replans</p>
            </div>
            <button
              onClick={() => navigate('/calendar')}
              className="text-xs font-bold text-sky-600 hover:text-sky-700 flex items-center gap-1"
            >
              Full Calendar <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          {data.todays_plan.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs">
              No sessions scheduled for today. Enjoy your break or generate a fresh plan!
            </div>
          ) : (
            <div className="space-y-3">
              {data.todays_plan.map((sess) => {
                const isDone = sess.status === 'done';
                const isMissed = sess.status === 'missed';

                return (
                  <div
                    key={sess.id}
                    className={`p-4 rounded-xl border flex items-center justify-between gap-4 transition ${
                      isDone
                        ? 'bg-emerald-50/40 border-emerald-200'
                        : isMissed
                        ? 'bg-rose-50/40 border-rose-200 opacity-75'
                        : 'bg-white border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="w-3 h-10 rounded-full flex-shrink-0"
                        style={{ backgroundColor: sess.subject_color || '#3b82f6' }}
                      />
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-bold text-slate-900 text-sm">{sess.topic_name}</h4>
                          <span
                            className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase ${
                              sess.type === 'revision'
                                ? 'bg-purple-100 text-purple-700'
                                : 'bg-sky-100 text-sky-700'
                            }`}
                          >
                            {sess.type}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {sess.subject_name} • {sess.planned_minutes} mins planned
                          {isDone && ` (${sess.actual_minutes}m actual)`}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {!isDone && !isMissed && (
                        <>
                          <button
                            onClick={() => handleSessionAction(sess.id, 'done', sess.planned_minutes)}
                            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-xs flex items-center gap-1 transition"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" /> Done
                          </button>
                          <button
                            onClick={() => handleSessionAction(sess.id, 'missed')}
                            className="px-2.5 py-1.5 bg-slate-100 hover:bg-rose-100 text-slate-600 hover:text-rose-700 rounded-lg text-xs font-semibold transition"
                          >
                            Missed
                          </button>
                        </>
                      )}
                      {isDone && (
                        <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-lg text-xs font-extrabold flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Completed
                        </span>
                      )}
                      {isMissed && (
                        <span className="px-3 py-1 bg-rose-100 text-rose-800 rounded-lg text-xs font-extrabold flex items-center gap-1">
                          <XCircle className="w-3.5 h-3.5" /> Missed
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Subject Progress Chart */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2 border-b border-slate-100 pb-3">
            <BarChart3 className="w-4 h-4 text-sky-600" /> Subject Workload & Progress
          </h3>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.subject_cards} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                <XAxis type="number" domain={[0, 100]} unit="%" tick={{ fontSize: 11 }} />
                <YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(value: any) => [`${value}%`, 'Progress']} />
                <Bar dataKey="progress_pct" radius={[0, 4, 4, 0]}>
                  {data.subject_cards.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color || '#0284c7'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-100">
            {data.subject_cards.map((sub) => (
              <div key={sub.id} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 truncate">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: sub.color }} />
                  <span className="font-semibold text-slate-700 truncate">{sub.name}</span>
                </div>
                <span className="text-slate-500 font-medium">{sub.estimated_remaining_hours}h left (vel: {sub.velocity})</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Interactive Triage Modal */}
      {triageModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 max-h-[90vh] overflow-y-auto space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-rose-100 text-rose-700 flex items-center justify-center font-bold">
                  <Brain className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-base">Infeasibility & Triage Advisor</h3>
                  <p className="text-xs text-slate-500">Value density ratio (weight / est_hours) recommendation engine</p>
                </div>
              </div>
              <button
                onClick={() => setTriageModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                ✕
              </button>
            </div>

            {triageLoading ? (
              <div className="py-12 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-rose-600 mx-auto"></div>
                <p className="text-xs text-slate-500 mt-2">Analyzing subject workload ratios...</p>
              </div>
            ) : triageData?.triage_recommendations?.length > 0 ? (
              <div className="space-y-4">
                {triageData.triage_recommendations.map((triage: any, idx: number) => (
                  <div key={idx} className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-slate-900 text-sm">{triage.subject_name} Exam Deficit</h4>
                      <span className="px-2.5 py-1 bg-rose-100 text-rose-800 rounded-md text-xs font-black">
                        Deficit: {triage.deficit_hours} Hours
                      </span>
                    </div>

                    <p className="text-xs text-slate-600">{triage.message}</p>

                    <div className="space-y-2">
                      <p className="text-xs font-bold text-slate-700 uppercase tracking-wider">Recommended Adjustments:</p>
                      {triage.recommendations.map((rec: TriageRecommendation, rIdx: number) => (
                        <div key={rIdx} className="p-3 bg-white rounded-lg border border-slate-200 text-xs space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-900">{rec.topic_name}</span>
                            <span
                              className={`px-2 py-0.5 rounded-md text-[10px] font-black uppercase ${
                                rec.recommended_action === 'drop'
                                  ? 'bg-rose-100 text-rose-800'
                                  : 'bg-amber-100 text-amber-800'
                              }`}
                            >
                              Action: {rec.recommended_action} (Save {rec.potential_savings_hours}h)
                            </span>
                          </div>
                          <p className="text-slate-500 text-[11px] leading-relaxed">{rec.reason}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-emerald-600 font-semibold text-xs">
                No active deficits! Your study capacity currently covers all required exam topics.
              </div>
            )}

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setTriageModalOpen(false)}
                className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold transition"
              >
                Close Advisor
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
