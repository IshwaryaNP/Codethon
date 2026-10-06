import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { QuizSubmissionResult } from '../types';
import { CheckCircle2, AlertTriangle, RefreshCw, ArrowRight, Brain } from 'lucide-react';

export const QuizResultsPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const result: QuizSubmissionResult | undefined = location.state?.result;

  if (!result) {
    return (
      <div className="text-center py-20">
        <p className="text-xs text-slate-500">No quiz result available.</p>
        <button onClick={() => navigate('/dashboard')} className="mt-4 px-4 py-2 bg-sky-600 text-white rounded-xl text-xs font-bold">
          Go to Dashboard
        </button>
      </div>
    );
  }

  const scorePct = Math.round(result.score * 100);
  const masteryPct = Math.round(result.new_mastery * 100);

  return (
    <div className="space-y-6 max-w-2xl mx-auto py-6">
      <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-lg text-center space-y-5">
        <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto font-bold">
          <CheckCircle2 className="w-8 h-8" />
        </div>

        <div>
          <h1 className="text-2xl font-black text-slate-900">Quiz Completed!</h1>
          <p className="text-xs text-slate-500 mt-1">Deterministic python grading & mastery update applied</p>
        </div>

        {/* Confidence Warning (Section 25) */}
        {result.confidence_warning && (
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-900 text-xs text-left flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-bold">Confidence Mismatch Warning</h4>
              <p className="mt-0.5 leading-relaxed">
                Your confidence was high ({result.confidence}/5), but your quiz performance was below 50% ({scorePct}%).
                Consider revising this topic again.
              </p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-100">
          <div className="p-3 bg-slate-50 rounded-xl">
            <p className="text-[10px] text-slate-400 font-bold uppercase">Quiz Score</p>
            <p className="text-2xl font-black text-slate-900 mt-0.5">{scorePct}%</p>
            <p className="text-[10px] text-slate-500">{result.correct_count} / {result.total_valid_questions} correct</p>
          </div>

          <div className="p-3 bg-sky-50 rounded-xl">
            <p className="text-[10px] text-sky-600 font-bold uppercase">New Mastery</p>
            <p className="text-2xl font-black text-sky-700 mt-0.5">{masteryPct}%</p>
            <p className="text-[10px] text-sky-600">Updated in Database</p>
          </div>

          <div className="p-3 bg-purple-50 rounded-xl">
            <p className="text-[10px] text-purple-600 font-bold uppercase">Confidence</p>
            <p className="text-2xl font-black text-purple-700 mt-0.5">{result.confidence}/5</p>
            <p className="text-[10px] text-purple-600">Selected Level</p>
          </div>
        </div>

        {/* Weak Subtopic Revisions */}
        {result.weak_subtopics && result.weak_subtopics.length > 0 && (
          <div className="p-4 bg-purple-50/50 border border-purple-200 rounded-xl text-left space-y-2">
            <h4 className="font-bold text-xs text-purple-900 flex items-center gap-1.5">
              <Brain className="w-4 h-4 text-purple-600" /> Weak Subtopics Identified
            </h4>
            <p className="text-xs text-purple-700">
              Short revision sessions have been added to your schedule for:
            </p>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {result.weak_subtopics.map((sub, idx) => (
                <span key={idx} className="px-2.5 py-1 bg-purple-200/60 text-purple-900 rounded-md text-[11px] font-bold">
                  {sub}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="pt-4 flex items-center justify-center gap-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold shadow-md transition flex items-center gap-1.5"
          >
            Go to Dashboard <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
