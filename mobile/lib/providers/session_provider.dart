import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/session_model.dart';
import '../services/api_service.dart';

final sessionsListProvider = FutureProvider<List<SessionModel>>((ref) async {
  final api = ApiService();
  return await api.getSessions();
});

final activeSessionProvider = Provider<SessionModel?>((ref) {
  final asyncSessions = ref.watch(sessionsListProvider);
  return asyncSessions.when(
    data: (list) {
      try {
        return list.firstWhere((s) => s.isActive);
      } catch (_) {
        return null;
      }
    },
    loading: () => null,
    error: (_, __) => null,
  );
});
