import React from 'react';
import { 
  ShieldCheck, 
  Radio, 
  Calendar, 
  History, 
  Smartphone, 
  Activity, 
  BarChart3, 
  LogOut,
  Wifi,
  WifiOff,
  Download
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

interface NavbarProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
  pendingDeviceRequestsCount?: number;
  wsConnected?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onTabChange,
  pendingDeviceRequestsCount = 0,
  wsConnected = false
}) => {
  const { user, logout } = useAuth();

  const navItems = [
    { id: 'live', label: 'Live Monitor', icon: Radio },
    { id: 'sessions', label: 'Sessions', icon: Calendar },
    { id: 'history', label: 'Attendance', icon: History },
    { 
      id: 'devices', 
      label: 'Device Approvals', 
      icon: Smartphone,
      badge: pendingDeviceRequestsCount > 0 ? pendingDeviceRequestsCount : undefined 
    },
    { id: 'audit', label: 'Security Audit', icon: Activity },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  ];

  return (
    <header className="border-b border-[#27272a] bg-[#0c0c0e] sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          {/* Logo & Product Title */}
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded bg-zinc-900 border border-zinc-700 flex items-center justify-center text-white">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="font-semibold tracking-tight text-white text-sm">ProxyProof</span>
                <span className="text-[10px] text-zinc-500 border border-zinc-800 rounded px-1.5 py-0.2 bg-zinc-900/60 font-mono">v1.0</span>
              </div>
            </div>

            {/* Nav Tabs */}
            <nav className="hidden md:flex items-center space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onTabChange(item.id)}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                      isActive 
                        ? 'bg-zinc-800/80 text-white border border-zinc-700' 
                        : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900'
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-emerald-400' : 'text-zinc-500'}`} />
                    <span>{item.label}</span>
                    {item.badge !== undefined && (
                      <span className="ml-1 bg-amber-500/20 text-amber-300 border border-amber-800/50 text-[10px] px-1.5 py-0.2 rounded-full font-mono">
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Right Status & Profile Controls */}
          <div className="flex items-center gap-4">
            {/* Real-time WebSocket connection status badge */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded border border-zinc-800 bg-zinc-900/50 text-xs">
              {wsConnected ? (
                <>
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  <span className="text-[11px] text-zinc-400 font-mono">LIVE WS</span>
                </>
              ) : (
                <>
                  <span className="inline-flex rounded-full h-2 w-2 bg-zinc-600"></span>
                  <span className="text-[11px] text-zinc-500 font-mono">OFFLINE</span>
                </>
              )}
            </div>

            {/* Download Mobile APK Button */}
            <a
              href="/proxyproof.apk"
              download="proxyproof.apk"
              className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded border border-emerald-900/60 bg-emerald-950/20 text-emerald-400 hover:bg-emerald-900/40 text-xs font-mono transition-colors"
              title="Download Android Mobile APK"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Get APK</span>
            </a>

            {/* User Profile */}
            <div className="flex items-center gap-3 pl-2 border-l border-zinc-800">
              <div className="text-right hidden sm:block">
                <div className="text-xs font-medium text-zinc-200">{user?.full_name || 'Organizer'}</div>
                <div className="text-[10px] text-zinc-500 font-mono">{user?.role}</div>
              </div>
              <button
                onClick={logout}
                title="Log out"
                className="p-1.5 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 rounded transition-colors"
                aria-label="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
