import 'dart:convert';
import 'dart:typed_data';

class BlePacket {
  final int magic;
  final int sessionId;
  final int windowIndex;
  final String token;
  final int rssi;
  final DateTime receivedAt;

  BlePacket({
    required this.magic,
    required this.sessionId,
    required this.windowIndex,
    required this.token,
    required this.rssi,
    required this.receivedAt,
  });

  /// Parse the 26-byte manufacturer data payload:
  /// Bytes 0-1: Magic 0x5050 ('PP')
  /// Bytes 2-5: Session ID (big-endian uint32)
  /// Bytes 6-9: Window Index (big-endian uint32)
  /// Bytes 10-25: Token (16-char ASCII string)
  static BlePacket? parse(List<int> rawBytes, int rssi) {
    if (rawBytes.length < 26) return null;

    final data = ByteData.sublistView(Uint8List.fromList(rawBytes));
    final magic = data.getUint16(0, Endian.big);
    if (magic != 0x5050) return null;

    final sessionId = data.getUint32(2, Endian.big);
    final windowIndex = data.getUint32(6, Endian.big);

    final tokenBytes = rawBytes.sublist(10, 26);
    final token = ascii.decode(tokenBytes, allowInvalid: true).replaceAll('\x00', '').trim();

    if (token.isEmpty) return null;

    return BlePacket(
      magic: magic,
      sessionId: sessionId,
      windowIndex: windowIndex,
      token: token,
      rssi: rssi,
      receivedAt: DateTime.now(),
    );
  }

  /// Pack payload into 26 bytes for BLE advertising
  static Uint8List pack(int sessionId, int windowIndex, String token) {
    final bytes = Uint8List(26);
    final byteData = ByteData.sublistView(bytes);

    // Magic 0x5050
    byteData.setUint16(0, 0x5050, Endian.big);
    byteData.setUint32(2, sessionId, Endian.big);
    byteData.setUint32(6, windowIndex, Endian.big);

    final tokenAscii = ascii.encode(token.padRight(16).substring(0, 16));
    bytes.setRange(10, 26, tokenAscii);

    return bytes;
  }
}
