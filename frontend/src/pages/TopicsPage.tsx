import React, { useEffect, useState } from 'react';
import { topicsApi } from '../api/topics';
import { subjectsApi } from '../api/subjects';
import { Topic, Subject } from '../types';
import { FileText, Play, Plus, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const TopicsPage: React.FC = () => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadAll = async () => {
    try {
      setLoading(true);
      const [tData, sData] = await Promise.all([topicsApi.list(), subjectsApi.list()]);
      setTopics(tData);
      setSubjects(sData);
    } catch (err) {
      console.error('Failed to load topics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const handleDelete = async (id: string) => {
    if (confirm('Delete topic?')) {
      await topicsApi.delete(id);
      loadAll();
    }
  };

  const subjMap = new Map(subjects.map((s) => [s.id, s]));

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-sky-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-black text-slate-900">All Topics & Mastery</h1>
          <p className="text-xs text-slate-500">Track mastery scores, difficulty, and quiz status across all courses</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-xs">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 font-bold text-slate-600 uppercase tracking-wider">
              <th className="py-3 px-4">Topic Name</th>
              <th className="py-3 px-4">Subject</th>
              <th className="py-3 px-4">Est. Hours</th>
              <th className="py-3 px-4">Difficulty</th>
              <th className="py-3 px-4">Exam Weight</th>
              <th className="py-3 px-4">Mastery</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium text-slate-800">
            {topics.map((t) => {
              const sub = subjMap.get(t.subject_id);
              const masteryPct = Math.round(t.mastery * 100);

              return (
                <tr key={t.id} className="hover:bg-slate-50/80 transition">
                  <td className="py-3.5 px-4 font-bold text-slate-900">{t.name}</td>
                  <td className="py-3.5 px-4">
                    <span
                      className="px-2 py-0.5 rounded text-[10px] font-bold text-white inline-block"
                      style={{ backgroundColor: sub?.color || '#3b82f6' }}
                    >
                      {sub?.name || 'General'}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">{t.est_hours}h</td>
                  <td className="py-3.5 px-4">{t.difficulty}/5</td>
                  <td className="py-3.5 px-4">{t.weight}/5</td>
                  <td className="py-3.5 px-4 font-bold text-sky-600">{masteryPct}%</td>
                  <td className="py-3.5 px-4">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase ${
                        t.status === 'completed'
                          ? 'bg-emerald-100 text-emerald-800'
                          : t.status === 'in_progress'
                          ? 'bg-sky-100 text-sky-800'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {t.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right space-x-2">
                    <button
                      onClick={() => navigate(`/quiz/${t.id}`)}
                      className="px-2.5 py-1 bg-sky-600 hover:bg-sky-700 text-white rounded-md text-[11px] font-bold"
                    >
                      Quiz
                    </button>
                    <button
                      onClick={() => handleDelete(t.id)}
                      className="p-1 text-slate-400 hover:text-rose-600 inline-block"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
