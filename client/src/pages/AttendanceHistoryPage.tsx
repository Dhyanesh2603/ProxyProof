import React, { useState, useEffect } from 'react';
import { Download, Search, RefreshCw, Calendar, Filter } from 'lucide-react';
import { api } from '../services/api';
import { AttendanceRecord } from '../types';
import { Badge } from '../components/Badge';

export const AttendanceHistoryPage: React.FC = () => {
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await api.getAttendanceHistory();
      setRecords(data);
    } catch (err) {
      console.error('Error fetching attendance history', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const filtered = records.filter((r) => {
    const matchesStatus = filterStatus === 'ALL' || r.status === filterStatus;
    const q = search.toLowerCase();
    const matchesSearch = 
      (r.student_name || '').toLowerCase().includes(q) ||
      (r.student_code || '').toLowerCase().includes(q) ||
      (r.session_code || '').toLowerCase().includes(q) ||
      (r.course_code || '').toLowerCase().includes(q) ||
      (r.device_uuid || '').toLowerCase().includes(q);
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-[#27272a]">
        <div>
          <h1 className="text-lg font-bold tracking-tight text-white">Attendance Records</h1>
          <p className="text-xs text-zinc-400 mt-1">
            Historical audit log of all verified, late, and rejected attendance attempts.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadHistory}
            className="p-1.5 rounded border border-zinc-700 bg-zinc-900 text-zinc-300 hover:text-white"
            title="Refresh records"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <a
            href={api.exportCsvUrl()}
            download
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-zinc-100 hover:bg-white text-zinc-950 text-xs font-semibold transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Full CSV</span>
          </a>
        </div>
      </div>

      {/* Table Container */}
      <div className="bg-[#121214] border border-[#27272a] rounded-lg overflow-hidden">
        {/* Controls */}
        <div className="p-4 border-b border-[#27272a] flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="relative w-full sm:w-72">
            <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search student, session, device..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#09090b] border border-[#27272a] rounded pl-8 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 font-mono focus:outline-hidden focus:border-zinc-500"
            />
          </div>

          <div className="flex items-center gap-1.5 w-full sm:w-auto justify-end">
            {['ALL', 'PRESENT', 'LATE', 'REJECTED'].map((st) => (
              <button
                key={st}
                onClick={() => setFilterStatus(st)}
                className={`text-[11px] px-2.5 py-1 rounded font-medium transition-colors ${
                  filterStatus === st 
                    ? 'bg-zinc-800 text-white border border-zinc-700' 
                    : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left enterprise-table">
            <thead>
              <tr className="bg-[#0e0e10]">
                <th className="py-2.5 px-4">Student</th>
                <th className="py-2.5 px-4">Student ID</th>
                <th className="py-2.5 px-4">Session</th>
                <th className="py-2.5 px-4">Course</th>
                <th className="py-2.5 px-4">Device UUID</th>
                <th className="py-2.5 px-4">RSSI</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Audit Details</th>
                <th className="py-2.5 px-4 text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/40">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-xs text-zinc-500">
                    <RefreshCw className="w-4 h-4 animate-spin inline mr-2" />
                    Loading records...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-xs text-zinc-500">
                    No attendance records match your filter criteria.
                  </td>
                </tr>
              ) : (
                filtered.map((r) => (
                  <tr key={r.id} className="hover:bg-zinc-900/40 transition-colors">
                    <td className="py-2.5 px-4 text-xs font-medium text-zinc-200">
                      {r.student_name}
                    </td>
                    <td className="py-2.5 px-4 font-mono text-zinc-400 text-xs">
                      {r.student_code}
                    </td>
                    <td className="py-2.5 px-4 font-mono text-zinc-300 text-xs">
                      {r.session_code || `SES-${r.session_id}`}
                    </td>
                    <td className="py-2.5 px-4 font-mono text-zinc-400 text-xs">
                      {r.course_code || '---'}
                    </td>
                    <td className="py-2.5 px-4 font-mono text-zinc-500 text-[11px] max-w-[140px] truncate" title={r.device_uuid}>
                      {r.device_uuid}
                    </td>
                    <td className="py-2.5 px-4 font-mono text-xs">
                      <span className={r.rssi >= -75 ? 'text-emerald-400' : 'text-rose-400'}>
                        {r.rssi} dBm
                      </span>
                    </td>
                    <td className="py-2.5 px-4">
                      <Badge status={r.status} />
                    </td>
                    <td className="py-2.5 px-4 text-xs text-zinc-400 max-w-xs truncate" title={r.rejection_reason || 'Verified proximity packet'}>
                      {r.rejection_reason || 'Verified proximity packet'}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-[11px] text-zinc-500">
                      {r.marked_at ? new Date(r.marked_at).toLocaleString() : '---'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="p-3 border-t border-[#27272a] bg-[#0c0c0e] text-[11px] text-zinc-500 flex items-center justify-between">
          <span>Showing {filtered.length} total historical entries</span>
          <span className="font-mono">Tamper-Evident HMAC Logging</span>
        </div>
      </div>
    </div>
  );
};
