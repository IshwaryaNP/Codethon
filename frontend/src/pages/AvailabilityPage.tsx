import React, { useEffect, useState } from 'react';
import { availabilityApi } from '../api/availability';
import { Availability } from '../types';
import { Clock, CheckCircle2, Save } from 'lucide-react';
import { sessionsApi } from '../api/sessions';

export const AvailabilityPage: React.FC = () => {
  const [config, setConfig] = useState<Omit<Availability, 'id' | 'user_id'>>({
    monday: 2.5,
    tuesday: 2.5,
    wednesday: 2.0,
    thursday: 2.5,
    friday: 2.0,
    saturday: 4.0,
    sunday: 3.0,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    availabilityApi.get().then((data) => {
      setConfig({
        monday: data.monday,
        tuesday: data.tuesday,
        wednesday: data.wednesday,
        thursday: data.thursday,
        friday: data.friday,
        saturday: data.saturday,
        sunday: data.sunday,
      });
      setLoading(false);
    });
  }, []);

  const handleChange = (day: keyof typeof config, value: number) => {
    setConfig((prev) => ({ ...prev, [day]: Math.max(0, Math.min(24, value)) }));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);
    try {
      await availabilityApi.update(config);
      // Auto replan schedule after availability change
      await sessionsApi.replan();
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to update availability:', err);
    } finally {
      setSaving(false);
    }
  };

  const days: Array<{ key: keyof typeof config; label: string }> = [
    { key: 'monday', label: 'Monday' },
    { key: 'tuesday', label: 'Tuesday' },
    { key: 'wednesday', label: 'Wednesday' },
    { key: 'thursday', label: 'Thursday' },
    { key: 'friday', label: 'Friday' },
    { key: 'saturday', label: 'Saturday' },
    { key: 'sunday', label: 'Sunday' },
  ];

  const totalWeeklyHours = Object.values(config).reduce((a, b) => a + b, 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-sky-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-xl font-black text-slate-900">Weekly Study Availability</h1>
        <p className="text-xs text-slate-500">
          Configure daily available study hours. Usable scheduling capacity reserves a 20% daily buffer.
        </p>
      </div>

      <form onSubmit={handleSave} className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-6">
        <div className="p-4 bg-sky-50 rounded-xl border border-sky-200 flex items-center justify-between text-xs">
          <span className="font-bold text-sky-900">Total Weekly Available Study Capacity:</span>
          <span className="text-base font-black text-sky-700">{totalWeeklyHours.toFixed(1)} Hours / Week</span>
        </div>

        <div className="space-y-4 divide-y divide-slate-100">
          {days.map(({ key, label }) => (
            <div key={key} className="pt-3 first:pt-0 flex items-center justify-between gap-4">
              <label className="font-extrabold text-slate-900 text-sm">{label}</label>

              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="0"
                  max="12"
                  step="0.5"
                  value={config[key]}
                  onChange={(e) => handleChange(key, parseFloat(e.target.value))}
                  className="w-40 h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-sky-600"
                />
                <input
                  type="number"
                  min="0"
                  max="24"
                  step="0.5"
                  value={config[key]}
                  onChange={(e) => handleChange(key, parseFloat(e.target.value) || 0)}
                  className="w-16 px-2.5 py-1 rounded-lg border border-slate-300 text-xs font-bold text-center"
                />
                <span className="text-xs font-semibold text-slate-500 w-8">hrs</span>
              </div>
            </div>
          ))}
        </div>

        <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
          {savedSuccess ? (
            <p className="text-xs text-emerald-600 font-bold flex items-center gap-1">
              <CheckCircle2 className="w-4 h-4" /> Updated & Schedule Replanned!
            </p>
          ) : (
            <span />
          )}

          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-bold shadow-md transition flex items-center gap-1.5"
          >
            <Save className="w-4 h-4" /> {saving ? 'Saving...' : 'Save & Replan Schedule'}
          </button>
        </div>
      </form>
    </div>
  );
};
