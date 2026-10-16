import 'package:flutter/material.dart';

class BleRadar extends StatefulWidget {
  final bool isScanning;
  final double size;

  const BleRadar({
    super.key,
    required this.isScanning,
    this.size = 120,
  });

  @override
  State<BleRadar> createState() => _BleRadarState();
}

class _BleRadarState extends State<BleRadar> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );

    if (widget.isScanning) {
      _controller.repeat();
    }
  }

  @override
  void didUpdateWidget(covariant BleRadar oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isScanning && !_controller.isAnimating) {
      _controller.repeat();
    } else if (!widget.isScanning && _controller.isAnimating) {
      _controller.stop();
      _controller.reset();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Animated concentric pulse ring
          if (widget.isScanning)
            AnimatedBuilder(
              animation: _controller,
              builder: (context, child) {
                final scale = 0.5 + (_controller.value * 0.5);
                final opacity = (1.0 - _controller.value).clamp(0.0, 1.0);
                return Transform.scale(
                  scale: scale,
                  child: Container(
                    width: widget.size,
                    height: widget.size,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: const Color(0xFF10B981).withValues(alpha: opacity * 0.5),
                        width: 1.5,
                      ),
                    ),
                  ),
                );
              },
            ),

          // Inner static ring
          Container(
            width: widget.size * 0.55,
            height: widget.size * 0.55,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: const Color(0xFF18181B),
              border: Border.all(
                color: widget.isScanning ? const Color(0xFF10B981) : const Color(0xFF3F3F46),
                width: 1.2,
              ),
            ),
            child: Icon(
              Icons.bluetooth,
              size: widget.size * 0.28,
              color: widget.isScanning ? const Color(0xFF34D399) : const Color(0xFFA1A1AA),
            ),
          ),
        ],
      ),
    );
  }
}
