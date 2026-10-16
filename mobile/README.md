# ProxyProof Mobile App (Flutter & Riverpod)

The mobile client for the **ProxyProof BLE-Based Smart Attendance System**.

---

## Key Capabilities

1. **Continuous BLE Scanning**: Listens for the instructor's rotating advertising packet using `flutter_blue_plus`.
2. **Proximity & RSSI Validation**: Filters out weak stray signals outside classroom boundary (attenuated below `-75 dBm`).
3. **Cryptographic Token Verification**: Decodes the 26-byte manufacturer advertisement frame (`0x5050` prefix, uint32 Session ID, uint32 Window Index, and 16-character HMAC token).
4. **Device Binding Enforcement**: Extracts the hardware UUID (`device_info_plus`) and sends it alongside the rotating token. The backend verifies that the phone belongs to the logged-in student.
5. **Zero-Interaction Attendance**: No QR scanning or button pressing required. As soon as the student steps inside the classroom with Bluetooth enabled, attendance is verified automatically.
6. **Built-in Dev Simulator**: When testing on emulators without BLE hardware, tap **"Simulate Beacon Packet"** to test the entire end-to-end verification pipeline.

---

## Folder Structure

```
mobile/
├── pubspec.yaml
├── lib/
│   ├── main.dart
│   ├── config/
│   │   └── app_config.dart
│   ├── models/
│   │   ├── user_model.dart
│   │   ├── session_model.dart
│   │   ├── attendance_model.dart
│   │   └── ble_packet.dart
│   ├── services/
│   │   ├── api_service.dart
│   │   ├── ble_scanner_service.dart
│   │   ├── ble_advertiser_service.dart
│   │   ├── device_info_service.dart
│   │   └── storage_service.dart
│   ├── providers/
│   │   ├── auth_provider.dart
│   │   ├── session_provider.dart
│   │   ├── attendance_provider.dart
│   │   └── ble_provider.dart
│   ├── widgets/
│   │   ├── ble_radar.dart
│   │   ├── status_badge.dart
│   │   ├── attendance_card.dart
│   │   └── enterprise_card.dart
│   └── screens/
│       ├── login_screen.dart
│       ├── student_home_screen.dart
│       ├── organizer_home_screen.dart
│       ├── organizer_session_screen.dart
│       ├── device_registration_screen.dart
│       └── attendance_history_screen.dart
```

---

## Running the App

```bash
cd mobile
flutter pub get
flutter run
```

### Backend Endpoint Configuration
Edit `lib/config/app_config.dart`:
- Android Emulator: `http://10.0.2.2:8000/api/v1`
- iOS Simulator: `http://127.0.0.1:8000/api/v1`
- Physical Phone over LAN: `http://<YOUR_LOCAL_IP>:8000/api/v1`
