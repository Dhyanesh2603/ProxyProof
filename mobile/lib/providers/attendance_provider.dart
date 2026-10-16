import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/attendance_model.dart';
import '../services/api_service.dart';

class AttendanceHistoryState {
  final double percentage;
  final int totalPresent;
  final int totalAttempts;
  final List<AttendanceModel> records;
  final bool isLoading;
  final String? error;

  AttendanceHistoryState({
    this.percentage = 0.0,
    this.totalPresent = 0,
    this.totalAttempts = 0,
    this.records = const [],
    this.isLoading = false,
    this.error,
  });
}

class AttendanceHistoryNotifier extends StateNotifier<AttendanceHistoryState> {
  final ApiService _api = ApiService();

  AttendanceHistoryNotifier() : super(AttendanceHistoryState(isLoading: true)) {
    loadHistory();
  }

  Future<void> loadHistory() async {
    state = AttendanceHistoryState(isLoading: true);
    try {
      final res = await _api.getStudentAttendanceHistory();
      final double pct = (res['percentage'] as num?)?.toDouble() ?? 0.0;
      final int present = res['total_present'] ?? 0;
      final int total = res['total_attempts'] ?? 0;
      final List rawList = res['history'] ?? [];
      final list = rawList.map((e) => AttendanceModel.fromJson(e)).toList();

      state = AttendanceHistoryState(
        percentage: pct,
        totalPresent: present,
        totalAttempts: total,
        records: list,
        isLoading: false,
      );
    } catch (e) {
      state = AttendanceHistoryState(
        isLoading: false,
        error: e.toString().replaceAll('Exception: ', ''),
      );
    }
  }
}

final attendanceHistoryProvider = StateNotifierProvider<AttendanceHistoryNotifier, AttendanceHistoryState>((ref) {
  return AttendanceHistoryNotifier();
});
