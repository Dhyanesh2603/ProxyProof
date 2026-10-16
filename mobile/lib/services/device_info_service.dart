import 'dart:io';
import 'package:device_info_plus/device_info_plus.dart';
import 'storage_service.dart';

class DeviceInfoService {
  final _deviceInfo = DeviceInfoPlugin();
  final _storage = StorageService();

  Future<Map<String, String>> getDeviceInfo() async {
    // Check if we have a locally persisted hardware binding UUID
    String? storedUuid = await _storage.getDeviceUuid();
    String deviceName = 'Generic Phone';

    try {
      if (Platform.isAndroid) {
        final androidInfo = await _deviceInfo.androidInfo;
        storedUuid ??= 'DEV-AND-${androidInfo.id}';
        deviceName = '${androidInfo.brand.toUpperCase()} ${androidInfo.model}';
      } else if (Platform.isIOS) {
        final iosInfo = await _deviceInfo.iosInfo;
        storedUuid ??= 'DEV-IOS-${iosInfo.identifierForVendor ?? "UNKNOWN"}';
        deviceName = iosInfo.utsname.machine;
      } else {
        storedUuid ??= 'DEV-UUID-${DateTime.now().millisecondsSinceEpoch}';
        deviceName = 'Mobile Device';
      }
    } catch (_) {
      storedUuid ??= 'DEV-UUID-FALLBACK-${DateTime.now().millisecondsSinceEpoch}';
      deviceName = 'Smartphone Device';
    }

    await _storage.saveDeviceUuid(storedUuid);

    return {
      'uuid': storedUuid,
      'name': deviceName,
    };
  }
}
