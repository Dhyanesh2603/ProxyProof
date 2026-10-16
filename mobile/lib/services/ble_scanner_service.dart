import 'dart:async';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';
import '../config/app_config.dart';
import '../models/ble_packet.dart';

class BleScannerService {
  final _packetController = StreamController<BlePacket>.broadcast();
  Stream<BlePacket> get packetStream => _packetController.stream;

  StreamSubscription<List<ScanResult>>? _scanSubscription;
  bool _isScanning = false;
  bool get isScanning => _isScanning;

  int _currentRssiThreshold = AppConfig.defaultRssiThreshold;

  void setRssiThreshold(int threshold) {
    _currentRssiThreshold = threshold;
  }

  Future<bool> isBluetoothSupportedAndOn() async {
    try {
      final isSupported = await FlutterBluePlus.isSupported;
      if (!isSupported) return false;
      final adapterState = await FlutterBluePlus.adapterState.first;
      return adapterState == BluetoothAdapterState.on;
    } catch (_) {
      return false;
    }
  }

  Future<void> startScanning({int? rssiThreshold}) async {
    if (_isScanning) return;
    if (rssiThreshold != null) _currentRssiThreshold = rssiThreshold;

    final ready = await isBluetoothSupportedAndOn();
    if (!ready) {
      // Bluetooth is unavailable or off
    }

    _isScanning = true;

    try {
      // Listen to scan results continuously
      _scanSubscription = FlutterBluePlus.onScanResults.listen((results) {
        for (ScanResult r in results) {
          _processScanResult(r);
        }
      }, onError: (e) {
        // scan error
      });

      await FlutterBluePlus.startScan(
        timeout: null, // continuous scan
        androidUsesFineLocation: true,
      );
    } catch (_) {
      _isScanning = false;
    }
  }

  void _processScanResult(ScanResult r) {
    // Check manufacturer data map
    final mData = r.advertisementData.manufacturerData;

    // Check if ProxyProof company identifier 0x5050 exists
    if (mData.containsKey(AppConfig.bleManufacturerId)) {
      final payload = mData[AppConfig.bleManufacturerId]!;
      // Full frame with prefix
      final fullBytes = [0x50, 0x50, ...payload];
      final packet = BlePacket.parse(fullBytes, r.rssi);
      if (packet != null && packet.rssi >= _currentRssiThreshold) {
        _packetController.add(packet);
      }
    } else {
      // Alternatively, some stacks place entire 26-byte frame in value
      for (final entry in mData.entries) {
        final bytes = entry.value;
        if (bytes.length >= 24) {
          final candidate = [entry.key & 0xFF, (entry.key >> 8) & 0xFF, ...bytes];
          final packet = BlePacket.parse(candidate, r.rssi);
          if (packet != null && packet.rssi >= _currentRssiThreshold) {
            _packetController.add(packet);
            break;
          }
        }
      }
    }
  }

  /// Inject simulated packet (useful for testing, emulators or desktop preview)
  void injectSimulatedPacket(BlePacket packet) {
    if (packet.rssi >= _currentRssiThreshold) {
      _packetController.add(packet);
    }
  }

  Future<void> stopScanning() async {
    if (!_isScanning) return;
    _isScanning = false;
    await _scanSubscription?.cancel();
    _scanSubscription = null;
    try {
      await FlutterBluePlus.stopScan();
    } catch (_) {}
  }

  void dispose() {
    stopScanning();
    _packetController.close();
  }
}
