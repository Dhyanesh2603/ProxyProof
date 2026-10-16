import 'dart:async';
import 'package:flutter/foundation.dart';
import '../config/app_config.dart';
import '../models/ble_packet.dart';
import 'api_service.dart';

class BleAdvertiserService {
  final ApiService _api = ApiService();
  Timer? _rotationTimer;
  bool _isAdvertising = false;
  bool get isAdvertising => _isAdvertising;

  int? _activeSessionId;
  String? _currentToken;
  int? _currentWindowIndex;

  String? get currentToken => _currentToken;
  int? get currentWindowIndex => _currentWindowIndex;

  final _tokenController = StreamController<String>.broadcast();
  Stream<String> get tokenStream => _tokenController.stream;

  Future<void> startAdvertising(int sessionId) async {
    if (_isAdvertising && _activeSessionId == sessionId) return;

    _activeSessionId = sessionId;
    _isAdvertising = true;

    // Fetch initial token and start rotation loop
    await _rotateToken();

    _rotationTimer?.cancel();
    _rotationTimer = Timer.periodic(AppConfig.tokenRotationInterval, (_) {
      _rotateToken();
    });
  }

  Future<void> _rotateToken() async {
    if (!_isAdvertising || _activeSessionId == null) return;
    try {
      final data = await _api.getSessionToken(_activeSessionId!);
      _currentToken = data['token'] as String;
      _currentWindowIndex = data['window_index'] as int;

      // Pack into 26-byte BLE frame
      final bleBytes = BlePacket.pack(
        _activeSessionId!,
        _currentWindowIndex!,
        _currentToken!,
      );

      debugPrint('BLE Broadcasting Packet [${bleBytes.length} bytes]: Hex: ${data['ble_payload_hex']}');

      _tokenController.add(_currentToken!);
    } catch (e) {
      debugPrint('Error rotating advertising token: $e');
    }
  }

  void stopAdvertising() {
    _isAdvertising = false;
    _rotationTimer?.cancel();
    _rotationTimer = null;
    _activeSessionId = null;
    _currentToken = null;
  }

  void dispose() {
    stopAdvertising();
    _tokenController.close();
  }
}
