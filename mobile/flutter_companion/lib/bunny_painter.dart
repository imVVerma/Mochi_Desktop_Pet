import 'dart:math' as math;
import 'package:flutter/material.dart';

/**
 * BunnyPainter:
 * Procedural Canvas CustomPainter rendering Mochi's Floppy Bunny model:
 * - Animated breathing and ear tilt.
 * - Gentle bouncing and micro-wiggle.
 * - Blushing cheeks and sparkle eyes.
 */
class BunnyPainter extends CustomPainter {
  final double phase; // 0.0 to 1.0
  final bool isDragging;
  final Color bodyColor;
  final String accessory;

  BunnyPainter({
    required this.phase,
    required this.isDragging,
    required this.bodyColor,
    required this.accessory,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2 + 10;

    final breath = math.sin(phase * 2 * math.pi) * 2.5;
    final earAngle = math.sin(phase * 2 * math.pi) * 0.08;

    final bodyPaint = Paint()
      ..color = bodyColor
      ..style = PaintingStyle.fill;

    final innerEarPaint = Paint()
      ..color = const Color(0xFFFFD1DC)
      ..style = PaintingStyle.fill;

    final blushPaint = Paint()
      ..color = const Color(0xFFFF9AA2).withOpacity(0.55)
      ..style = PaintingStyle.fill;

    final eyePaint = Paint()
      ..color = const Color(0xFF2C2C2C)
      ..style = PaintingStyle.fill;

    final sparklePaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    // Draw Droopy Ears (left and right)
    _drawFloppyEar(canvas, cx - 26, cy - 22, -0.45 + earAngle, bodyPaint, innerEarPaint);
    _drawFloppyEar(canvas, cx + 26, cy - 22, 0.45 - earAngle, bodyPaint, innerEarPaint);

    // Draw Head & Chubby Cheeks
    final headRadius = 40.0 + (breath * 0.3);
    canvas.drawCircle(Offset(cx, cy), headRadius, bodyPaint);

    // Draw Blush
    canvas.drawCircle(Offset(cx - 24, cy + 8), 8.0, blushPaint);
    canvas.drawCircle(Offset(cx + 24, cy + 8), 8.0, blushPaint);

    // Draw Sparkle Eyes
    canvas.drawCircle(Offset(cx - 15, cy - 4), 5.0, eyePaint);
    canvas.drawCircle(Offset(cx - 13.5, cy - 5.5), 1.8, sparklePaint);

    canvas.drawCircle(Offset(cx + 15, cy - 4), 5.0, eyePaint);
    canvas.drawCircle(Offset(cx + 16.5, cy - 5.5), 1.8, sparklePaint);

    // Nose
    final nosePaint = Paint()
      ..color = const Color(0xFFE57373)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(Offset(cx, cy + 3), 2.2, nosePaint);

    // Optional Ribbon accessory
    if (accessory != 'None') {
      final accPaint = Paint()..color = const Color(0xFFFF6B6B);
      canvas.drawCircle(Offset(cx - 26, cy - 30), 6, accPaint);
      canvas.drawCircle(Offset(cx - 16, cy - 30), 6, accPaint);
      canvas.drawCircle(Offset(cx - 21, cy - 30), 3.5, sparklePaint);
    }
  }

  void _drawFloppyEar(
    Canvas canvas,
    double x,
    double y,
    double angle,
    Paint outerPaint,
    Paint innerPaint,
  ) {
    canvas.save();
    canvas.translate(x, y);
    canvas.rotate(angle);

    final outerRRect = RRect.fromRectAndRadius(
      const Rect.fromLTWH(-11, 0, 22, 50),
      const Radius.circular(11),
    );
    canvas.drawRRect(outerRRect, outerPaint);

    final innerRRect = RRect.fromRectAndRadius(
      const Rect.fromLTWH(-7, 6, 14, 38),
      const Radius.circular(7),
    );
    canvas.drawRRect(innerRRect, innerPaint);

    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant BunnyPainter oldDelegate) {
    return oldDelegate.phase != phase ||
        oldDelegate.isDragging != isDragging ||
        oldDelegate.bodyColor != bodyColor ||
        oldDelegate.accessory != accessory;
  }
}
