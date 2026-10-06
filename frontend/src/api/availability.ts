import { apiClient } from './client';
import { Availability } from '../types';

export const availabilityApi = {
  get: async (): Promise<Availability> => {
    const res = await apiClient.get<Availability>('/availability');
    return res.data;
  },

  update: async (data: Omit<Availability, 'id' | 'user_id'>): Promise<Availability> => {
    const res = await apiClient.put<Availability>('/availability', data);
    return res.data;
  },
};
