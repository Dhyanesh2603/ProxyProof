import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/ble_packet.dart';
import '../services/ble_scanner_service.dart';
import '../services/ble_advertiser_service.dart';
import '../services/device_info_service.dart';
import '../services/api_service.dart';

class BleScanState {
  final bool isScanning;
  final BlePacket? lastPacket;
  final bool isMarking;
  final String? successMessage;
  final String? errorMessage;
  final Set<int> markedSessions;

  BleScanState({
    this.isScanning = false,
    this.lastPacket,
    this.isMarking = false,
    this.successMessage,
    this.errorMessage,
    Set<int>? markedSessions,
  }) : markedSessions = markedSessions ?? {};

  BleScanState copyWith({
    bool? isScanning,
    BlePacket? lastPacket,
    bool? isMarking,
    String? successMessage,
    String? errorMessage,
    Set<int>? markedSessions,
  }) {
    return BleScanState(
      isScanning: isScanning ?? this.isScanning,
      lastPacket: lastPacket ?? this.lastPacket,
      isMarking: isMarking ?? this.isMarking,
      successMessage: successMessage,
      errorMessage: errorMessage,
      markedSessions: markedSessions ?? this.markedSessions,
    );
  }
}

class BleScanNotifier extends StateNotifier<BleScanState> {
  final BleScannerService _scanner = BleScannerService();
  final DeviceInfoService _deviceInfo = DeviceInfoService();
  final ApiService _api = ApiService();
  StreamSubscription<BlePacket>? _sub;

  BleScanNotifier() : super(BleScanState()) {
    _listenPackets();
  }

  void _listenPackets() {
    _sub = _scanner.packetStream.listen((packet) {
      state = state.copyWith(lastPacket: packet);
      _autoMarkAttendance(packet);
    });
  }

  Future<void> startScan({int rssiThreshold = -75}) async {
    state = state.copyWith(isScanning: true, errorMessage: null, successMessage: null);
    await _scanner.startScanning(rssiThreshold: rssiThreshold);
  }

  Future<void> stopScan() async {
    await _scanner.stopScanning();
    state = state.copyWith(isScanning: false);
  }

  Future<void> _autoMarkAttendance(BlePacket packet) async {
    // Prevent duplicate attempts for the same session during app lifecycle
    if (state.markedSessions.contains(packet.sessionId) || state.isMarking) {
      return;
    }

    state = state.copyWith(isMarking: true, errorMessage: null);

    try {
      final dev = await _deviceInfo.getDeviceInfo();
      final res = await _api.markAttendance(
        sessionId: packet.sessionId,
        token: packet.token,
        deviceUuid: dev['uuid']!,
        rssi: packet.rssi,
      );

      final isSuccess = res['success'] == true;
      final msg = res['message'] ?? (isSuccess ? 'Attendance Marked Successfully' : res['rejection_reason'] ?? 'Rejected');

      if (isSuccess) {
        final updatedSet = Set<int>.from(state.markedSessions)..add(packet.sessionId);
        state = state.copyWith(
          isMarking: false,
          successMessage: msg,
          markedSessions: updatedSet,
        );
      } else {
        state = state.copyWith(
          isMarking: false,
          errorMessage: msg,
        );
      }
    } catch (e) {
      state = state.copyWith(
        isMarking: false,
        errorMessage: e.toString().replaceAll('Exception: ', ''),
      );
    }
  }

  /// Inject simulation packet for testing inside emulator
  void simulatePacket(int sessionId, String token, int rssi) {
    final packet = BlePacket(
      magic: 0x5050,
      sessionId: sessionId,
      windowIndex: DateTime.now().millisecondsSinceEpoch ~/ 5000,
      token: token,
      rssi: rssi,
      receivedAt: DateTime.now(),
    );
    _scanner.injectSimulatedPacket(packet);
  }

  @override
  void dispose() {
    _sub?.cancel();
    _scanner.dispose();
    super.dispose();
  }
}

final bleScanProvider = StateNotifierProvider<BleScanNotifier, BleScanState>((ref) {
  return BleScanNotifier();
});

final bleAdvertiserProvider = Provider<BleAdvertiserService>((ref) {
  final service = BleAdvertiserService();
  ref.onDispose(() => service.dispose());
  return service;
});
