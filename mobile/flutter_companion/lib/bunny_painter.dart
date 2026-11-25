import 'dart:math' as math;
import 'package:flutter/material.dart';

/**
 * BunnyPainter:
 * Procedural Canvas CustomPainter rendering Mochi's Floppy Bunny model:
 * - Animated breathing and soft ear momentum.
 * - Gentle bouncing, eye blinking, and mouse tracking.
 * - Procedural rendering of all 6 wardrobe accessories:
 *   (Crown, Ribbon, Sakura Flower, Glasses, Top Hat, Scarf, Natural).
 * - Soft contact shadow grounding Mochi on screen.
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

    // Contact shadow
    final shadowPaint = Paint()..color = const Color(0x28000000);
    canvas.drawOval(
      Rect.fromCenter(center: Offset(cx, cy + 44), width: 75, height: 14),
      shadowPaint,
    );

    final bodyPaint = Paint()
      ..color = bodyColor
      ..style = PaintingStyle.fill;

    final innerEarPaint = Paint()
      ..color = const Color(0xFFFFD1DC)
      ..style = PaintingStyle.fill;

    final blushPaint = Paint()
      ..color = const Color(0xFFFF9AA2).withValues(alpha: 0.55)
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

    // Blinking logic (subtle natural blink around phase 0.94 - 0.99)
    final isBlinking = phase > 0.93 && phase < 0.98;

    if (isBlinking) {
      final blinkPaint = Paint()
        ..color = const Color(0xFF2C2C2C)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.5
        ..strokeCap = StrokeCap.round;
      canvas.drawLine(Offset(cx - 20, cy - 3), Offset(cx - 10, cy - 3), blinkPaint);
      canvas.drawLine(Offset(cx + 10, cy - 3), Offset(cx + 20, cy - 3), blinkPaint);
    } else {
      // Draw Sparkle Eyes
      canvas.drawCircle(Offset(cx - 15, cy - 4), 5.0, eyePaint);
      canvas.drawCircle(Offset(cx - 13.5, cy - 5.5), 1.8, sparklePaint);
      canvas.drawCircle(Offset(cx - 16.5, cy - 2.5), 1.0, sparklePaint);

      canvas.drawCircle(Offset(cx + 15, cy - 4), 5.0, eyePaint);
      canvas.drawCircle(Offset(cx + 16.5, cy - 5.5), 1.8, sparklePaint);
      canvas.drawCircle(Offset(cx + 13.5, cy - 2.5), 1.0, sparklePaint);
    }

    // Nose
    final nosePaint = Paint()
      ..color = const Color(0xFFE57373)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(Offset(cx, cy + 3.5), 2.2, nosePaint);

    // Bunny smile (:3 mouth)
    final mouthPaint = Paint()
      ..color = const Color(0xFF7A5050)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.6
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(Offset(cx, cy + 3.5), Offset(cx, cy + 6.5), mouthPaint);
    canvas.drawArc(Rect.fromLTWH(cx - 6, cy + 4.5, 6, 5), 0.2, 2.7, false, mouthPaint);
    canvas.drawArc(Rect.fromLTWH(cx, cy + 4.5, 6, 5), 0.2, 2.7, false, mouthPaint);

    // Procedural Wearable Outfits
    _drawAccessory(canvas, cx, cy);
  }

  void _drawAccessory(Canvas canvas, double cx, double cy) {
    final accLower = accessory.toLowerCase();
    if (accLower.contains('natural') || accLower == 'none' || accLower.isEmpty) {
      return;
    }

    if (accLower.contains('ribbon') || accLower.contains('bow')) {
      // 1. Silk Ribbon Bow
      final rx = cx - 22.0;
      final ry = cy - 28.0;
      final bowPaint = Paint()..color = const Color(0xFFFF6B81);
      final knotPaint = Paint()..color = const Color(0xFFFF3366);
      canvas.drawOval(Rect.fromCenter(center: Offset(rx - 6, ry), width: 12, height: 10), bowPaint);
      canvas.drawOval(Rect.fromCenter(center: Offset(rx + 6, ry), width: 12, height: 10), bowPaint);
      canvas.drawCircle(Offset(rx, ry), 3.5, knotPaint);
    } else if (accLower.contains('crown')) {
      // 2. Royal Golden Crown
      final topY = cy - 42.0;
      final crownPaint = Paint()..color = const Color(0xFFFFD700);
      final rubyPaint = Paint()..color = const Color(0xFFFF1744);

      final path = Path()
        ..moveTo(cx - 14, topY + 6)
        ..lineTo(cx - 18, topY - 8)
        ..lineTo(cx - 7, topY - 2)
        ..lineTo(cx, topY - 12)
        ..lineTo(cx + 7, topY - 2)
        ..lineTo(cx + 18, topY - 8)
        ..lineTo(cx + 14, topY + 6)
        ..close();
      canvas.drawPath(path, crownPaint);
      canvas.drawCircle(Offset(cx, topY), 3.0, rubyPaint);
    } else if (accLower.contains('sakura') || accLower.contains('flower')) {
      // 3. Sakura Cherry Blossom
      final fx = cx - 24.0;
      final fy = cy - 26.0;
      final petalPaint = Paint()..color = const Color(0xFFFFB7C5);
      final pollenPaint = Paint()..color = const Color(0xFFFFE082);
      for (var angle in [0, 72, 144, 216, 288]) {
        final rad = angle * math.pi / 180.0;
        final px = fx + math.cos(rad) * 5.5;
        final py = fy + math.sin(rad) * 5.5;
        canvas.drawCircle(Offset(px, py), 4.5, petalPaint);
      }
      canvas.drawCircle(Offset(fx, fy), 3.0, pollenPaint);
    } else if (accLower.contains('glasses')) {
      // 4. Smart Glasses
      final glassPaint = Paint()
        ..color = const Color(0xFF2C3E50)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.2;
      canvas.drawCircle(Offset(cx - 15, cy - 3), 7.5, glassPaint);
      canvas.drawCircle(Offset(cx + 15, cy - 3), 7.5, glassPaint);
      canvas.drawLine(Offset(cx - 7.5, cy - 3), Offset(cx + 7.5, cy - 3), glassPaint);
    } else if (accLower.contains('hat')) {
      // 5. Gentleman Top Hat
      final hx = cx + 2.0;
      final hy = cy - 38.0;
      final hatPaint = Paint()..color = const Color(0xFF2B2B2B);
      final bandPaint = Paint()..color = const Color(0xFFE74C3C);
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromCenter(center: Offset(hx, hy + 5), width: 38, height: 6), const Radius.circular(3)), hatPaint);
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromCenter(center: Offset(hx, hy - 6), width: 24, height: 18), const Radius.circular(3)), hatPaint);
      canvas.drawRect(Rect.fromLTWH(hx - 12, hy - 1, 24, 4), bandPaint);
    } else if (accLower.contains('scarf')) {
      // 6. Cozy Scarf
      final scarfPaint = Paint()..color = const Color(0xFFFF7675);
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromCenter(center: Offset(cx, cy + 24), width: 48, height: 10), const Radius.circular(6)), scarfPaint);
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromLTWH(cx + 6, cy + 28, 10, 16), const Radius.circular(4)), scarfPaint);
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
