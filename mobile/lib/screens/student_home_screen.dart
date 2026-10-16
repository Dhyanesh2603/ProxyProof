import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../providers/ble_provider.dart';
import '../providers/attendance_provider.dart';
import '../widgets/ble_radar.dart';
import '../widgets/enterprise_card.dart';
import '../widgets/status_badge.dart';
import 'attendance_history_screen.dart';
import 'device_registration_screen.dart';

class StudentHomeScreen extends ConsumerStatefulWidget {
  const StudentHomeScreen({super.key});

  @override
  ConsumerState<StudentHomeScreen> createState() => _StudentHomeScreenState();
}

class _StudentHomeScreenState extends ConsumerState<StudentHomeScreen> {
  @override
  void initState() {
    super.initState();
    // Start continuous automatic BLE scanning upon screen entry
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(bleScanProvider.notifier).startScan();
      ref.read(attendanceHistoryProvider.notifier).loadHistory();
    });
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final user = authState.user;
    final scanState = ref.watch(bleScanProvider);
    final historyState = ref.watch(attendanceHistoryProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF09090B),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0C0C0E),
        elevation: 0,
        title: Row(
          children: [
            Container(
              width: 26,
              height: 26,
              decoration: BoxDecoration(
                color: const Color(0xFF18181B),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: const Color(0xFF27272A)),
              ),
              child: const Icon(Icons.shield_outlined, size: 14, color: Color(0xFF34D399)),
            ),
            const SizedBox(width: 8),
            const Text(
              'ProxyProof Student',
              style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.phone_android, size: 18, color: Color(0xFFA1A1AA)),
            tooltip: 'Device Binding',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const DeviceRegistrationScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout, size: 18, color: Color(0xFFA1A1AA)),
            tooltip: 'Logout',
            onPressed: () => ref.read(authProvider.notifier).logout(),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(attendanceHistoryProvider.notifier).loadHistory(),
        color: const Color(0xFF34D399),
        backgroundColor: const Color(0xFF18181B),
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Student ID & Compliance Banner
              EnterpriseCard(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          user?.fullName ?? 'Student',
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          user?.studentId ?? 'N/A',
                          style: const TextStyle(color: Color(0xFF71717A), fontSize: 12, fontFamily: 'monospace'),
                        ),
                      ],
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        const Text(
                          'ATTENDANCE',
                          style: TextStyle(color: Color(0xFF71717A), fontSize: 9, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${historyState.percentage.toStringAsFixed(1)}%',
                          style: const TextStyle(color: Color(0xFF34D399), fontWeight: FontWeight.bold, fontSize: 16, fontFamily: 'monospace'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Scanning Radar & Live Status
              EnterpriseCard(
                padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
                child: Column(
                  children: [
                    BleRadar(
                      isScanning: scanState.isScanning,
                      size: 130,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      scanState.isScanning ? 'SCANNING CLASSROOM BLE BEACONS' : 'SCANNER IDLE',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        fontFamily: 'monospace',
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Attendance marks automatically once physically inside the room.',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Color(0xFF71717A), fontSize: 11),
                    ),
                    const SizedBox(height: 14),

                    // Last detected packet telemetry
                    if (scanState.lastPacket != null) ...[
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: const Color(0xFF09090B),
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(color: const Color(0xFF27272A)),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceAround,
                          children: [
                            Column(
                              children: [
                                const Text('SESSION', style: TextStyle(color: Color(0xFF71717A), fontSize: 9, fontFamily: 'monospace')),
                                const SizedBox(height: 2),
                                Text('#${scanState.lastPacket!.sessionId}', style: const TextStyle(color: Colors.white, fontSize: 12, fontFamily: 'monospace', fontWeight: FontWeight.bold)),
                              ],
                            ),
                            Column(
                              children: [
                                const Text('RSSI SIGNAL', style: TextStyle(color: Color(0xFF71717A), fontSize: 9, fontFamily: 'monospace')),
                                const SizedBox(height: 2),
                                Text(
                                  '${scanState.lastPacket!.rssi} dBm',
                                  style: TextStyle(
                                    color: scanState.lastPacket!.rssi >= -75 ? const Color(0xFF34D399) : const Color(0xFFF87171),
                                    fontSize: 12,
                                    fontFamily: 'monospace',
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                            Column(
                              children: [
                                const Text('ROTATING TOKEN', style: TextStyle(color: Color(0xFF71717A), fontSize: 9, fontFamily: 'monospace')),
                                const SizedBox(height: 2),
                                Text(
                                  scanState.lastPacket!.token.substring(0, 8),
                                  style: const TextStyle(color: Color(0xFFA1A1AA), fontSize: 12, fontFamily: 'monospace'),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                    ],

                    // Attendance Pipeline Outcome Banner
                    if (scanState.isMarking) ...[
                      const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF34D399))),
                          SizedBox(width: 8),
                          Text('Verifying token & binding with backend...', style: TextStyle(color: Color(0xFFA1A1AA), fontSize: 11)),
                        ],
                      ),
                    ] else if (scanState.successMessage != null) ...[
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        decoration: BoxDecoration(
                          color: const Color(0xFF022C22),
                          border: Border.all(color: const Color(0xFF064E3B)),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.check_circle, size: 14, color: Color(0xFF34D399)),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                scanState.successMessage!,
                                style: const TextStyle(color: Color(0xFF6EE7B7), fontSize: 11, fontWeight: FontWeight.w600),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ] else if (scanState.errorMessage != null) ...[
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        decoration: BoxDecoration(
                          color: const Color(0xFF4C0519),
                          border: Border.all(color: const Color(0xFF881337)),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.cancel, size: 14, color: Color(0xFFF87171)),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                scanState.errorMessage!,
                                style: const TextStyle(color: Color(0xFFFECDD3), fontSize: 11),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Test Simulation Button (Useful on emulators or when BLE hardware is off)
              OutlinedButton.icon(
                onPressed: () {
                  // Simulate receiving broadcast for Session 1 with -65 dBm
                  ref.read(bleScanProvider.notifier).simulatePacket(1, 'e3b0c44298fc1c14', -65);
                },
                icon: const Icon(Icons.play_circle_outline, size: 14, color: Color(0xFFA1A1AA)),
                label: const Text('Simulate Beacon Packet (Dev Mode)', style: TextStyle(color: Color(0xFFA1A1AA), fontSize: 11)),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: Color(0xFF27272A)),
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                ),
              ),
              const SizedBox(height: 16),

              // Recent Attendance Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'RECENT ATTENDANCE',
                    style: TextStyle(color: Color(0xFF71717A), fontSize: 11, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                  ),
                  TextButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => const AttendanceHistoryScreen()),
                      );
                    },
                    child: const Text('View All', style: TextStyle(color: Color(0xFF34D399), fontSize: 11)),
                  ),
                ],
              ),
              const SizedBox(height: 6),

              if (historyState.records.isEmpty)
                const EnterpriseCard(
                  child: Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(vertical: 12),
                      child: Text('No attendance records logged yet.', style: TextStyle(color: Color(0xFF71717A), fontSize: 12)),
                    ),
                  ),
                )
              else
                ...historyState.records.take(3).map((r) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: EnterpriseCard(
                    padding: const EdgeInsets.all(12),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(r.courseCode, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                            const SizedBox(height: 2),
                            Text(
                              r.markedAt?.substring(0, 10) ?? 'Recent',
                              style: const TextStyle(color: Color(0xFF71717A), fontSize: 11, fontFamily: 'monospace'),
                            ),
                          ],
                        ),
                        StatusBadge(status: r.status),
                      ],
                    ),
                  ),
                )),
            ],
          ),
        ),
      ),
    );
  }
}
