import React, { useState, useEffect } from 'react';
import { Activity, ShieldAlert, AlertTriangle, Info, RefreshCw, Filter, Terminal } from 'lucide-react';
import { api } from '../services/api';
import { AuditLog } from '../types';
import { Badge } from '../components/Badge';

export const AuditLogPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs(severityFilter === 'ALL' ? undefined : severityFilter);
      setLogs(data);
    } catch (err) {
      console.error('Error fetching audit logs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [severityFilter]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-[#27272a]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold tracking-tight text-white">Security & Anomaly Audit Trail</h1>
            <span className="text-[10px] text-zinc-400 font-mono border border-zinc-800 bg-zinc-900 px-2 py-0.5 rounded">
              Immutable Log
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Real-time heuristic anomaly detection, proxy replay attempts, device collisions, and session lifecycle events.
          </p>
        </div>
        <button
          onClick={loadLogs}
          className="p-1.5 rounded border border-zinc-700 bg-zinc-900 text-zinc-300 hover:text-white"
          title="Refresh logs"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Severity Filter Pills */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-zinc-400 flex items-center gap-1">
          <Filter className="w-3.5 h-3.5" /> Filter Severity:
        </span>
        {['ALL', 'CRITICAL', 'WARNING', 'INFO'].map((sev) => (
          <button
            key={sev}
            onClick={() => setSeverityFilter(sev)}
            className={`text-xs px-3 py-1 rounded font-medium transition-colors ${
              severityFilter === sev
                ? 'bg-zinc-800 text-white border border-zinc-600'
                : 'text-zinc-500 hover:text-zinc-300'
            }`}
          >
            {sev}
          </button>
        ))}
      </div>

      {/* Audit Log Stream */}
      <div className="bg-[#121214] border border-[#27272a] rounded-lg overflow-hidden">
        <div className="p-3 bg-[#0e0e10] border-b border-[#27272a] flex items-center justify-between text-xs text-zinc-400 font-mono">
          <div className="flex items-center gap-2">
            <Terminal className="w-3.5 h-3.5 text-zinc-500" />
            <span>PROXYPROOF-SECURITY-DAEMON://audit_log</span>
          </div>
          <span>{logs.length} entries recorded</span>
        </div>

        <div className="divide-y divide-zinc-800/40 max-h-[650px] overflow-y-auto font-mono text-xs">
          {loading ? (
            <div className="py-12 text-center text-zinc-500">
              <RefreshCw className="w-4 h-4 animate-spin inline mr-2" />
              Loading security logs...
            </div>
          ) : logs.length === 0 ? (
            <div className="py-12 text-center text-zinc-500">
              No audit logs found for the selected severity level.
            </div>
          ) : (
            logs.map((log) => {
              const isCrit = log.severity === 'CRITICAL';
              const isWarn = log.severity === 'WARNING';

              return (
                <div 
                  key={log.id} 
                  className={`p-3.5 hover:bg-zinc-900/50 transition-colors flex flex-col md:flex-row md:items-start justify-between gap-3 ${
                    isCrit ? 'bg-rose-950/10' : isWarn ? 'bg-amber-950/5' : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5">
                      {isCrit ? (
                        <ShieldAlert className="w-4 h-4 text-rose-400" />
                      ) : isWarn ? (
                        <AlertTriangle className="w-4 h-4 text-amber-400" />
                      ) : (
                        <Info className="w-4 h-4 text-zinc-500" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-zinc-200">{log.event_type}</span>
                        <Badge status={log.severity} />
                        {log.user_name && (
                          <span className="text-zinc-400 text-[11px]">
                            User: <strong className="text-zinc-200">{log.user_name}</strong>
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-zinc-400 mt-1 break-all bg-zinc-950/60 p-2 rounded border border-zinc-900">
                        {log.details}
                      </div>
                    </div>
                  </div>

                  <div className="text-right shrink-0 text-[11px] text-zinc-500 flex md:flex-col items-center md:items-end justify-between">
                    <div>{log.created_at ? new Date(log.created_at).toLocaleTimeString() : '---'}</div>
                    <div className="text-[10px] text-zinc-600">IP: {log.ip_address || '127.0.0.1'}</div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
