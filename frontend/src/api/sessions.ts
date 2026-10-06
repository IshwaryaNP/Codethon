import { apiClient } from './client';
import { Session } from '../types';

export const sessionsApi = {
  list: async (startDate?: string, endDate?: string): Promise<Session[]> => {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const res = await apiClient.get<Session[]>('/sessions', { params });
    return res.data;
  },

  updateStatus: async (sessionId: string, status: 'done' | 'missed' | 'planned', actualMinutes?: number): Promise<Session> => {
    const res = await apiClient.put<Session>(`/sessions/${sessionId}/status`, {
      status,
      actual_minutes: actualMinutes
    });
    return res.data;
  },

  replan: async (): Promise<any> => {
    const res = await apiClient.post('/scheduler/replan');
    return res.data;
  },

  getFeasibility: async (): Promise<any> => {
    const res = await apiClient.get('/scheduler/feasibility');
    return res.data;
  }
};
