import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Square, 
  Download, 
  Users, 
  Clock, 
  Wifi, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  Search,
  Filter
} from 'lucide-react';
import { api } from '../services/api';
import { LiveWebSocketClient } from '../services/websocket';
import { SessionDetail, AttendanceRecord } from '../types';
import { StatsCard } from '../components/StatsCard';
import { Badge } from '../components/Badge';
import { TokenBeaconSimulator } from '../components/TokenBeaconSimulator';

interface LiveSessionPageProps {
  sessionId?: number;
  onNavigateToSessions?: () => void;
}

export const LiveSessionPage: React.FC<LiveSessionPageProps> = ({
  sessionId: propSessionId,
  onNavigateToSessions
}) => {
  const [session, setSession] = useState<SessionDetail | null>(null);
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [wsClient, setWsClient] = useState<LiveWebSocketClient | null>(null);

  // Load active session
  useEffect(() => {
    let isMounted = true;

    async function loadInitialSession() {
      setLoading(true);
      try {
        let activeId = propSessionId;
        if (!activeId) {
          const sessions = await api.getSessions();
          const found = sessions.find((s) => s.status === 'ACTIVE') || sessions[0];
          if (found) activeId = found.id;
        }

        if (activeId) {
          const [sessData, liveData] = await Promise.all([
            api.getSession(activeId),
            api.getLiveAttendance(activeId)
          ]);
          if (isMounted) {
            setSession(sessData);
            setRecords(liveData.records || []);
            setTimeRemaining(sessData.remaining_seconds);
          }
        }
      } catch (e) {
        console.error('Error fetching session', e);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadInitialSession();

    return () => {
      isMounted = false;
    };
  }, [propSessionId]);

  // Connect WebSocket for real-time live events
  useEffect(() => {
    if (!session?.session_id) return;

    const ws = new LiveWebSocketClient(`/ws/sessions/${session.session_id}`);
    ws.connect();

    const unsubscribe = ws.subscribe((event) => {
      if (event.type === 'ATTENDANCE_MARKED' || event.type === 'ATTENDANCE_REJECTED') {
        // Prepend new record to live table
        const newRecord: AttendanceRecord = {
          id: event.record.id,
          student_id: event.record.student_id,
          student_name: event.record.student_name,
          student_code: event.record.student_code,
          device_uuid: event.record.device_uuid,
          rssi: event.record.rssi,
          status: event.record.status,
          rejection_reason: event.record.rejection_reason,
          marked_at: event.record.marked_at || new Date().toISOString()
        };

        setRecords((prev) => [newRecord, ...prev.filter((r) => r.id !== newRecord.id)]);

        // Update session stats
        if (event.stats && session) {
          setSession((prev) => prev ? { ...prev, stats: event.stats } : prev);
        }
      } else if (event.type === 'SESSION_ENDED') {
        setSession((prev) => prev ? { ...prev, status: 'ENDED', remaining_seconds: 0 } : prev);
      }
    });

    setWsClient(ws);

    return () => {
      unsubscribe();
      ws.disconnect();
    };
  }, [session?.session_id]);

  // Countdown timer for session
  useEffect(() => {
    if (!session || session.status !== 'ACTIVE' || timeRemaining <= 0) return;
    const interval = setInterval(() => {
      setTimeRemaining((prev) => Math.max(0, prev - 1));
    }, 1000);
    return () => clearInterval(interval);
  }, [session?.status, timeRemaining]);

  const handleEndSession = async () => {
    if (!session) return;
    if (!window.confirm('Are you sure you want to end this attendance session? BLE broadcasting will terminate.')) return;
    try {
      await api.endSession(session.session_id);
      const updated = await api.getSession(session.session_id);
      setSession(updated);
    } catch (err: any) {
      alert(`Failed to end session: ${err.message}`);
    }
  };

  const handleStartSession = async () => {
    if (!session) return;
    try {
      await api.startSession(session.session_id);
      const updated = await api.getSession(session.session_id);
      setSession(updated);
      setTimeRemaining(updated.remaining_seconds);
    } catch (err: any) {
      alert(`Failed to start session: ${err.message}`);
    }
  };

  const formatSeconds = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const filteredRecords = records.filter((r) => {
    const matchesFilter = filterStatus === 'ALL' || r.status === filterStatus;
    const q = searchQuery.toLowerCase();
    const matchesSearch = 
      r.student_name.toLowerCase().includes(q) ||
      r.student_code.toLowerCase().includes(q) ||
      r.device_uuid.toLowerCase().includes(q);
    return matchesFilter && matchesSearch;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 text-zinc-500">
        <RefreshCw className="w-5 h-5 animate-spin mr-2" />
        <span>Loading live attendance monitor...</span>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center">
        <h2 className="text-base font-semibold text-zinc-200">No Active Attendance Session</h2>
        <p className="text-xs text-zinc-400 mt-1">Create or select a session to begin real-time BLE monitoring.</p>
        <button
          onClick={onNavigateToSessions}
          className="mt-4 px-4 py-2 bg-zinc-100 text-zinc-900 rounded text-xs font-semibold hover:bg-white"
        >
          Go to Sessions
        </button>
      </div>
    );
  }

  const totalMarked = (session.stats?.present || 0) + (session.stats?.late || 0);
  const totalAttempts = totalMarked + (session.stats?.rejected || 0);
  const successRate = totalAttempts > 0 ? Math.round((totalMarked / totalAttempts) * 100) : 100;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Session Top Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#27272a]">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-bold tracking-tight text-white">
              {session.course_code} &mdash; {session.course_name}
            </h1>
            <Badge status={session.status} />
            <span className="text-xs font-mono text-zinc-400 border border-zinc-800 bg-zinc-900 px-2 py-0.5 rounded">
              Sec {session.section}
            </span>
          </div>
          <div className="flex items-center gap-4 text-xs text-zinc-400 mt-1.5 font-mono">
            <span>Session Code: <strong className="text-zinc-200">{session.session_code}</strong></span>
            <span>&bull;</span>
            <span>RSSI Cutoff: <strong className="text-zinc-200">{session.rssi_threshold} dBm</strong></span>
            <span>&bull;</span>
            <span>
              Time Remaining:{' '}
              <strong className={timeRemaining < 300 ? 'text-amber-400' : 'text-zinc-200'}>
                {formatSeconds(timeRemaining)}
              </strong>
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {session.status === 'ACTIVE' ? (
            <button
              onClick={handleEndSession}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-rose-950/40 border border-rose-800/60 text-rose-300 hover:bg-rose-900/50 text-xs font-medium transition-colors"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
              <span>End Session</span>
            </button>
          ) : session.status === 'SCHEDULED' ? (
            <button
              onClick={handleStartSession}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-emerald-950/40 border border-emerald-800/60 text-emerald-300 hover:bg-emerald-900/50 text-xs font-medium transition-colors"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Start Session</span>
            </button>
          ) : null}

          <a
            href={api.exportCsvUrl(session.session_id)}
            download
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-zinc-900 border border-zinc-700 text-zinc-200 hover:bg-zinc-800 text-xs font-medium transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </a>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <StatsCard
          label="Present"
          value={session.stats?.present || 0}
          subtext="Verified inside classroom"
          icon={<CheckCircle className="w-4 h-4 text-emerald-400" />}
        />
        <StatsCard
          label="Late Entries"
          value={session.stats?.late || 0}
          subtext="After 15-min mark"
          icon={<Clock className="w-4 h-4 text-amber-400" />}
        />
        <StatsCard
          label="Rejected Attempts"
          value={session.stats?.rejected || 0}
          subtext="Proxies & weak RSSI blocked"
          icon={<XCircle className="w-4 h-4 text-rose-400" />}
        />
        <StatsCard
          label="Pass Rate"
          value={`${successRate}%`}
          subtext={`${totalMarked} / ${totalAttempts} total attempts`}
          icon={<Users className="w-4 h-4 text-zinc-400" />}
        />
        <StatsCard
          label="RSSI Cutoff"
          value={`${session.rssi_threshold} dBm`}
          subtext="Boundary wall attenuation"
          icon={<Wifi className="w-4 h-4 text-zinc-400" />}
        />
      </div>

      {/* Interactive BLE Rotating Token Beacon Simulator */}
      {session.status === 'ACTIVE' && (
        <TokenBeaconSimulator
          sessionId={session.session_id}
          sessionCode={session.session_code}
          rssiThreshold={session.rssi_threshold}
          onAttendanceSimulated={async () => {
            const liveData = await api.getLiveAttendance(session.session_id);
            setRecords(liveData.records || []);
            setSession((prev) => prev ? { ...prev, stats: liveData.stats } : prev);
          }}
        />
      )}

      {/* Real-time Student Arrivals Table */}
      <div className="bg-[#121214] border border-[#27272a] rounded-lg">
        {/* Table Controls */}
        <div className="p-4 border-b border-[#27272a] flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <div className="relative w-full sm:w-64">
              <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Search student or device..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#09090b] border border-[#27272a] rounded pl-8 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-hidden focus:border-zinc-500 font-mono"
              />
            </div>
          </div>

          {/* Status Filter Pills */}
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
                <th className="py-2.5 px-4">Device UUID</th>
                <th className="py-2.5 px-4">RSSI Signal</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Reason / Notes</th>
                <th className="py-2.5 px-4 text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/40">
              {filteredRecords.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-xs text-zinc-500">
                    No attendance records detected for current criteria.
                  </td>
                </tr>
              ) : (
                filteredRecords.map((r) => {
                  const isPresent = r.status === 'PRESENT';
                  const isLate = r.status === 'LATE';
                  const isRejected = r.status === 'REJECTED';

                  return (
                    <tr key={r.id} className="hover:bg-zinc-900/40 transition-colors">
                      <td className="py-2.5 px-4 font-medium text-zinc-200 text-xs">
                        {r.student_name}
                      </td>
                      <td className="py-2.5 px-4 font-mono text-zinc-400 text-xs">
                        {r.student_code}
                      </td>
                      <td className="py-2.5 px-4 font-mono text-zinc-500 text-[11px]">
                        {r.device_uuid}
                      </td>
                      <td className="py-2.5 px-4 font-mono text-xs">
                        <span className={`inline-flex items-center gap-1 ${
                          r.rssi >= session.rssi_threshold ? 'text-emerald-400' : 'text-rose-400 font-semibold'
                        }`}>
                          {r.rssi} dBm
                        </span>
                      </td>
                      <td className="py-2.5 px-4">
                        <Badge status={r.status} />
                      </td>
                      <td className="py-2.5 px-4 text-xs text-zinc-400 max-w-xs truncate">
                        {r.rejection_reason || (isPresent ? 'Verified Indoor BLE beacon' : isLate ? 'Verified late arrival' : '---')}
                      </td>
                      <td className="py-2.5 px-4 text-right font-mono text-[11px] text-zinc-500">
                        {r.marked_at ? new Date(r.marked_at).toLocaleTimeString() : '---'}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Footer info */}
        <div className="p-3 border-t border-[#27272a] bg-[#0c0c0e] text-[11px] text-zinc-500 flex items-center justify-between">
          <span>Showing {filteredRecords.length} records in active session</span>
          <span className="font-mono">ProxyProof Anti-Spoofing Engine Active</span>
        </div>
      </div>
    </div>
  );
};
