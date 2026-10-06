import { apiClient } from './client';
import { Subject } from '../types';

export const subjectsApi = {
  list: async (): Promise<Subject[]> => {
    const res = await apiClient.get<Subject[]>('/subjects');
    return res.data;
  },

  get: async (id: string): Promise<Subject> => {
    const res = await apiClient.get<Subject>(`/subjects/${id}`);
    return res.data;
  },

  create: async (data: {
    name: string;
    description?: string;
    color?: string;
    initial_topic?: string;
    initial_est_hours?: number;
    exam_date?: string;
  }): Promise<Subject> => {
    const res = await apiClient.post<Subject>('/subjects', data);
    return res.data;
  },

  update: async (id: string, data: Partial<{ name: string; description: string; color: string }>): Promise<Subject> => {
    const res = await apiClient.put<Subject>(`/subjects/${id}`, data);
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/subjects/${id}`);
  },
};
