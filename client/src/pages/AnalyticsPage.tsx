import React, { useState, useEffect } from 'react';
import { BarChart3, Users, Calendar, ShieldCheck, AlertTriangle, RefreshCw, Smartphone, CheckCircle } from 'lucide-react';
import { api } from '../services/api';
import { AnalyticsOverview } from '../types';
import { StatsCard } from '../components/StatsCard';

export const AnalyticsPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [anData, repData] = await Promise.all([
        api.getAnalytics(),
        api.getReports()
      ]);
      setAnalytics(anData);
      setReports(repData);
    } catch (err) {
      console.error('Error fetching analytics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-[#27272a]">
        <div>
          <h1 className="text-lg font-bold tracking-tight text-white">System Analytics & Compliance</h1>
          <p className="text-xs text-zinc-400 mt-1">
            Aggregate attendance rates, course metrics, hardware compliance, and anti-proxy telemetry.
          </p>
        </div>
        <button
          onClick={loadData}
          className="p-1.5 rounded border border-zinc-700 bg-zinc-900 text-zinc-300 hover:text-white"
          title="Refresh analytics"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatsCard
          label="Overall Attendance Rate"
          value={`${analytics?.overall_attendance_rate || 0}%`}
          subtext="Total verified present / attempts"
          icon={<CheckCircle className="w-4 h-4 text-emerald-400" />}
        />
        <StatsCard
          label="Total Enrolled Students"
          value={analytics?.total_students || 0}
          subtext="Active registered accounts"
          icon={<Users className="w-4 h-4 text-zinc-400" />}
        />
        <StatsCard
          label="Bound Hardware Devices"
          value={analytics?.registered_devices || 0}
          subtext="1-to-1 phone compliance"
          icon={<Smartphone className="w-4 h-4 text-zinc-400" />}
        />
        <StatsCard
          label="Security Threat Flags"
          value={analytics?.security_alerts_count || 0}
          subtext="Replays, mismatches & weak RSSI"
          icon={<AlertTriangle className="w-4 h-4 text-amber-400" />}
        />
      </div>

      {/* Course Breakdown Table */}
      <div className="space-y-3 pt-4">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
          Course & Section Performance
        </h2>

        <div className="bg-[#121214] border border-[#27272a] rounded-lg overflow-hidden">
          <table className="w-full text-left enterprise-table">
            <thead>
              <tr className="bg-[#0e0e10]">
                <th className="py-2.5 px-4">Course Code</th>
                <th className="py-2.5 px-4">Course Name</th>
                <th className="py-2.5 px-4">Section</th>
                <th className="py-2.5 px-4">Sessions Held</th>
                <th className="py-2.5 px-4">Successful Marks</th>
                <th className="py-2.5 px-4">Blocked Proxies</th>
                <th className="py-2.5 px-4 text-right">Integrity Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/40">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-xs text-zinc-500">
                    <RefreshCw className="w-4 h-4 animate-spin inline mr-2" />
                    Loading course reports...
                  </td>
                </tr>
              ) : reports.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-xs text-zinc-500">
                    No course reports available.
                  </td>
                </tr>
              ) : (
                reports.map((rep) => {
                  const total = rep.successful_attendance + rep.rejected_attempts;
                  const rate = total > 0 ? Math.round((rep.successful_attendance / total) * 100) : 0;

                  return (
                    <tr key={rep.course_id} className="hover:bg-zinc-900/40 transition-colors">
                      <td className="py-3 px-4 font-mono font-medium text-white text-xs">
                        {rep.course_code}
                      </td>
                      <td className="py-3 px-4 text-xs font-medium text-zinc-200">
                        {rep.course_name}
                      </td>
                      <td className="py-3 px-4 font-mono text-xs text-zinc-400">
                        {rep.section}
                      </td>
                      <td className="py-3 px-4 font-mono text-xs text-zinc-300">
                        {rep.total_sessions}
                      </td>
                      <td className="py-3 px-4 font-mono text-xs text-emerald-400">
                        {rep.successful_attendance}
                      </td>
                      <td className="py-3 px-4 font-mono text-xs text-rose-400">
                        {rep.rejected_attempts}
                      </td>
                      <td className="py-3 px-4 text-right font-mono text-xs text-zinc-200">
                        {rate}%
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
