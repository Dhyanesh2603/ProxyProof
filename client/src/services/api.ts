import { 
  User, 
  Course, 
  AttendanceSession, 
  SessionDetail, 
  AttendanceRecord, 
  DeviceRequest, 
  AuditLog, 
  AnalyticsOverview,
  RotatingTokenInfo
} from '../types';

const API_BASE = '/api/v1';

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('proxyproof_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMsg = `HTTP ${response.status}`;
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errorMsg;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  return response.json();
}

export const api = {
  // Auth
  login: async (email: string, password: string) => {
    return request<{ access_token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  getCurrentUser: async () => {
    return request<User>('/auth/me');
  },

  // Sessions
  getSessions: async () => {
    return request<AttendanceSession[]>('/sessions');
  },

  getSession: async (id: number) => {
    return request<SessionDetail>(`/sessions/${id}`);
  },

  createSession: async (data: { course_id: number; duration_minutes: number; rssi_threshold: number; token_rotation_interval: number }) => {
    return request<AttendanceSession>('/sessions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  startSession: async (id: number) => {
    return request<{ message: string; status: string; started_at: string }>(`/sessions/${id}/start`, {
      method: 'POST',
    });
  },

  endSession: async (id: number) => {
    return request<{ message: string; status: string; ended_at: string }>(`/sessions/${id}/end`, {
      method: 'POST',
    });
  },

  getSessionToken: async (id: number) => {
    return request<RotatingTokenInfo>(`/sessions/${id}/token`);
  },

  // Courses
  getCourses: async () => {
    return request<Course[]>('/sessions/courses/list');
  },

  createCourse: async (data: { code: string; name: string; section: string }) => {
    return request<Course>('/sessions/courses/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Attendance
  getLiveAttendance: async (sessionId: number) => {
    return request<{ session_id: number; stats: any; records: AttendanceRecord[] }>(`/attendance/live/${sessionId}`);
  },

  getAttendanceHistory: async () => {
    return request<AttendanceRecord[]>('/attendance/history');
  },

  markAttendance: async (data: { session_id: number; token: string; device_uuid: string; rssi: number }) => {
    return request<{ success: boolean; status: string; message: string; rejection_reason?: string }>('/attendance/mark', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  exportCsvUrl: (sessionId?: number) => {
    return `${API_BASE}/attendance/export${sessionId ? `?session_id=${sessionId}` : ''}`;
  },

  manualMarkAttendance: async (data: { session_id: number; student_id: number; status?: string; note?: string }) => {
    return request<{ success: boolean; id: number; status: string; marked_at: string }>('/attendance/manual', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  removeAttendance: async (attendanceId: number) => {
    return request<{ success: boolean; message: string }>(`/attendance/${attendanceId}`, {
      method: 'DELETE',
    });
  },

  // Devices
  getDeviceRequests: async () => {
    return request<DeviceRequest[]>('/devices/requests');
  },

  reviewDeviceRequest: async (requestId: number, approve: boolean) => {
    return request<{ id: number; status: string }>(`/devices/approve/${requestId}`, {
      method: 'PUT',
      body: JSON.stringify({ approve }),
    });
  },

  // Analytics & Auditing
  getAnalytics: async () => {
    return request<AnalyticsOverview>('/analytics');
  },

  getAuditLogs: async (severity?: string) => {
    return request<AuditLog[]>(`/analytics/audit-logs${severity ? `?severity=${severity}` : ''}`);
  },

  getReports: async () => {
    return request<any[]>('/analytics/reports');
  },

  getHealth: async () => {
    return request<any>('/health');
  }
};
