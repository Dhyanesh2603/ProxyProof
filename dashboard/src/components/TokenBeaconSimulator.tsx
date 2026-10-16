import React, { useState, useEffect } from 'react';
import { Radio, RefreshCw, Send, CheckCircle2, XCircle, AlertTriangle, Cpu, Copy, Check } from 'lucide-react';
import { api } from '../services/api';
import { RotatingTokenInfo } from '../types';

interface TokenBeaconSimulatorProps {
  sessionId: number;
  sessionCode: string;
  rssiThreshold: number;
  onAttendanceSimulated?: () => void;
}

export const TokenBeaconSimulator: React.FC<TokenBeaconSimulatorProps> = ({
  sessionId,
  sessionCode,
  rssiThreshold,
  onAttendanceSimulated
}) => {
  const [tokenInfo, setTokenInfo] = useState<RotatingTokenInfo | null>(null);
  const [secondsRemaining, setSecondsRemaining] = useState<number>(5);
  const [copied, setCopied] = useState(false);

  // Simulation form states
  const [selectedStudent, setSelectedStudent] = useState<string>('alice');
  const [deviceUuid, setDeviceUuid] = useState<string>('DEV-UUID-ALICE-15PRO');
  const [rssi, setRssi] = useState<number>(-62);
  const [simResult, setSimResult] = useState<{ success: boolean; message: string; status?: string } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Fetch token periodically
  useEffect(() => {
    let timer: any = null;

    async function fetchToken() {
      try {
        const data = await api.getSessionToken(sessionId);
        setTokenInfo(data);
        setSecondsRemaining(Math.max(0.5, data.time_remaining_seconds));
      } catch (err) {
        // Session might not be active
      }
    }

    fetchToken();
    const interval = setInterval(fetchToken, 4000);

    // 100ms smooth countdown ticker
    const countdown = setInterval(() => {
      setSecondsRemaining((prev) => {
        if (prev <= 0.2) {
          fetchToken();
          return 5.0;
        }
        return Math.max(0, prev - 0.1);
      });
    }, 100);

    return () => {
      clearInterval(interval);
      clearInterval(countdown);
    };
  }, [sessionId]);

  const handleStudentPresetChange = (key: string) => {
    setSelectedStudent(key);
    if (key === 'alice') {
      setDeviceUuid('DEV-UUID-ALICE-15PRO');
      setRssi(-62);
    } else if (key === 'bob') {
      setDeviceUuid('DEV-UUID-BOB-PIXEL8');
      setRssi(-68);
    } else if (key === 'charlie') {
      setDeviceUuid('DEV-UUID-CHARLIE-S24');
      setRssi(-86); // Charlie outside hallway!
    } else if (key === 'spoof') {
      setDeviceUuid('ROGUE-UNREGISTERED-EMULATOR-UUID');
      setRssi(-55);
    }
    setSimResult(null);
  };

  const handleCopyPayload = () => {
    if (tokenInfo?.ble_payload_hex) {
      navigator.clipboard.writeText(tokenInfo.ble_payload_hex);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleSimulateAttendance = async () => {
    if (!tokenInfo) return;
    setIsSubmitting(true);
    setSimResult(null);
    try {
      const res = await api.markAttendance({
        session_id: sessionId,
        token: tokenInfo.token,
        device_uuid: deviceUuid,
        rssi: rssi
      });
      setSimResult({
        success: res.success,
        message: res.message || (res.success ? 'Attendance verified successfully' : res.rejection_reason || 'Rejected'),
        status: res.status
      });
      if (onAttendanceSimulated) {
        onAttendanceSimulated();
      }
    } catch (err: any) {
      setSimResult({
        success: false,
        message: err.message || 'Verification request failed'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const progressPercent = Math.min(100, Math.max(0, (secondsRemaining / 5.0) * 100));
  const isInsideClassroom = rssi >= rssiThreshold;

  return (
    <div className="bg-[#121214] border border-[#27272a] rounded-lg p-5">
      <div className="flex items-center justify-between pb-4 border-b border-[#27272a]">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded bg-zinc-800 border border-zinc-700 text-emerald-400">
            <Radio className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">BLE Advertising Beacon & Scanner Simulator</h3>
            <p className="text-xs text-zinc-400">Real-time rotating cryptographic token beacon broadcaster</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono text-zinc-500 bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded">
            Session: {sessionCode}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-5">
        {/* Left: Active Rotating Token Broadcast */}
        <div className="space-y-4">
          <div className="bg-[#09090b] border border-[#27272a] rounded p-4">
            <div className="flex items-center justify-between text-xs text-zinc-400 mb-1">
              <span className="uppercase font-mono text-[10px] tracking-wider">Active HMAC Token (16 hex)</span>
              <span className="mono-num font-mono text-emerald-400 font-medium">
                {secondsRemaining.toFixed(1)}s remaining
              </span>
            </div>

            <div className="flex items-center justify-between gap-3 mt-2">
              <div className="font-mono text-lg font-bold tracking-wider text-emerald-400 truncate">
                {tokenInfo ? tokenInfo.token : 'INITIALIZING...'}
              </div>
              <button
                onClick={handleCopyPayload}
                className="p-1.5 rounded border border-zinc-800 hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors"
                title="Copy BLE Raw Hex Payload"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>

            {/* Countdown Progress Bar */}
            <div className="w-full bg-zinc-800/80 h-1 rounded-full mt-3 overflow-hidden">
              <div 
                className="bg-emerald-500 h-full transition-all duration-100 ease-linear"
                style={{ width: `${progressPercent}%` }}
              />
            </div>

            <div className="grid grid-cols-2 gap-2 mt-3 pt-3 border-t border-zinc-800/60 text-[11px] text-zinc-400 font-mono">
              <div>
                <span className="text-zinc-500">Window Index:</span> #{tokenInfo?.window_index || '---'}
              </div>
              <div>
                <span className="text-zinc-500">Rotation Step:</span> {tokenInfo?.rotation_interval_seconds || 5}s
              </div>
            </div>
          </div>

          {/* Raw BLE Manufacturer Packet Details */}
          <div className="bg-[#09090b] border border-[#27272a] rounded p-3 text-xs font-mono">
            <div className="text-[10px] uppercase tracking-wider text-zinc-500 mb-1 flex items-center justify-between">
              <span>BLE Advertisement Frame (26 Bytes)</span>
              <span className="text-zinc-500">Prefix: 0x5050 ('PP')</span>
            </div>
            <div className="text-[11px] text-zinc-300 break-all select-all bg-zinc-950 p-2 rounded border border-zinc-800/60">
              {tokenInfo?.ble_payload_hex || '5050000000010000000065336230633434323938666331633134'}
            </div>
          </div>
        </div>

        {/* Right: Interactive Student Attendance Simulator */}
        <div className="bg-[#09090b] border border-[#27272a] rounded p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-zinc-200 uppercase tracking-wide">
                Simulate Student BLE Scanner
              </span>
              <span className="text-[11px] text-zinc-400">Interactive Pipeline Tester</span>
            </div>

            {/* Quick Presets */}
            <div className="flex items-center gap-1.5 mb-3 flex-wrap">
              <span className="text-[11px] text-zinc-500">Presets:</span>
              <button
                type="button"
                onClick={() => handleStudentPresetChange('alice')}
                className={`text-[11px] px-2 py-0.5 rounded border transition-colors ${
                  selectedStudent === 'alice' 
                    ? 'border-emerald-700 bg-emerald-950/40 text-emerald-300' 
                    : 'border-zinc-800 bg-zinc-900 text-zinc-400 hover:text-white'
                }`}
              >
                Alice (Inside -62dBm)
              </button>
              <button
                type="button"
                onClick={() => handleStudentPresetChange('charlie')}
                className={`text-[11px] px-2 py-0.5 rounded border transition-colors ${
                  selectedStudent === 'charlie' 
                    ? 'border-amber-700 bg-amber-950/40 text-amber-300' 
                    : 'border-zinc-800 bg-zinc-900 text-zinc-400 hover:text-white'
                }`}
              >
                Charlie (Outside -86dBm)
              </button>
              <button
                type="button"
                onClick={() => handleStudentPresetChange('spoof')}
                className={`text-[11px] px-2 py-0.5 rounded border transition-colors ${
                  selectedStudent === 'spoof' 
                    ? 'border-rose-700 bg-rose-950/40 text-rose-300' 
                    : 'border-zinc-800 bg-zinc-900 text-zinc-400 hover:text-white'
                }`}
              >
                Rogue Device (Spoof)
              </button>
            </div>

            {/* Form Fields */}
            <div className="space-y-3">
              <div>
                <label className="block text-[11px] font-medium text-zinc-400 mb-1">
                  Device Hardware UUID
                </label>
                <input
                  type="text"
                  value={deviceUuid}
                  onChange={(e) => setDeviceUuid(e.target.value)}
                  className="w-full bg-[#121214] border border-[#27272a] rounded px-3 py-1.5 text-xs text-zinc-200 font-mono focus:outline-hidden focus:border-zinc-500"
                  placeholder="e.g. DEV-UUID-ALICE-15PRO"
                />
              </div>

              <div>
                <div className="flex items-center justify-between text-[11px] font-medium text-zinc-400 mb-1">
                  <span>Measured RSSI Signal Strength</span>
                  <span className={`mono-num font-mono font-medium ${isInsideClassroom ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {rssi} dBm ({isInsideClassroom ? 'Inside Boundary' : 'Outside Classroom Boundary'})
                  </span>
                </div>
                <input
                  type="range"
                  min="-95"
                  max="-45"
                  value={rssi}
                  onChange={(e) => setRssi(parseInt(e.target.value, 10))}
                  className="w-full accent-emerald-500 h-1.5 bg-zinc-800 rounded-lg cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-zinc-500 font-mono mt-0.5">
                  <span>-95 dBm (Weak / Street)</span>
                  <span className="text-zinc-400">Threshold: {rssiThreshold} dBm</span>
                  <span>-45 dBm (Adjacent)</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-zinc-800/80">
            {simResult && (
              <div className={`p-2.5 rounded border mb-3 text-xs flex items-start gap-2 ${
                simResult.success 
                  ? 'border-emerald-800/60 bg-emerald-950/20 text-emerald-300' 
                  : 'border-rose-800/60 bg-rose-950/20 text-rose-300'
              }`}>
                {simResult.success ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                ) : (
                  <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                )}
                <div>
                  <div className="font-semibold">{simResult.success ? 'Verified' : 'Verification Rejected'}</div>
                  <div className="text-[11px] opacity-90">{simResult.message}</div>
                </div>
              </div>
            )}

            <button
              type="button"
              onClick={handleSimulateAttendance}
              disabled={isSubmitting || !tokenInfo}
              className="w-full bg-zinc-100 hover:bg-white text-zinc-950 text-xs font-semibold py-2 px-3 rounded flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Verifying Against Backend Pipeline...</span>
                </>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5" />
                  <span>Send Attendance Packet</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
