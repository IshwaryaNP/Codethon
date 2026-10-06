import { apiClient } from './client';
import { Question, QuizSubmissionResult } from '../types';

export const quizzesApi = {
  generate: async (topicId: string): Promise<Question[]> => {
    const res = await apiClient.post<Question[]>(`/quizzes/generate/${topicId}`);
    return res.data;
  },

  submit: async (data: {
    topic_id: string;
    confidence: number;
    answers: Record<string, number>;
  }): Promise<QuizSubmissionResult> => {
    const res = await apiClient.post<QuizSubmissionResult>('/quizzes/submit', data);
    return res.data;
  },

  reportQuestion: async (questionId: string, reason: string): Promise<void> => {
    await apiClient.post('/quizzes/report', { question_id: questionId, reason });
  }
};
