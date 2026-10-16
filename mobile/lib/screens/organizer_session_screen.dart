import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/session_model.dart';
import '../services/api_service.dart';
import '../providers/ble_provider.dart';
import '../widgets/ble_radar.dart';
import '../widgets/status_badge.dart';
import '../widgets/enterprise_card.dart';

class OrganizerSessionScreen extends ConsumerStatefulWidget {
  final SessionModel session;

  const OrganizerSessionScreen({super.key, required this.session});

  @override
  ConsumerState<OrganizerSessionScreen> createState() => _OrganizerSessionScreenState();
}

class _OrganizerSessionScreenState extends ConsumerState<OrganizerSessionScreen> {
  final ApiService _api = ApiService();
  String? _currentToken;
  int? _windowIndex;
  double _secondsRemaining = 5.0;
  Timer? _countdownTimer;
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _startBroadcasting();
  }

  void _startBroadcasting() {
    final advertiser = ref.read(bleAdvertiserProvider);
    advertiser.startAdvertising(widget.session.id);

    _pollToken();
    _pollTimer = Timer.periodic(const Duration(seconds: 4), (_) => _pollToken());

    _countdownTimer = Timer.periodic(const Duration(milliseconds: 100), (_) {
      if (mounted) {
        setState(() {
          if (_secondsRemaining <= 0.2) {
            _secondsRemaining = 5.0;
            _pollToken();
          } else {
            _secondsRemaining -= 0.1;
          }
        });
      }
    });
  }

  Future<void> _pollToken() async {
    try {
      final data = await _api.getSessionToken(widget.session.id);
      if (mounted) {
        setState(() {
          _currentToken = data['token'] as String;
          _windowIndex = data['window_index'] as int;
          _secondsRemaining = (data['time_remaining_seconds'] as num).toDouble();
        });
      }
    } catch (_) {}
  }

  @override
  void dispose() {
    _countdownTimer?.cancel();
    _pollTimer?.cancel();
    ref.read(bleAdvertiserProvider).stopAdvertising();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isAdvertising = ref.watch(bleAdvertiserProvider).isAdvertising;

    return Scaffold(
      backgroundColor: const Color(0xFF09090B),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0C0C0E),
        elevation: 0,
        title: Text(
          'Beacon Broadcast: ${widget.session.sessionCode}',
          style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Session Banner
            EnterpriseCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        widget.session.courseCode,
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                      StatusBadge(status: widget.session.status),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    widget.session.courseName,
                    style: const TextStyle(color: Color(0xFFA1A1AA), fontSize: 12),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      _infoPill('Section', widget.session.section),
                      const SizedBox(width: 8),
                      _infoPill('Threshold', '${widget.session.rssiThreshold} dBm'),
                      const SizedBox(width: 8),
                      _infoPill('Window', '5s HMAC'),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Radar & Token Broadcast Card
            EnterpriseCard(
              padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
              child: Column(
                children: [
                  BleRadar(
                    isScanning: isAdvertising,
                    size: 130,
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'BROADCASTING ROTATING BLE PACKET',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      fontFamily: 'monospace',
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Advertising session packet every 100ms. Token rotates every 5s.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Color(0xFF71717A), fontSize: 11),
                  ),
                  const SizedBox(height: 20),

                  // Active Token Display
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: const Color(0xFF09090B),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: const Color(0xFF27272A)),
                    ),
                    child: Column(
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'ACTIVE HMAC TOKEN',
                              style: TextStyle(color: Color(0xFF71717A), fontSize: 10, fontFamily: 'monospace', fontWeight: FontWeight.bold),
                            ),
                            Text(
                              '${_secondsRemaining.toStringAsFixed(1)}s',
                              style: const TextStyle(color: Color(0xFF34D399), fontSize: 11, fontFamily: 'monospace', fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          _currentToken ?? 'INITIALIZING...',
                          style: const TextStyle(
                            color: Color(0xFF34D399),
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            fontFamily: 'monospace',
                            letterSpacing: 2,
                          ),
                        ),
                        const SizedBox(height: 10),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(2),
                          child: LinearProgressIndicator(
                            value: (_secondsRemaining / 5.0).clamp(0.0, 1.0),
                            backgroundColor: const Color(0xFF27272A),
                            color: const Color(0xFF34D399),
                            minHeight: 3,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Window: ${_windowIndex ?? '-'}',
                              style: const TextStyle(color: Color(0xFF71717A), fontSize: 10, fontFamily: 'monospace'),
                            ),
                            const Text(
                              'Algorithm: HMAC-SHA256',
                              style: TextStyle(color: Color(0xFF71717A), fontSize: 10, fontFamily: 'monospace'),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _infoPill(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF18181B),
        border: Border.all(color: const Color(0xFF27272A)),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        '$label: $value',
        style: const TextStyle(color: Color(0xFFA1A1AA), fontSize: 10, fontFamily: 'monospace'),
      ),
    );
  }
}
