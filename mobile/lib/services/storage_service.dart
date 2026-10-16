import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';

class StorageService {
  final _secureStorage = const FlutterSecureStorage();
  static const _tokenKey = 'jwt_token';
  static const _userKey = 'cached_user';
  static const _deviceUuidKey = 'bound_device_uuid';

  Future<void> saveToken(String token) async {
    await _secureStorage.write(key: _tokenKey, value: token);
  }

  Future<String?> getToken() async {
    return await _secureStorage.read(key: _tokenKey);
  }

  Future<void> saveUser(UserModel user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userKey, jsonEncode(user.toJson()));
  }

  Future<UserModel?> getUser() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString(_userKey);
    if (data == null) return null;
    try {
      return UserModel.fromJson(jsonDecode(data));
    } catch (_) {
      return null;
    }
  }

  Future<void> saveDeviceUuid(String uuid) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_deviceUuidKey, uuid);
  }

  Future<String?> getDeviceUuid() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_deviceUuidKey);
  }

  Future<void> clearAll() async {
    await _secureStorage.deleteAll();
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
