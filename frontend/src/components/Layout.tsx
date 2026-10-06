import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  BookOpen,
  Calendar,
  Clock,
  HelpCircle,
  FileText,
  LogOut,
  Sparkles,
  RefreshCw,
  Bell,
  User as UserIcon,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { sessionsApi } from '../api/sessions';

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isReplanning, setIsReplanning] = useState(false);
  const [replanSuccess, setReplanSuccess] = useState<string | null>(null);

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Subjects', path: '/subjects', icon: BookOpen },
    { name: 'Topics & Mastery', path: '/topics', icon: FileText },
    { name: 'Exams & Events', path: '/events', icon: Calendar },
    { name: 'Timetable', path: '/calendar', icon: Clock },
    { name: 'AI Syllabus Parser', path: '/syllabus', icon: Sparkles },
    { name: 'Availability', path: '/availability', icon: Clock },
  ];

  const handleManualReplan = async () => {
    try {
      setIsReplanning(true);
      await sessionsApi.replan();
      setReplanSuccess('Schedule recalculated!');
      setTimeout(() => setReplanSuccess(null), 3000);
    } catch (err) {
      console.error('Replan error:', err);
    } finally {
      setIsReplanning(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 shadow-xl flex-shrink-0">
        <div className="p-5 border-b border-slate-800">
          <Link to="/dashboard" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-md">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-bold text-white text-base leading-snug">Study Planner</h1>
              <p className="text-xs text-sky-400 font-medium">Adaptive & Intelligent</p>
            </div>
          </Link>
        </div>

        {/* Pitch Badge */}
        <div className="mx-4 my-3 p-3 bg-slate-800/80 rounded-lg border border-slate-700/60 text-xs text-slate-300">
          <p className="italic text-sky-300 font-medium">
            "We tell you whether you'll be ready for each exam, and re-plan when you won't."
          </p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-2 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || (item.path !== '/dashboard' && location.pathname.startsWith(item.path));
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-sky-600 text-white shadow-sm'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Trigger Replan Button */}
        <div className="p-4 border-t border-slate-800">
          <button
            onClick={handleManualReplan}
            disabled={isReplanning}
            className="w-full py-2.5 px-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-semibold text-sky-300 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isReplanning ? 'animate-spin text-sky-400' : ''}`} />
            {isReplanning ? 'Replanning Schedule...' : 'Re-calculate Schedule'}
          </button>
          {replanSuccess && (
            <p className="text-center text-xs text-emerald-400 mt-1 font-medium flex items-center justify-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> {replanSuccess}
            </p>
          )}
        </div>

        {/* User Footer */}
        <div className="p-4 border-t border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-slate-200 text-xs font-bold uppercase">
              {user?.name?.slice(0, 2) || 'ST'}
            </div>
            <div className="truncate">
              <p className="text-xs font-semibold text-white truncate">{user?.name}</p>
              <p className="text-[10px] text-slate-400 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-md transition"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shadow-xs sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-bold text-slate-800">
              {navItems.find((i) => i.path === location.pathname)?.name || 'Study Planner'}
            </h2>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <p className="text-xs text-slate-500 font-medium">
                {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' })}
              </p>
            </div>
            <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 border border-slate-200">
              <UserIcon className="w-4 h-4" />
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
};
