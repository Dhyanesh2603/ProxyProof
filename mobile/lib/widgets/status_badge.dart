import 'package:flutter/material.dart';

class StatusBadge extends StatelessWidget {
  final String status;

  const StatusBadge({super.key, required this.status});

  @override
  Widget build(BuildContext context) {
    final norm = status.toUpperCase();

    Color dotColor = const Color(0xFFA1A1AA);
    Color textColor = const Color(0xFFD4D4D8);
    Color borderColor = const Color(0xFF27272A);
    Color bgColor = const Color(0xFF18181B);

    if (norm == 'PRESENT' || norm == 'ACTIVE' || norm == 'APPROVED') {
      dotColor = const Color(0xFF34D399); // emerald 400
      textColor = const Color(0xFF6EE7B7);
      borderColor = const Color(0xFF064E3B);
      bgColor = const Color(0xFF022C22);
    } else if (norm == 'LATE' || norm == 'PENDING' || norm == 'WARNING') {
      dotColor = const Color(0xFFFBBF24); // amber 400
      textColor = const Color(0xFFFDE68A);
      borderColor = const Color(0xFF78350F);
      bgColor = const Color(0xFF451A03);
    } else if (norm == 'REJECTED' || norm == 'ENDED' || norm == 'CRITICAL') {
      dotColor = const Color(0xFFF87171); // rose 400
      textColor = const Color(0xFFFECDD3);
      borderColor = const Color(0xFF881337);
      bgColor = const Color(0xFF4C0519);
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: bgColor.withValues(alpha: 0.4),
        border: Border.all(color: borderColor, width: 0.8),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(color: dotColor, shape: BoxShape.circle),
          ),
          const SizedBox(width: 5),
          Text(
            status,
            style: TextStyle(
              color: textColor,
              fontSize: 11,
              fontWeight: FontWeight.w600,
              fontFamily: 'monospace',
            ),
          ),
        ],
      ),
    );
  }
}
