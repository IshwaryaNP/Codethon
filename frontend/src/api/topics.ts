import { apiClient } from './client';
import { Topic } from '../types';

export const topicsApi = {
  list: async (subjectId?: string): Promise<Topic[]> => {
    const params = subjectId ? { subject_id: subjectId } : {};
    const res = await apiClient.get<Topic[]>('/topics', { params });
    return res.data;
  },

  get: async (id: string): Promise<Topic> => {
    const res = await apiClient.get<Topic>(`/topics/${id}`);
    return res.data;
  },

  create: async (data: {
    subject_id: string;
    name: string;
    est_hours: number;
    difficulty: number;
    weight: number;
    mastery?: number;
    status?: string;
  }): Promise<Topic> => {
    const res = await apiClient.post<Topic>('/topics', data);
    return res.data;
  },

  update: async (id: string, data: Partial<Topic>): Promise<Topic> => {
    const res = await apiClient.put<Topic>(`/topics/${id}`, data);
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/topics/${id}`);
  },
};
