import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { quizzesApi } from '../api/quizzes';
import { Question, QuizSubmissionResult } from '../types';
import { HelpCircle, AlertTriangle, Flag, CheckCircle2, ArrowRight } from 'lucide-react';

export const QuizPage: React.FC = () => {
  const { topicId } = useParams<{ topicId: string }>();
  const navigate = useNavigate();

  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [confidence, setConfidence] = useState<number>(3);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [reportedIds, setReportedIds] = useState<string[]>([]);

  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [reportingQId, setReportingQId] = useState<string | null>(null);
  const [reportReason, setReportReason] = useState('unclear question');

  useEffect(() => {
    if (!topicId) return;
    const fetchQs = async () => {
      try {
        setLoading(true);
        const data = await quizzesApi.generate(topicId);
        setQuestions(data);
      } catch (err) {
        console.error('Failed to generate quiz:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchQs();
  }, [topicId]);

  const handleSelectAnswer = (questionId: string, optionIdx: number) => {
    setAnswers((prev) => ({ ...prev, [questionId]: optionIdx }));
  };

  const openReportModal = (qId: string) => {
    setReportingQId(qId);
    setReportModalOpen(true);
  };

  const submitReport = async () => {
    if (!reportingQId) return;
    try {
      await quizzesApi.reportQuestion(reportingQId, reportReason);
      setReportedIds((prev) => [...prev, reportingQId]);
      setReportModalOpen(false);
    } catch (err) {
      console.error('Failed to report question:', err);
    }
  };

  const handleSubmitQuiz = async () => {
    if (!topicId) return;
    setSubmitting(true);
    try {
      const result: QuizSubmissionResult = await quizzesApi.submit({
        topic_id: topicId,
        confidence,
        answers
      });
      navigate('/quiz-results', { state: { result } });
    } catch (err) {
      console.error('Failed to submit quiz:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-3">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-sky-600"></div>
        <p className="text-xs text-slate-500 font-medium">Generating 5 MCQs for Topic...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-4">
        <div>
          <h1 className="text-xl font-black text-slate-900">Topic MCQ Quiz</h1>
          <p className="text-xs text-slate-500">Test your understanding. Answers update mastery and trigger spaced revision.</p>
        </div>

        {/* Confidence Selector BEFORE Quiz */}
        <div className="p-4 bg-sky-50 rounded-xl border border-sky-200 space-y-2">
          <label className="block text-xs font-bold text-sky-900 uppercase">
            Select Your Pre-Quiz Confidence Level (1-5):
          </label>
          <div className="flex items-center gap-3">
            {[1, 2, 3, 4, 5].map((level) => (
              <button
                key={level}
                type="button"
                onClick={() => setConfidence(level)}
                className={`flex-1 py-2 rounded-lg text-xs font-bold border transition ${
                  confidence === level
                    ? 'bg-sky-600 text-white border-sky-600 shadow-xs'
                    : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-100'
                }`}
              >
                {level} {level === 1 ? '(Very Low)' : level === 5 ? '(Very High)' : ''}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* MCQs List */}
      <div className="space-y-5">
        {questions.map((q, idx) => {
          const isReported = reportedIds.includes(q.id);

          return (
            <div
              key={q.id}
              className={`bg-white rounded-2xl p-6 border shadow-xs space-y-4 ${
                isReported ? 'border-amber-300 bg-amber-50/40 opacity-75' : 'border-slate-200'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <h3 className="font-extrabold text-slate-900 text-sm leading-snug">
                  {idx + 1}. {q.question}
                </h3>
                <button
                  type="button"
                  onClick={() => openReportModal(q.id)}
                  disabled={isReported}
                  className={`px-2.5 py-1 rounded text-[10px] font-bold flex items-center gap-1 transition ${
                    isReported
                      ? 'bg-amber-100 text-amber-800'
                      : 'bg-slate-100 hover:bg-rose-100 text-slate-500 hover:text-rose-700'
                  }`}
                >
                  <Flag className="w-3 h-3" /> {isReported ? 'Reported' : 'Report'}
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {q.options.map((opt, oIdx) => {
                  const isSelected = answers[q.id] === oIdx;
                  return (
                    <button
                      key={oIdx}
                      type="button"
                      onClick={() => handleSelectAnswer(q.id, oIdx)}
                      className={`p-3 rounded-xl text-xs font-semibold text-left border transition ${
                        isSelected
                          ? 'bg-sky-600 text-white border-sky-600 shadow-xs'
                          : 'bg-slate-50 text-slate-800 border-slate-200 hover:bg-slate-100'
                      }`}
                    >
                      <span className="font-bold mr-2">{String.fromCharCode(65 + oIdx)}.</span> {opt}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Submit Button */}
      <div className="flex justify-end pt-4">
        <button
          onClick={handleSubmitQuiz}
          disabled={submitting}
          className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm font-bold shadow-md transition flex items-center gap-2 disabled:opacity-50"
        >
          {submitting ? 'Grading Answers...' : 'Submit Quiz'}
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Report Modal */}
      {reportModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <h3 className="font-extrabold text-slate-900 text-base">Report Question Problem</h3>
            <p className="text-xs text-slate-500">Reported questions will be excluded from quiz scoring.</p>

            <div className="space-y-2">
              <label className="block text-xs font-semibold text-slate-700 uppercase">Reason</label>
              <select
                value={reportReason}
                onChange={(e) => setReportReason(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs font-medium"
              >
                <option value="incorrect question">Incorrect Question</option>
                <option value="unclear question">Unclear Question</option>
                <option value="wrong answer">Wrong Answer Key</option>
                <option value="duplicate">Duplicate</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div className="pt-2 flex justify-end gap-2">
              <button onClick={() => setReportModalOpen(false)} className="px-4 py-2 bg-slate-100 rounded-xl text-xs font-bold">
                Cancel
              </button>
              <button onClick={submitReport} className="px-4 py-2 bg-rose-600 text-white rounded-xl text-xs font-bold">
                Submit Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
