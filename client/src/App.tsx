import React, { useState, useEffect } from 'react';
import { useAuth } from './hooks/useAuth';
import { Navbar } from './components/Navbar';
import { LiveSessionPage } from './pages/LiveSessionPage';
import { SessionsPage } from './pages/SessionsPage';
import { AttendanceHistoryPage } from './pages/AttendanceHistoryPage';
import { DeviceApprovalPage } from './pages/DeviceApprovalPage';
import { AuditLogPage } from './pages/AuditLogPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { LoginPage } from './pages/LoginPage';
import { LiveWebSocketClient } from './services/websocket';
import { api } from './services/api';
import { RefreshCw } from 'lucide-react';

export function App() {
  const { user, isLoading } = useAuth();
  const [currentTab, setCurrentTab] = useState<string>('live');
  const [selectedSessionId, setSelectedSessionId] = useState<number | undefined>(undefined);
  const [pendingRequestsCount, setPendingRequestsCount] = useState<number>(0);
  const [wsConnected, setWsConnected] = useState<boolean>(false);

  // Poll or check pending device requests count
  const refreshPendingCount = async () => {
    if (!user) return;
    try {
      const requests = await api.getDeviceRequests();
      const count = requests.filter((r) => r.status === 'PENDING').length;
      setPendingRequestsCount(count);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    if (user) {
      refreshPendingCount();

      // Connect global events websocket
      const globalWs = new LiveWebSocketClient('/ws/events');
      globalWs.connect();

      const unbindStatus = globalWs.onStatusChange((status) => {
        setWsConnected(status);
      });

      const unbindEvents = globalWs.subscribe((event) => {
        if (event.type === 'DEVICE_CHANGE_REQUESTED') {
          setPendingRequestsCount((prev) => prev + 1);
        }
      });

      return () => {
        unbindStatus();
        unbindEvents();
        globalWs.disconnect();
      };
    }
  }, [user]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center text-zinc-500 font-mono text-xs">
        <RefreshCw className="w-4 h-4 animate-spin mr-2 text-zinc-400" />
        <span>Initializing ProxyProof Enterprise Console...</span>
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <div className="min-h-screen bg-[#09090b] flex flex-col">
      <Navbar
        currentTab={currentTab}
        onTabChange={(tab) => {
          setCurrentTab(tab);
        }}
        pendingDeviceRequestsCount={pendingRequestsCount}
        wsConnected={wsConnected}
      />

      <main className="flex-1">
        {currentTab === 'live' && (
          <LiveSessionPage
            sessionId={selectedSessionId}
            onNavigateToSessions={() => setCurrentTab('sessions')}
          />
        )}
        {currentTab === 'sessions' && (
          <SessionsPage
            onSelectSession={(id) => {
              setSelectedSessionId(id);
              setCurrentTab('live');
            }}
          />
        )}
        {currentTab === 'history' && <AttendanceHistoryPage />}
        {currentTab === 'devices' && (
          <DeviceApprovalPage onRequestProcessed={refreshPendingCount} />
        )}
        {currentTab === 'audit' && <AuditLogPage />}
        {currentTab === 'analytics' && <AnalyticsPage />}
      </main>

      <footer className="border-t border-[#27272a] bg-[#0c0c0e] py-4 text-center text-xs text-zinc-600 font-mono">
        ProxyProof Enterprise BLE Attendance Platform &bull; Linear/Vercel Design Specification &bull; Cryptographic HMAC Anti-Proxy Security
      </footer>
    </div>
  );
}

export default App;
