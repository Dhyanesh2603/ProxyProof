import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../models/user_model.dart';
import '../models/session_model.dart';
import 'storage_service.dart';

class ApiService {
  final StorageService _storage = StorageService();

  Future<Map<String, String>> _headers() async {
    final token = await _storage.getToken();
    final map = {'Content-Type': 'application/json'};
    if (token != null) {
      map['Authorization'] = 'Bearer $token';
    }
    return map;
  }

  // Authentication
  Future<Map<String, dynamic>> login(String email, String password) async {
    final url = Uri.parse('${AppConfig.baseUrl}/auth/login');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final token = data['access_token'] as String;
      final user = UserModel.fromJson(data['user']);
      await _storage.saveToken(token);
      await _storage.saveUser(user);
      return data;
    } else {
      final err = jsonDecode(response.body);
      throw Exception(err['detail'] ?? 'Login failed');
    }
  }

  Future<Map<String, dynamic>> register({
    required String name,
    required String email,
    required String password,
    required String role,
    String? studentId,
  }) async {
    final url = Uri.parse('${AppConfig.baseUrl}/auth/register');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'full_name': name,
        'email': email,
        'password': password,
        'role': role,
        'student_id': studentId,
      }),
    );

    if (response.statusCode == 201) {
      final data = jsonDecode(response.body);
      final token = data['access_token'] as String;
      final user = UserModel.fromJson(data['user']);
      await _storage.saveToken(token);
      await _storage.saveUser(user);
      return data;
    } else {
      final err = jsonDecode(response.body);
      throw Exception(err['detail'] ?? 'Registration failed');
    }
  }

  Future<UserModel> getCurrentUser() async {
    final url = Uri.parse('${AppConfig.baseUrl}/auth/me');
    final response = await http.get(url, headers: await _headers());
    if (response.statusCode == 200) {
      return UserModel.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to fetch user profile');
  }

  // Sessions
  Future<List<SessionModel>> getSessions() async {
    final url = Uri.parse('${AppConfig.baseUrl}/sessions');
    final response = await http.get(url, headers: await _headers());
    if (response.statusCode == 200) {
      final List list = jsonDecode(response.body);
      return list.map((e) => SessionModel.fromJson(e)).toList();
    }
    throw Exception('Failed to load sessions');
  }

  Future<Map<String, dynamic>> getSessionToken(int sessionId) async {
    final url = Uri.parse('${AppConfig.baseUrl}/sessions/$sessionId/token');
    final response = await http.get(url, headers: await _headers());
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to fetch rotating token');
  }

  // Attendance
  Future<Map<String, dynamic>> markAttendance({
    required int sessionId,
    required String token,
    required String deviceUuid,
    required int rssi,
  }) async {
    final url = Uri.parse('${AppConfig.baseUrl}/attendance/mark');
    final response = await http.post(
      url,
      headers: await _headers(),
      body: jsonEncode({
        'session_id': sessionId,
        'token': token,
        'device_uuid': deviceUuid,
        'rssi': rssi,
      }),
    );

    final data = jsonDecode(response.body);
    return data;
  }

  Future<Map<String, dynamic>> getStudentAttendanceHistory() async {
    final url = Uri.parse('${AppConfig.baseUrl}/attendance/history');
    final response = await http.get(url, headers: await _headers());
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load attendance history');
  }

  // Devices
  Future<Map<String, dynamic>> registerDevice(String deviceUuid, String deviceName) async {
    final url = Uri.parse('${AppConfig.baseUrl}/devices/register');
    final response = await http.post(
      url,
      headers: await _headers(),
      body: jsonEncode({
        'device_uuid': deviceUuid,
        'device_name': deviceName,
      }),
    );
    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    }
    final err = jsonDecode(response.body);
    throw Exception(err['detail'] ?? 'Device registration failed');
  }

  Future<Map<String, dynamic>> getMyDevice() async {
    final url = Uri.parse('${AppConfig.baseUrl}/devices/my-device');
    final response = await http.get(url, headers: await _headers());
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to get device info');
  }

  Future<Map<String, dynamic>> requestDeviceChange(String newDeviceUuid, String newDeviceName, String reason) async {
    final url = Uri.parse('${AppConfig.baseUrl}/devices/change-request');
    final response = await http.post(
      url,
      headers: await _headers(),
      body: jsonEncode({
        'new_device_uuid': newDeviceUuid,
        'new_device_name': newDeviceName,
        'reason': reason,
      }),
    );
    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    }
    final err = jsonDecode(response.body);
    throw Exception(err['detail'] ?? 'Device change request failed');
  }
}
