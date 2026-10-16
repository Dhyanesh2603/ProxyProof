import React, { useState } from 'react';
import { ShieldCheck, Lock, Mail, ArrowRight, UserCheck, Shield } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const [email, setEmail] = useState<string>('prof.smith@university.edu');
  const [password, setPassword] = useState<string>('Admin@1234');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickFill = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-[#09090b] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Brand Icon & Heading */}
        <div className="flex justify-center">
          <div className="w-12 h-12 rounded-lg bg-zinc-900 border border-zinc-700 flex items-center justify-center text-white shadow-inner">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
          </div>
        </div>
        <h2 className="mt-4 text-center text-xl font-bold tracking-tight text-white">
          ProxyProof Internal Console
        </h2>
        <p className="mt-1 text-center text-xs text-zinc-400">
          Smart BLE Attendance Verification & Anti-Proxy Infrastructure
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-[#121214] border border-[#27272a] py-8 px-6 shadow-2xl rounded-lg sm:px-8">
          <form className="space-y-4" onSubmit={handleSubmit}>
            {error && (
              <div className="p-3 bg-rose-950/40 border border-rose-900/60 rounded text-xs text-rose-300">
                {error}
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1" htmlFor="email-input">
                University Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-zinc-500 absolute left-3 top-2.5" />
                <input
                  id="email-input"
                  name="email"
                  type="email"
                  autoComplete="email"
                  inputMode="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-[#09090b] border border-[#27272a] rounded pl-9 pr-3 py-2 text-xs text-white placeholder-zinc-500 font-mono focus:outline-hidden focus:border-zinc-500 transition-colors"
                  placeholder="name@university.edu"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1" htmlFor="password-input">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-zinc-500 absolute left-3 top-2.5" />
                <input
                  id="password-input"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[#09090b] border border-[#27272a] rounded pl-9 pr-3 py-2 text-xs text-white placeholder-zinc-500 font-mono focus:outline-hidden focus:border-zinc-500 transition-colors"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2 px-4 border border-transparent rounded text-xs font-semibold text-zinc-950 bg-zinc-100 hover:bg-white focus:outline-hidden transition-colors disabled:opacity-50 mt-2"
            >
              <span>{loading ? 'Authenticating...' : 'Sign In to Console'}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>

          {/* Demo Account Quick-Fill */}
          <div className="mt-6 pt-5 border-t border-zinc-800">
            <span className="block text-[10px] font-mono uppercase tracking-wider text-zinc-500 mb-2">
              Instant Demo Access
            </span>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleQuickFill('prof.smith@university.edu', 'Admin@1234')}
                className="p-2 rounded bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-left transition-colors"
              >
                <div className="text-[11px] font-semibold text-zinc-200 flex items-center gap-1">
                  <Shield className="w-3 h-3 text-emerald-400" />
                  <span>Organizer</span>
                </div>
                <div className="text-[10px] text-zinc-500 truncate font-mono">prof.smith@university.edu</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickFill('alice@university.edu', 'Student@1234')}
                className="p-2 rounded bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-left transition-colors"
              >
                <div className="text-[11px] font-semibold text-zinc-200 flex items-center gap-1">
                  <UserCheck className="w-3 h-3 text-blue-400" />
                  <span>Student</span>
                </div>
                <div className="text-[10px] text-zinc-500 truncate font-mono">alice@university.edu</div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
