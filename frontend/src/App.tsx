import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { SubjectsPage } from './pages/SubjectsPage';
import { SubjectDetailPage } from './pages/SubjectDetailPage';
import { TopicsPage } from './pages/TopicsPage';
import { EventsPage } from './pages/EventsPage';
import { CalendarPage } from './pages/CalendarPage';
import { SyllabusPage } from './pages/SyllabusPage';
import { QuizPage } from './pages/QuizPage';
import { QuizResultsPage } from './pages/QuizResultsPage';
import { AvailabilityPage } from './pages/AvailabilityPage';
import { SettingsPage } from './pages/SettingsPage';

export const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route
              path="/*"
              element={
                <Layout>
                  <Routes>
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/subjects" element={<SubjectsPage />} />
                    <Route path="/subjects/:id" element={<SubjectDetailPage />} />
                    <Route path="/topics" element={<TopicsPage />} />
                    <Route path="/events" element={<EventsPage />} />
                    <Route path="/calendar" element={<CalendarPage />} />
                    <Route path="/syllabus" element={<SyllabusPage />} />
                    <Route path="/quiz/:topicId" element={<QuizPage />} />
                    <Route path="/quiz-results" element={<QuizResultsPage />} />
                    <Route path="/availability" element={<AvailabilityPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </Layout>
              }
            />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
  );
};

export default App;
