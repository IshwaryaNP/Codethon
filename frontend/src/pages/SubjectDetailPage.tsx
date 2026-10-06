import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { subjectsApi } from '../api/subjects';
import { topicsApi } from '../api/topics';
import { eventsApi } from '../api/events';
import { Subject, Topic, ExamEvent } from '../types';
import { ArrowLeft, Plus, BookOpen, Calendar, HelpCircle, CheckCircle2, Play } from 'lucide-react';

export const SubjectDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [subject, setSubject] = useState<Subject | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [events, setEvents] = useState<ExamEvent[]>([]);
  const [loading, setLoading] = useState(true);

  const [topicModalOpen, setTopicModalOpen] = useState(false);
  const [topicName, setTopicName] = useState('');
  const [estHours, setEstHours] = useState(3.0);
  const [difficulty, setDifficulty] = useState(3);
  const [weight, setWeight] = useState(4);

  const loadDetails = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const subRes = await subjectsApi.get(id);
      setSubject(subRes);

      const topRes = await topicsApi.list(id);
      setTopics(topRes);

      const evtRes = await eventsApi.list(id);
      setEvents(evtRes);
    } catch (err) {
      console.error('Failed to load subject detail:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDetails();
  }, [id]);

  const handleCreateTopic = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    try {
      await topicsApi.create({
        subject_id: id,
        name: topicName,
        est_hours: estHours,
        difficulty,
        weight,
        mastery: 0.0,
        status: 'pending'
      });
      setTopicName('');
      setEstHours(3.0);
      setTopicModalOpen(false);
      loadDetails();
    } catch (err) {
      console.error('Failed to create topic:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-sky-600"></div>
      </div>
    );
  }

  if (!subject) return null;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <button
        onClick={() => navigate('/subjects')}
        className="flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-900 transition"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Subjects
      </button>

      {/* Header Banner */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div
            className="w-14 h-14 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-md"
            style={{ backgroundColor: subject.color }}
          >
            <BookOpen className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900">{subject.name}</h1>
            <p className="text-xs text-slate-500 mt-1">{subject.description || 'No description'}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate('/syllabus')}
            className="px-3.5 py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-xl text-xs font-bold transition flex items-center gap-1.5"
          >
            Import Syllabus AI
          </button>
          <button
            onClick={() => setTopicModalOpen(true)}
            className="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-bold shadow-xs transition flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" /> Add Topic
          </button>
        </div>
      </div>

      {/* Grid: Topics & Events */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Topics List */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="font-extrabold text-slate-900 text-base">Course Topics ({topics.length})</h3>

          <div className="space-y-3">
            {topics.map((t) => (
              <div key={t.id} className="bg-white rounded-xl p-4 border border-slate-200 shadow-xs flex items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="font-bold text-slate-900 text-sm">{t.name}</h4>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        t.status === 'completed'
                          ? 'bg-emerald-100 text-emerald-800'
                          : t.status === 'in_progress'
                          ? 'bg-sky-100 text-sky-800'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {t.status}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                    <span>Est: {t.est_hours}h</span>
                    <span>Diff: {t.difficulty}/5</span>
                    <span>Weight: {t.weight}/5</span>
                    <span className="font-bold text-sky-600">Mastery: {Math.round(t.mastery * 100)}%</span>
                  </div>
                </div>

                <button
                  onClick={() => navigate(`/quiz/${t.id}`)}
                  className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold flex items-center gap-1 transition"
                >
                  <Play className="w-3 h-3 fill-current" /> Take MCQ Quiz
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Exams List */}
        <div className="space-y-4">
          <h3 className="font-extrabold text-slate-900 text-base">Subject Exams ({events.length})</h3>

          <div className="space-y-3">
            {events.map((evt) => (
              <div key={evt.id} className="bg-white rounded-xl p-4 border border-slate-200 shadow-xs">
                <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 text-[10px] font-black uppercase">
                  {evt.type}
                </span>
                <h4 className="font-bold text-slate-900 text-sm mt-1">{evt.title}</h4>
                <p className="text-xs text-slate-500 mt-0.5">Due: {evt.due_date.slice(0, 10)}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Add Topic Modal */}
      {topicModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <h3 className="font-extrabold text-slate-900 text-base">Add Topic to {subject.name}</h3>

            <form onSubmit={handleCreateTopic} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 uppercase mb-1">Topic Name</label>
                <input
                  type="text"
                  required
                  value={topicName}
                  onChange={(e) => setTopicName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300"
                  placeholder="e.g. Graph Traversal"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 uppercase mb-1">Est. Study Hours</label>
                <input
                  type="number"
                  step="0.5"
                  required
                  value={estHours}
                  onChange={(e) => setEstHours(parseFloat(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">Difficulty (1-5)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    value={difficulty}
                    onChange={(e) => setDifficulty(parseInt(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">Exam Weight (1-5)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    value={weight}
                    onChange={(e) => setWeight(parseInt(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300"
                  />
                </div>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setTopicModalOpen(false)}
                  className="px-4 py-2 bg-slate-100 rounded-xl font-bold"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-sky-600 text-white rounded-xl font-bold">
                  Save Topic
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
