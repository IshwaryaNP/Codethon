import { apiClient } from './client';
import { Topic } from '../types';

export interface SyllabusParseResponse {
  subject_id: string;
  subject_name: string;
  extracted_topics: Array<{
    name: string;
    est_hours: number;
    difficulty: number;
    weight: number;
  }>;
}

export const syllabusApi = {
  parse: async (subjectId: string, syllabusText: string): Promise<SyllabusParseResponse> => {
    const res = await apiClient.post<SyllabusParseResponse>('/syllabus/parse', {
      subject_id: subjectId,
      syllabus_text: syllabusText
    });
    return res.data;
  },

  confirm: async (subjectId: string, topics: Array<{ name: string; est_hours: number; difficulty: number; weight: number }>): Promise<Topic[]> => {
    const res = await apiClient.post<Topic[]>('/syllabus/confirm', {
      subject_id: subjectId,
      topics
    });
    return res.data;
  }
};
