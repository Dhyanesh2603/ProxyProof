import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  static const String appName = 'ProxyProof';
  static const String appVersion = '1.0.0';

  // Base API URL default: USB reverse tethering uses 127.0.0.1:8005
  static const String defaultBaseUrl = 'http://127.0.0.1:8005/api/v1';

  static String _baseUrl = defaultBaseUrl;
  static String get baseUrl => _baseUrl;

  static String get wsUrl {
    final uri = Uri.parse(_baseUrl);
    final wsScheme = uri.scheme == 'https' ? 'wss' : 'ws';
    final portStr = uri.hasPort ? ':${uri.port}' : '';
    return '$wsScheme://${uri.host}$portStr';
  }

  static Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString('server_url');
    if (saved != null && !saved.contains('10.0.2.2')) {
      _baseUrl = saved;
    } else {
      _baseUrl = defaultBaseUrl;
    }
  }

  static Future<void> setBaseUrl(String url) async {
    var formatted = url.trim();
    if (formatted.endsWith('/')) {
      formatted = formatted.substring(0, formatted.length - 1);
    }
    if (!formatted.endsWith('/api/v1')) {
      formatted = '$formatted/api/v1';
    }
    _baseUrl = formatted;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('server_url', _baseUrl);
  }

  // BLE Configuration
  static const int bleManufacturerId = 0x5050; // 'PP' (ProxyProof identifier)
  static const int defaultRssiThreshold = -75; // dBm cutoff
  static const Duration tokenScanInterval = Duration(seconds: 3);
  static const Duration tokenRotationInterval = Duration(seconds: 5);
}
