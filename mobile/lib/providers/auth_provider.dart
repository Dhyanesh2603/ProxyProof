import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

class AuthState {
  final UserModel? user;
  final bool isLoading;
  final String? error;

  AuthState({this.user, this.isLoading = false, this.error});

  bool get isAuthenticated => user != null;
  bool get isOrganizer => user?.isOrganizer ?? false;
  bool get isStudent => user?.isStudent ?? false;

  AuthState copyWith({UserModel? user, bool? isLoading, String? error}) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final ApiService _api = ApiService();
  final StorageService _storage = StorageService();

  AuthNotifier() : super(AuthState(isLoading: true)) {
    _init();
  }

  Future<void> _init() async {
    final token = await _storage.getToken();
    if (token != null) {
      try {
        final profile = await _api.getCurrentUser();
        state = AuthState(user: profile, isLoading: false);
        return;
      } catch (_) {
        await _storage.clearAll();
      }
    }
    state = AuthState(isLoading: false);
  }

  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final res = await _api.login(email, password);
      final user = UserModel.fromJson(res['user']);
      state = AuthState(user: user, isLoading: false);
    } catch (e) {
      state = AuthState(isLoading: false, error: e.toString().replaceAll('Exception: ', ''));
    }
  }

  Future<void> register({
    required String name,
    required String email,
    required String password,
    required String role,
    String? studentId,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final res = await _api.register(
        name: name,
        email: email,
        password: password,
        role: role,
        studentId: studentId,
      );
      final user = UserModel.fromJson(res['user']);
      state = AuthState(user: user, isLoading: false);
    } catch (e) {
      state = AuthState(isLoading: false, error: e.toString().replaceAll('Exception: ', ''));
    }
  }

  Future<void> logout() async {
    await _storage.clearAll();
    state = AuthState(user: null);
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});
