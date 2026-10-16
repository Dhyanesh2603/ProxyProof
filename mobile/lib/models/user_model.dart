class UserModel {
  final int id;
  final String email;
  final String fullName;
  final String role; // 'ORGANIZER' or 'STUDENT'
  final String? studentId;

  UserModel({
    required this.id,
    required this.email,
    required this.fullName,
    required this.role,
    this.studentId,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as int,
      email: json['email'] as String,
      fullName: json['full_name'] as String,
      role: json['role'] as String,
      studentId: json['student_id'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'email': email,
    'full_name': fullName,
    'role': role,
    'student_id': studentId,
  };

  bool get isOrganizer => role == 'ORGANIZER';
  bool get isStudent => role == 'STUDENT';
}
