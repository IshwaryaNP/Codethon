import React, { useEffect, useState } from 'react';
import { eventsApi } from '../api/events';
import { subjectsApi } from '../api/subjects';
import { ExamEvent, Subject } from '../types';
import { Plus, Calendar, Trash2 } from 'lucide-react';

export const EventsPage: React.FC = () => {
  const [events, setEvents] = useState<ExamEvent[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  const [title, setTitle] = useState('');
  const [type, setType] = useState<'exam' | 'assignment'>('exam');
  const [subjectId, setSubjectId] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [description, setDescription] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const [eRes, sRes] = await Promise.all([eventsApi.list(), subjectsApi.list()]);
      setEvents(eRes);
      setSubjects(sRes);
      if (sRes.length > 0) setSubjectId(sRes[0].id);
    } catch (err) {
      console.error('Failed to load events:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await eventsApi.create({
        title,
        type,
        subject_id: subjectId,
        due_date: new Date(dueDate).toISOString(),
        description
      });
      setTitle('');
      setModalOpen(false);
      loadData();
    } catch (err) {
      console.error('Failed to create event:', err);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Delete exam event?')) {
      await eventsApi.delete(id);
      loadData();
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
          <h1 className="text-xl font-black text-slate-900">Exams & Assignments</h1>
          <p className="text-xs text-slate-500">Configure academic deadlines for deterministic scheduling</p>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="px-4 py-2.5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-bold shadow-xs flex items-center gap-1.5 transition"
        >
          <Plus className="w-4 h-4" /> Add Event
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {events.map((evt) => {
          const sub = subjMap.get(evt.subject_id);
          const isExam = evt.type === 'exam';

          return (
            <div key={evt.id} className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider ${
                    isExam ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'
                  }`}
                >
                  {evt.type}
                </span>
                <button onClick={() => handleDelete(evt.id)} className="p-1 text-slate-400 hover:text-rose-600">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div>
                <h3 className="font-extrabold text-slate-900 text-base">{evt.title}</h3>
                <p className="text-xs text-slate-500 mt-0.5 font-medium">{sub?.name || 'General Course'}</p>
              </div>

              <div className="pt-2 border-t border-slate-100 text-xs font-bold text-slate-700">
                Due: {evt.due_date.slice(0, 10)}
              </div>
            </div>
          );
        })}
      </div>

      {modalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <h3 className="font-extrabold text-slate-900 text-base">Add Exam or Assignment</h3>

            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 uppercase mb-1">Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300"
                  placeholder="e.g. Computer Networks Final Exam"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 uppercase mb-1">Event Type</label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value as any)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 font-medium"
                >
                  <option value="exam">Exam</option>
                  <option value="assignment">Assignment</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 uppercase mb-1">Subject</label>
                <select
                  value={subjectId}
                  onChange={(e) => setSubjectId(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 font-medium"
                >
                  {subjects.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 uppercase mb-1">Due Date</label>
                <input
                  type="date"
                  required
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 font-medium"
                />
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button type="button" onClick={() => setModalOpen(false)} className="px-4 py-2 bg-slate-100 rounded-xl font-bold">
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-sky-600 text-white rounded-xl font-bold">
                  Save Event
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
