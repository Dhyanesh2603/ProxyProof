import 'package:flutter/material.dart';

class EnterpriseCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final Color? borderColor;

  const EnterpriseCard({
    super.key,
    required this.child,
    this.padding,
    this.borderColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding ?? const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF121214),
        border: Border.all(
          color: borderColor ?? const Color(0xFF27272A),
          width: 1,
        ),
        borderRadius: BorderRadius.circular(6),
      ),
      child: child,
    );
  }
}
