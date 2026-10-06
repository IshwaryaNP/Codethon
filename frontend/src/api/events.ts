import { apiClient } from './client';
import { ExamEvent } from '../types';

export const eventsApi = {
  list: async (subjectId?: string): Promise<ExamEvent[]> => {
    const params = subjectId ? { subject_id: subjectId } : {};
    const res = await apiClient.get<ExamEvent[]>('/events', { params });
    return res.data;
  },

  create: async (data: {
    title: string;
    type: 'exam' | 'assignment';
    subject_id: string;
    due_date: string;
    description?: string;
  }): Promise<ExamEvent> => {
    const res = await apiClient.post<ExamEvent>('/events', data);
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/events/${id}`);
  },
};
