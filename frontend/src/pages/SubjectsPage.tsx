import React, { useEffect, useState } from 'react';
import { subjectsApi } from '../api/subjects';
import { Subject } from '../types';
import { Plus, BookOpen, Trash2, Edit2, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const SubjectsPage: React.FC = () => {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [color, setColor] = useState('#0284c7');
  const [initialTopic, setInitialTopic] = useState('');
  const [initialEstHours, setInitialEstHours] = useState(2.0);
  const [examDate, setExamDate] = useState('');
  const navigate = useNavigate();

  const loadSubjects = async () => {
    try {
      setLoading(true);
      const data = await subjectsApi.list();
      setSubjects(data);
    } catch (err) {
      console.error('Failed to load subjects:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSubjects();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await subjectsApi.create({
        name,
        description,
        color,
        initial_topic: initialTopic,
        initial_est_hours: Number(initialEstHours) || 2.0,
        exam_date: examDate ? new Date(examDate).toISOString() : undefined
      });
      setName('');
      setDescription('');
      setColor('#0284c7');
      setInitialTopic('');
      setInitialEstHours(2.0);
      setExamDate('');
      setModalOpen(false);
      loadSubjects();
    } catch (err) {
      console.error('Failed to create subject:', err);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this subject and all associated topics/events?')) {
      try {
        await subjectsApi.delete(id);
        loadSubjects();
      } catch (err) {
        console.error('Failed to delete subject:', err);
      }
    }
  };

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
          <h1 className="text-xl font-black text-slate-900">Academic Subjects</h1>
          <p className="text-xs text-slate-500">Organize your courses and study modules</p>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="px-4 py-2.5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-bold shadow-sm flex items-center gap-1.5 transition"
        >
          <Plus className="w-4 h-4" /> Add Subject
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {subjects.map((sub) => (
          <div
            key={sub.id}
            onClick={() => navigate(`/subjects/${sub.id}`)}
            className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs hover:shadow-md transition cursor-pointer flex flex-col justify-between space-y-4 group"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold" style={{ backgroundColor: sub.color }}>
                  <BookOpen className="w-5 h-5" />
                </div>
                <button
                  onClick={(e) => handleDelete(sub.id, e)}
                  className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                  title="Delete Subject"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div>
                <h3 className="font-extrabold text-slate-900 text-base group-hover:text-sky-600 transition truncate">
                  {sub.name}
                </h3>
                <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                  {sub.description || 'No description provided.'}
                </p>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-sky-600">
              <span>View Topics & Syllabus</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition" />
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-5">
            <h3 className="font-extrabold text-slate-900 text-lg">Add New Subject</h3>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Subject Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-sky-500"
                  placeholder="e.g. Data Structures"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-sky-500"
                  rows={3}
                  placeholder="Short course description..."
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Starting Topic / Chapter</label>
                <input
                  type="text"
                  value={initialTopic}
                  onChange={(e) => setInitialTopic(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-sky-500"
                  placeholder="e.g. Unit 1: Introduction (Optional)"
                />
                <p className="text-[11px] text-slate-400 mt-1">Schedules immediately onto your timetable starting today/tomorrow</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Estimated Hours</label>
                  <input
                    type="number"
                    min="0.5"
                    step="0.5"
                    value={initialEstHours}
                    onChange={(e) => setInitialEstHours(parseFloat(e.target.value))}
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-sky-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Target Exam Date</label>
                  <input
                    type="date"
                    value={examDate}
                    onChange={(e) => setExamDate(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-sky-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Accent Color</label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={color}
                    onChange={(e) => setColor(e.target.value)}
                    className="w-10 h-10 rounded-lg cursor-pointer border-0"
                  />
                  <span className="text-xs font-mono font-medium text-slate-600">{color}</span>
                </div>
              </div>

              <div className="pt-3 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-bold shadow-sm"
                >
                  Create Subject
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
