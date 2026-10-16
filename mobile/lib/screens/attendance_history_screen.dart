import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/attendance_provider.dart';
import '../widgets/attendance_card.dart';
import '../widgets/enterprise_card.dart';

class AttendanceHistoryScreen extends ConsumerWidget {
  const AttendanceHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final historyState = ref.watch(attendanceHistoryProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF09090B),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0C0C0E),
        elevation: 0,
        title: const Text(
          'Attendance History',
          style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, size: 18, color: Color(0xFFA1A1AA)),
            onPressed: () => ref.read(attendanceHistoryProvider.notifier).loadHistory(),
          ),
        ],
      ),
      body: historyState.isLoading
          ? const Center(child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF34D399)))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Summary Banner
                  EnterpriseCard(
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        Column(
                          children: [
                            const Text('OVERALL RATE', style: TextStyle(color: Color(0xFF71717A), fontSize: 10, fontFamily: 'monospace')),
                            const SizedBox(height: 4),
                            Text(
                              '${historyState.percentage.toStringAsFixed(1)}%',
                              style: const TextStyle(color: Color(0xFF34D399), fontWeight: FontWeight.bold, fontSize: 18, fontFamily: 'monospace'),
                            ),
                          ],
                        ),
                        Container(width: 1, height: 32, color: const Color(0xFF27272A)),
                        Column(
                          children: [
                            const Text('VERIFIED PRESENT', style: TextStyle(color: Color(0xFF71717A), fontSize: 10, fontFamily: 'monospace')),
                            const SizedBox(height: 4),
                            Text(
                              '${historyState.totalPresent}',
                              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18, fontFamily: 'monospace'),
                            ),
                          ],
                        ),
                        Container(width: 1, height: 32, color: const Color(0xFF27272A)),
                        Column(
                          children: [
                            const Text('TOTAL ATTEMPTS', style: TextStyle(color: Color(0xFF71717A), fontSize: 10, fontFamily: 'monospace')),
                            const SizedBox(height: 4),
                            Text(
                              '${historyState.totalAttempts}',
                              style: const TextStyle(color: Color(0xFFA1A1AA), fontWeight: FontWeight.bold, fontSize: 18, fontFamily: 'monospace'),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  const Text(
                    'SESSION TIMELINE',
                    style: TextStyle(color: Color(0xFF71717A), fontSize: 11, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                  ),
                  const SizedBox(height: 10),

                  if (historyState.records.isEmpty)
                    const EnterpriseCard(
                      child: Center(
                        child: Padding(
                          padding: EdgeInsets.symmetric(vertical: 24),
                          child: Text('No attendance history found.', style: TextStyle(color: Color(0xFF71717A), fontSize: 12)),
                        ),
                      ),
                    )
                  else
                    ...historyState.records.map((rec) => Padding(
                          padding: const EdgeInsets.only(bottom: 10),
                          child: AttendanceCard(record: rec),
                        )),
                ],
              ),
            ),
    );
  }
}
