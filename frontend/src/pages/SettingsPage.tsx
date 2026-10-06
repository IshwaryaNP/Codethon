import React from 'react';
import { useAuth } from '../context/AuthContext';
import { User, LogOut, Shield } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-xl font-black text-slate-900">Account Settings</h1>
        <p className="text-xs text-slate-500">Manage user profile and authentication status</p>
      </div>

      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-slate-900 text-white font-black flex items-center justify-center text-base">
            {user?.name?.slice(0, 2) || 'ST'}
          </div>
          <div>
            <h3 className="font-extrabold text-slate-900 text-base">{user?.name}</h3>
            <p className="text-xs text-slate-500">{user?.email}</p>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100 flex justify-end">
          <button
            onClick={logout}
            className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold shadow-xs flex items-center gap-1.5 transition"
          >
            <LogOut className="w-4 h-4" /> Sign Out
          </button>
        </div>
      </div>
    </div>
  );
};
