import React, { useEffect, useState } from 'react';
import { syllabusApi, SyllabusParseResponse } from '../api/syllabus';
import { subjectsApi } from '../api/subjects';
import { Subject } from '../types';
import { Sparkles, CheckCircle2, AlertCircle, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const SyllabusPage: React.FC = () => {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState('');
  const [syllabusText, setSyllabusText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [parseResult, setParseResult] = useState<SyllabusParseResponse | null>(null);
  const [confirming, setConfirming] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    subjectsApi.list().then((data) => {
      setSubjects(data);
      if (data.length > 0) setSelectedSubjectId(data[0].id);
    });
  }, []);

  const handleParse = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await syllabusApi.parse(selectedSubjectId, syllabusText);
      setParseResult(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to parse syllabus with Anthropic API.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!parseResult) return;
    setConfirming(true);
    try {
      await syllabusApi.confirm(parseResult.subject_id, parseResult.extracted_topics);
      navigate(`/subjects/${parseResult.subject_id}`);
    } catch (err: any) {
      setError('Failed to confirm and save topics.');
    } finally {
      setConfirming(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-xl font-black text-slate-900 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-600" /> AI Syllabus Topic Extractor
        </h1>
        <p className="text-xs text-slate-500">
          Paste your course syllabus text. Anthropic AI extracts structured topics with estimated hours, difficulty & weight.
        </p>
      </div>

      {!parseResult ? (
        <form onSubmit={handleParse} className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-4">
          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Target Subject</label>
            <select
              value={selectedSubjectId}
              onChange={(e) => setSelectedSubjectId(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-medium"
            >
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Paste Raw Syllabus Text</label>
            <textarea
              required
              rows={10}
              value={syllabusText}
              onChange={(e) => setSyllabusText(e.target.value)}
              className="w-full p-4 rounded-xl border border-slate-300 text-xs font-mono leading-relaxed"
              placeholder={`Example:
Unit 1: Binary Search Trees & AVL Balancing (5 hours, Difficulty 4/5)
Unit 2: Graph Traversal Algorithms DFS and BFS (6 hours)
Unit 3: Dynamic Programming basics, Fibonacci and Knapsack (8 hours)`}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold shadow-md transition flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" /> Extracting Structured Topics...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" /> Extract Topics with Anthropic AI
              </>
            )}
          </button>
        </form>
      ) : (
        /* Preview & Confirm View */
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-5">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="font-extrabold text-slate-900 text-base">Extracted Topics Preview</h3>
              <p className="text-xs text-slate-500">Subject: {parseResult.subject_name}</p>
            </div>
            <button
              onClick={() => setParseResult(null)}
              className="text-xs font-bold text-slate-500 hover:text-slate-900 underline"
            >
              Edit Syllabus Text
            </button>
          </div>

          <div className="divide-y divide-slate-100 space-y-2">
            {parseResult.extracted_topics.map((t, idx) => (
              <div key={idx} className="pt-2 flex items-center justify-between text-xs">
                <div>
                  <h4 className="font-bold text-slate-900">{t.name}</h4>
                  <p className="text-slate-500 mt-0.5">
                    Est: {t.est_hours}h • Difficulty: {t.difficulty}/5 • Weight: {t.weight}/5
                  </p>
                </div>
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              </div>
            ))}
          </div>

          <div className="pt-4 border-t border-slate-100 flex justify-end gap-3">
            <button
              onClick={() => setParseResult(null)}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={confirming}
              className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md transition flex items-center gap-1.5"
            >
              {confirming ? 'Saving...' : 'Confirm & Save All Topics'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
