export interface User {
  id: string;
  name: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Subject {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  color: string;
  created_at: string;
  updated_at: string;
}

export interface Topic {
  id: string;
  user_id: string;
  subject_id: string;
  name: string;
  est_hours: number;
  difficulty: number;
  weight: number;
  mastery: number;
  status: 'pending' | 'in_progress' | 'completed';
  created_at: string;
  updated_at: string;
}

export interface ExamEvent {
  id: string;
  user_id: string;
  subject_id: string;
  title: string;
  type: 'exam' | 'assignment';
  due_date: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Availability {
  id: string;
  user_id: string;
  monday: number;
  tuesday: number;
  wednesday: number;
  thursday: number;
  friday: number;
  saturday: number;
  sunday: number;
}

export interface Session {
  id: string;
  user_id: string;
  subject_id: string;
  topic_id: string;
  topic_name?: string;
  subject_name?: string;
  subject_color?: string;
  planned_date: string;
  planned_minutes: number;
  actual_minutes?: number;
  status: 'planned' | 'done' | 'missed';
  type: 'study' | 'revision';
  created_at: string;
  updated_at: string;
}

export interface ExamReadiness {
  exam_id: string;
  exam_title: string;
  exam_date: string;
  remaining_hours: number;
  available_hours: number;
  readiness_probability: number;
  feasible: boolean;
  status: 'Ready' | 'At Risk' | 'Infeasible';
}

export interface TriageRecommendation {
  topic_id: string;
  topic_name: string;
  weight: number;
  est_hours: number;
  remaining_hours: number;
  value_ratio: number;
  recommended_action: 'compress' | 'drop';
  potential_savings_hours: number;
  reason: string;
}

export interface DashboardData {
  stats: {
    overall_progress_pct: number;
    completed_topics: number;
    total_topics: number;
    weekly_study_hours: number;
    upcoming_exams_count: number;
  };
  subject_cards: Array<{
    id: string;
    name: string;
    color: string;
    progress_pct: number;
    total_topics: number;
    completed_topics: number;
    remaining_topics: number;
    estimated_remaining_hours: number;
    velocity: number;
  }>;
  exam_readiness: ExamReadiness[];
  todays_plan: Session[];
  upcoming_deadlines: Array<{
    id: string;
    title: string;
    type: 'exam' | 'assignment';
    subject_name: string;
    subject_color: string;
    due_date: string;
  }>;
  priority_topics: Array<{
    id: string;
    name: string;
    subject_name: string;
    subject_color: string;
    priority: number;
    mastery: number;
    difficulty: number;
    est_hours: number;
  }>;
  warnings: Array<{
    type: string;
    title: string;
    message: string;
    severity: 'warning' | 'critical';
  }>;
}

export interface Question {
  id: string;
  topic_id: string;
  question: string;
  options: string[];
  subtopic: string;
  is_reported?: boolean;
}

export interface QuizSubmissionResult {
  id: string;
  user_id: string;
  topic_id: string;
  confidence: number;
  score: number;
  correct_count: number;
  total_valid_questions: number;
  new_mastery: number;
  confidence_warning: boolean;
  weak_subtopics: string[];
  created_at: string;
}
