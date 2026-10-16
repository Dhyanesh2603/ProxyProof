export type Role = 'ORGANIZER' | 'STUDENT';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  student_id: string | null;
  is_active?: boolean;
}

export interface Course {
  id: number;
  code: string;
  name: string;
  section: string;
}

export interface AttendanceSession {
  id: number;
  session_code: string;
  course_id: number;
  course_code: string;
  course_name: string;
  section: string;
  status: 'SCHEDULED' | 'ACTIVE' | 'ENDED';
  duration_minutes: number;
  rssi_threshold: number;
  token_rotation_interval?: number;
  started_at: string | null;
  ended_at: string | null;
  created_at: string | null;
}

export interface SessionStats {
  present: number;
  late: number;
  rejected: number;
  total_marked: number;
}

export interface SessionDetail {
  session_id: number;
  session_code: string;
  status: 'SCHEDULED' | 'ACTIVE' | 'ENDED';
  duration_minutes: number;
  rssi_threshold: number;
  remaining_seconds: number;
  started_at: string | null;
  course_code: string;
  course_name: string;
  section: string;
  stats: SessionStats;
}

export interface AttendanceRecord {
  id: number;
  session_id?: number;
  session_code?: string;
  course_code?: string;
  student_id: number;
  student_name: string;
  student_code: string;
  device_uuid: string;
  rssi: number;
  status: 'PRESENT' | 'LATE' | 'REJECTED';
  rejection_reason: string | null;
  marked_at: string;
}

export interface DeviceRequest {
  id: number;
  user_id: number;
  student_name: string;
  student_code: string;
  old_device_uuid: string;
  new_device_uuid: string;
  new_device_name: string;
  reason: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  reviewed_by: number | null;
  created_at: string;
}

export interface AuditLog {
  id: number;
  event_type: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  user_id: number | null;
  user_name: string;
  details: string;
  ip_address: string | null;
  created_at: string;
}

export interface AnalyticsOverview {
  total_students: number;
  total_sessions: number;
  active_sessions: number;
  total_present: number;
  total_late: number;
  total_rejected: number;
  overall_attendance_rate: number;
  registered_devices: number;
  security_alerts_count: number;
}

export interface RotatingTokenInfo {
  session_id: number;
  session_code: string;
  token: string;
  window_index: number;
  valid_from: number;
  valid_until: number;
  time_remaining_seconds: number;
  ble_payload_hex: string;
  rotation_interval_seconds: number;
}
