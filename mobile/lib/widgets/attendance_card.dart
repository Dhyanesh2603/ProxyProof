import 'package:flutter/material.dart';
import '../models/attendance_model.dart';
import 'status_badge.dart';
import 'enterprise_card.dart';

class AttendanceCard extends StatelessWidget {
  final AttendanceModel record;

  const AttendanceCard({super.key, required this.record});

  @override
  Widget build(BuildContext context) {
    return EnterpriseCard(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                record.courseCode,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              StatusBadge(status: record.status),
            ],
          ),
          const SizedBox(height: 4),
          if (record.courseName != null && record.courseName!.isNotEmpty)
            Text(
              record.courseName!,
              style: const TextStyle(color: Color(0xFFA1A1AA), fontSize: 12),
            ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.wifi, size: 12, color: Color(0xFF71717A)),
                  const SizedBox(width: 4),
                  Text(
                    '${record.rssi} dBm',
                    style: TextStyle(
                      color: record.rssi >= -75 ? const Color(0xFF34D399) : const Color(0xFFF87171),
                      fontSize: 11,
                      fontFamily: 'monospace',
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Session ${record.sessionCode}',
                    style: const TextStyle(color: Color(0xFF71717A), fontSize: 11, fontFamily: 'monospace'),
                  ),
                ],
              ),
              if (record.markedAt != null)
                Text(
                  record.markedAt!.length > 16 ? record.markedAt!.substring(0, 16).replaceAll('T', ' ') : record.markedAt!,
                  style: const TextStyle(color: Color(0xFF71717A), fontSize: 11, fontFamily: 'monospace'),
                ),
            ],
          ),
          if (record.rejectionReason != null && record.rejectionReason!.isNotEmpty) ...[
            const SizedBox(height: 6),
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: const Color(0x4D4C0519),
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: const Color(0x80881337), width: 0.8),
              ),
              child: Text(
                record.rejectionReason!,
                style: const TextStyle(color: Color(0xFFFECDD3), fontSize: 11),
              ),
            ),
          ]
        ],
      ),
    );
  }
}
