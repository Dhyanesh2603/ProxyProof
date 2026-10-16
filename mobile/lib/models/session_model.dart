class SessionModel {
  final int id;
  final String sessionCode;
  final int courseId;
  final String courseCode;
  final String courseName;
  final String section;
  final String status; // 'SCHEDULED', 'ACTIVE', 'ENDED'
  final int durationMinutes;
  final int rssiThreshold;
  final int tokenRotationInterval;
  final String? startedAt;

  SessionModel({
    required this.id,
    required this.sessionCode,
    required this.courseId,
    required this.courseCode,
    required this.courseName,
    required this.section,
    required this.status,
    required this.durationMinutes,
    required this.rssiThreshold,
    this.tokenRotationInterval = 5,
    this.startedAt,
  });

  factory SessionModel.fromJson(Map<String, dynamic> json) {
    return SessionModel(
      id: json['id'] ?? json['session_id'] as int,
      sessionCode: json['session_code'] as String,
      courseId: json['course_id'] ?? 0,
      courseCode: json['course_code'] ?? '',
      courseName: json['course_name'] ?? '',
      section: json['section'] ?? 'A',
      status: json['status'] as String,
      durationMinutes: json['duration_minutes'] ?? 60,
      rssiThreshold: json['rssi_threshold'] ?? -75,
      tokenRotationInterval: json['token_rotation_interval'] ?? 5,
      startedAt: json['started_at'] as String?,
    );
  }

  bool get isActive => status == 'ACTIVE';
}
