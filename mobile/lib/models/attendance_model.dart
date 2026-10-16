class AttendanceModel {
  final int id;
  final int? sessionId;
  final String sessionCode;
  final String courseCode;
  final String? courseName;
  final String status; // 'PRESENT', 'LATE', 'REJECTED'
  final String? rejectionReason;
  final int rssi;
  final String? markedAt;

  AttendanceModel({
    required this.id,
    this.sessionId,
    required this.sessionCode,
    required this.courseCode,
    this.courseName,
    required this.status,
    this.rejectionReason,
    required this.rssi,
    this.markedAt,
  });

  factory AttendanceModel.fromJson(Map<String, dynamic> json) {
    return AttendanceModel(
      id: json['id'] as int,
      sessionId: json['session_id'] as int?,
      sessionCode: json['session_code'] ?? 'SES-UNKNOWN',
      courseCode: json['course_code'] ?? 'N/A',
      courseName: json['course_name'] as String?,
      status: json['status'] as String,
      rejectionReason: json['rejection_reason'] as String?,
      rssi: json['rssi'] ?? -75,
      markedAt: json['marked_at'] as String?,
    );
  }

  bool get isVerified => status == 'PRESENT' || status == 'LATE';
  bool get isRejected => status == 'REJECTED';
}
