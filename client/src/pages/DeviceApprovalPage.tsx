import React, { useState, useEffect } from 'react';
import { Smartphone, Check, X, RefreshCw, AlertCircle, ShieldAlert } from 'lucide-react';
import { api } from '../services/api';
import { DeviceRequest } from '../types';
import { Badge } from '../components/Badge';

interface DeviceApprovalPageProps {
  onRequestProcessed?: () => void;
}

export const DeviceApprovalPage: React.FC<DeviceApprovalPageProps> = ({ onRequestProcessed }) => {
  const [requests, setRequests] = useState<DeviceRequest[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [processingId, setProcessingId] = useState<number | null>(null);

  const loadRequests = async () => {
    setLoading(true);
    try {
      const data = await api.getDeviceRequests();
      setRequests(data);
    } catch (err) {
      console.error('Error fetching device requests', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRequests();
  }, []);

  const handleReview = async (id: number, approve: boolean) => {
    const action = approve ? 'APPROVE' : 'REJECT';
    if (!window.confirm(`Are you sure you want to ${action} this device binding change?`)) return;

    setProcessingId(id);
    try {
      await api.reviewDeviceRequest(id, approve);
      await loadRequests();
      if (onRequestProcessed) onRequestProcessed();
    } catch (err: any) {
      alert(`Error processing request: ${err.message}`);
    } finally {
      setProcessingId(null);
    }
  };

  const pendingRequests = requests.filter((r) => r.status === 'PENDING');
  const pastRequests = requests.filter((r) => r.status !== 'PENDING');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-[#27272a]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold tracking-tight text-white">Device Binding Approvals</h1>
            {pendingRequests.length > 0 && (
              <span className="bg-amber-500/20 text-amber-300 border border-amber-800/60 text-xs px-2 py-0.5 rounded-full font-mono">
                {pendingRequests.length} pending
              </span>
            )}
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Strict 1-to-1 student hardware binding. Device migrations require explicit organizer verification.
          </p>
        </div>
        <button
          onClick={loadRequests}
          className="p-1.5 rounded border border-zinc-700 bg-zinc-900 text-zinc-300 hover:text-white"
          title="Refresh requests"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Pending Requests Section */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
          Pending Verification Requests ({pendingRequests.length})
        </h2>

        {loading ? (
          <div className="bg-[#121214] border border-[#27272a] rounded-lg p-8 text-center text-xs text-zinc-500">
            <RefreshCw className="w-4 h-4 animate-spin inline mr-2" />
            Loading device requests...
          </div>
        ) : pendingRequests.length === 0 ? (
          <div className="bg-[#121214] border border-[#27272a] rounded-lg p-6 text-center text-xs text-zinc-500">
            No pending device migration requests. All active student devices are bound and compliant.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {pendingRequests.map((req) => (
              <div key={req.id} className="bg-[#121214] border border-amber-900/40 rounded-lg p-5 space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-white">{req.student_name}</h3>
                    <div className="text-xs font-mono text-zinc-400">{req.student_code}</div>
                  </div>
                  <Badge status={req.status} />
                </div>

                <div className="space-y-2 bg-[#09090b] p-3 rounded border border-zinc-800/70 text-xs font-mono">
                  <div>
                    <span className="text-zinc-500 block text-[10px] uppercase">Registered Current Device</span>
                    <span className="text-zinc-400 truncate block">{req.old_device_uuid || 'None'}</span>
                  </div>
                  <div className="pt-2 border-t border-zinc-800/40">
                    <span className="text-emerald-500 block text-[10px] uppercase font-semibold">
                      New Requested Device ({req.new_device_name})
                    </span>
                    <span className="text-zinc-200 truncate block font-bold">{req.new_device_uuid}</span>
                  </div>
                </div>

                <div>
                  <span className="text-[10px] uppercase text-zinc-500 block">Student Justification</span>
                  <p className="text-xs text-zinc-300 mt-0.5 bg-zinc-950 p-2 rounded border border-zinc-900">
                    "{req.reason}"
                  </p>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-zinc-800/60">
                  <span className="text-[11px] text-zinc-500 font-mono">
                    {new Date(req.created_at).toLocaleDateString()}
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleReview(req.id, false)}
                      disabled={processingId === req.id}
                      className="px-3 py-1.5 rounded bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 hover:text-white text-xs font-medium flex items-center gap-1 transition-colors disabled:opacity-50"
                    >
                      <X className="w-3.5 h-3.5 text-rose-400" />
                      <span>Reject</span>
                    </button>
                    <button
                      onClick={() => handleReview(req.id, true)}
                      disabled={processingId === req.id}
                      className="px-3 py-1.5 rounded bg-emerald-950/60 hover:bg-emerald-900/80 border border-emerald-800/80 text-emerald-300 text-xs font-medium flex items-center gap-1 transition-colors disabled:opacity-50"
                    >
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Approve & Bind</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Past Processed History */}
      <div className="space-y-3 pt-6">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
          Processed Request History ({pastRequests.length})
        </h2>

        <div className="bg-[#121214] border border-[#27272a] rounded-lg overflow-hidden">
          <table className="w-full text-left enterprise-table">
            <thead>
              <tr className="bg-[#0e0e10]">
                <th className="py-2.5 px-4">Student</th>
                <th className="py-2.5 px-4">New Hardware Model</th>
                <th className="py-2.5 px-4">New UUID</th>
                <th className="py-2.5 px-4">Reason</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4 text-right">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/40">
              {pastRequests.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-xs text-zinc-500">
                    No past processed requests.
                  </td>
                </tr>
              ) : (
                pastRequests.map((r) => (
                  <tr key={r.id} className="hover:bg-zinc-900/40 transition-colors">
                    <td className="py-2.5 px-4 text-xs font-medium text-zinc-200">
                      <div>{r.student_name}</div>
                      <div className="text-[10px] text-zinc-500 font-mono">{r.student_code}</div>
                    </td>
                    <td className="py-2.5 px-4 text-xs text-zinc-300">
                      {r.new_device_name}
                    </td>
                    <td className="py-2.5 px-4 font-mono text-zinc-500 text-[11px] truncate max-w-xs" title={r.new_device_uuid}>
                      {r.new_device_uuid}
                    </td>
                    <td className="py-2.5 px-4 text-xs text-zinc-400 max-w-xs truncate" title={r.reason}>
                      {r.reason}
                    </td>
                    <td className="py-2.5 px-4">
                      <Badge status={r.status} />
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-[11px] text-zinc-500">
                      {new Date(r.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
