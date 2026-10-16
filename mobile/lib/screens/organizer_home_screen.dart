import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../providers/session_provider.dart';
import '../models/session_model.dart';
import '../widgets/enterprise_card.dart';
import '../widgets/status_badge.dart';
import 'organizer_session_screen.dart';

class OrganizerHomeScreen extends ConsumerWidget {
  const OrganizerHomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final user = authState.user;
    final sessionsAsync = ref.watch(sessionsListProvider);

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
              child: const Icon(Icons.security, size: 14, color: Color(0xFF34D399)),
            ),
            const SizedBox(width: 8),
            const Text(
              'ProxyProof Organizer',
              style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, size: 18, color: Color(0xFFA1A1AA)),
            tooltip: 'Refresh Sessions',
            onPressed: () => ref.refresh(sessionsListProvider),
          ),
          IconButton(
            icon: const Icon(Icons.logout, size: 18, color: Color(0xFFA1A1AA)),
            tooltip: 'Logout',
            onPressed: () => ref.read(authProvider.notifier).logout(),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => ref.refresh(sessionsListProvider),
        color: const Color(0xFF34D399),
        backgroundColor: const Color(0xFF18181B),
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Organizer Profile Card
              EnterpriseCard(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          user?.fullName ?? 'Organizer',
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          user?.email ?? '',
                          style: const TextStyle(color: Color(0xFF71717A), fontSize: 12, fontFamily: 'monospace'),
                        ),
                      ],
                    ),
                    const StatusBadge(status: 'ORGANIZER'),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Sessions Section
              const Text(
                'ATTENDANCE SESSIONS',
                style: TextStyle(color: Color(0xFF71717A), fontSize: 11, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
              ),
              const SizedBox(height: 10),

              sessionsAsync.when(
                data: (sessions) {
                  if (sessions.isEmpty) {
                    return const EnterpriseCard(
                      child: Center(
                        child: Padding(
                          padding: EdgeInsets.symmetric(vertical: 24),
                          child: Text(
                            'No sessions found. Create a session on the Web Console.',
                            style: TextStyle(color: Color(0xFF71717A), fontSize: 12),
                          ),
                        ),
                      ),
                    );
                  }

                  return Column(
                    children: sessions.map((sess) => _buildSessionTile(context, sess)).toList(),
                  );
                },
                loading: () => const Center(
                  child: Padding(
                    padding: EdgeInsets.symmetric(vertical: 32),
                    child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF34D399)),
                  ),
                ),
                error: (err, _) => EnterpriseCard(
                  child: Center(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      child: Text('Error: $err', style: const TextStyle(color: Color(0xFFF87171), fontSize: 12)),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSessionTile(BuildContext context, SessionModel sess) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: EnterpriseCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  sess.courseCode,
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
                ),
                StatusBadge(status: sess.status),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              '${sess.courseName} (Section ${sess.section})',
              style: const TextStyle(color: Color(0xFFA1A1AA), fontSize: 12),
            ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Code: ${sess.sessionCode}',
                  style: const TextStyle(color: Color(0xFF71717A), fontSize: 11, fontFamily: 'monospace'),
                ),
                Text(
                  'Cutoff: ${sess.rssiThreshold} dBm',
                  style: const TextStyle(color: Color(0xFF71717A), fontSize: 11, fontFamily: 'monospace'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => OrganizerSessionScreen(session: sess),
                    ),
                  );
                },
                icon: Icon(
                  sess.isActive ? Icons.radio : Icons.play_arrow,
                  size: 14,
                  color: Colors.black,
                ),
                label: Text(
                  sess.isActive ? 'Open Live BLE Beacon' : 'View Session Broadcast',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: Colors.black,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  elevation: 0,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
