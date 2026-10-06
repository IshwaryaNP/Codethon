import { apiClient } from './client';
import { DashboardData } from '../types';

export const dashboardApi = {
  getSummary: async (): Promise<DashboardData> => {
    const res = await apiClient.get<DashboardData>('/dashboard/summary');
    return res.data;
  },

  getDailySummary: async (): Promise<{ date: string; stats: any; summary: string }> => {
    const res = await apiClient.get('/summaries/daily');
    return res.data;
  },

  getWeeklySummary: async (): Promise<{ week_starting: string; stats: any; summary: string }> => {
    const res = await apiClient.get('/summaries/weekly');
    return res.data;
  }
};
