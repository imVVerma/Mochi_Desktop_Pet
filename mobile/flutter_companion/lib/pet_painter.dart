import 'dart:math' as math;
import 'package:flutter/material.dart';

/**
 * PetPainter:
 * Full-body CustomPainter rendering the active pet companion in the sanctuary app:
 * - Full character anatomy: head, ears, chubby body torso, front paws, animated tail, and accessories.
 * - Dynamic breathing cycle, natural blinking, and subtle tail/ear momentum physics.
 * - Procedural rendering for all 4 species (Bunny, Cat, Dog, Panda).
 * - Procedural rendering of all 6 wardrobe accessories (Crown, Ribbon, Sakura, Glasses, Top Hat, Scarf).
 */
class PetPainter extends CustomPainter {
  final String species;
  final double phase; // 0.0 to 1.0
  final bool isDragging;
  final Color bodyColor;
  final String accessory;

  PetPainter({
    required this.species,
    required this.phase,
    required this.isDragging,
    required this.bodyColor,
    required this.accessory,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2 + 6;

    final breath = math.sin(phase * 2 * math.pi) * 2.5;
    final earAngle = math.sin(phase * 2 * math.pi) * 0.08;
    final tailWag = math.sin(phase * 4 * math.pi) * 0.20;

    // 1. Soft Ground Contact Shadow
    final shadowPaint = Paint()..color = const Color(0x28000000);
    canvas.drawOval(
      Rect.fromCenter(center: Offset(cx, cy + 50), width: 84, height: 16),
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

    final darkVestPaint = Paint()
      ..color = const Color(0xFF2D3436)
      ..style = PaintingStyle.fill;

    // 2. Animated Tail (drawn behind torso)
    _drawTail(canvas, cx, cy, tailWag, bodyPaint, darkVestPaint);

    // 3. Chubby Torso / Body (drawn behind head)
    final isPanda = species.toLowerCase() == 'panda';
    final torsoPaint = isPanda ? darkVestPaint : bodyPaint;
    final torsoRect = Rect.fromCenter(
      center: Offset(cx, cy + 22 + (breath * 0.2)),
      width: 66,
      height: 52,
    );
    canvas.drawRRect(
      RRect.fromRectAndRadius(torsoRect, const Radius.circular(26)),
      torsoPaint,
    );

    // Belly patch
    final bellyPaint = Paint()
      ..color = isPanda
          ? Colors.white.withValues(alpha: 0.95)
          : Colors.white.withValues(alpha: 0.35);
    canvas.drawOval(
      Rect.fromCenter(center: Offset(cx, cy + 24), width: 36, height: 32),
      bellyPaint,
    );

    // 4. Front Resting Paws
    final pawPaint = isPanda ? darkVestPaint : bodyPaint;
    canvas.drawOval(
      Rect.fromCenter(center: Offset(cx - 18, cy + 44), width: 18, height: 13),
      pawPaint,
    );
    canvas.drawOval(
      Rect.fromCenter(center: Offset(cx + 18, cy + 44), width: 18, height: 13),
      pawPaint,
    );

    // 5. Character Ears (drawn behind head)
    _drawEars(canvas, cx, cy - 8, earAngle, bodyPaint, innerEarPaint, darkVestPaint);

    // 6. Chubby Head
    final headRadius = 37.0 + (breath * 0.3);
    final headCenter = Offset(cx, cy - 8);
    canvas.drawCircle(headCenter, headRadius, bodyPaint);

    // Character-specific markings (Panda eye patches, Shiba eyebrows)
    _drawHeadMarkings(canvas, cx, cy - 8, darkVestPaint);

    // 7. Blushing Cheeks
    canvas.drawCircle(Offset(cx - 23, cy - 2), 7.5, blushPaint);
    canvas.drawCircle(Offset(cx + 23, cy - 2), 7.5, blushPaint);

    // Cat Whiskers
    if (species.toLowerCase() == 'cat') {
      final whiskerPaint = Paint()
        ..color = const Color(0xFF636E72)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.8
        ..strokeCap = StrokeCap.round;
      // Left whiskers
      canvas.drawLine(Offset(cx - 22, cy - 6), Offset(cx - 38, cy - 8), whiskerPaint);
      canvas.drawLine(Offset(cx - 22, cy - 2), Offset(cx - 40, cy - 2), whiskerPaint);
      canvas.drawLine(Offset(cx - 22, cy + 2), Offset(cx - 38, cy + 4), whiskerPaint);
      // Right whiskers
      canvas.drawLine(Offset(cx + 22, cy - 6), Offset(cx + 38, cy - 8), whiskerPaint);
      canvas.drawLine(Offset(cx + 22, cy - 2), Offset(cx + 40, cy - 2), whiskerPaint);
      canvas.drawLine(Offset(cx + 22, cy + 2), Offset(cx + 38, cy + 4), whiskerPaint);
    }

    // 8. Eyes & Blinking Logic
    final isBlinking = phase > 0.93 && phase < 0.98;

    if (isBlinking) {
      final blinkPaint = Paint()
        ..color = const Color(0xFF2C2C2C)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.5
        ..strokeCap = StrokeCap.round;
      canvas.drawLine(Offset(cx - 19, cy - 12), Offset(cx - 9, cy - 12), blinkPaint);
      canvas.drawLine(Offset(cx + 9, cy - 12), Offset(cx + 19, cy - 12), blinkPaint);
    } else {
      // Sparkle Eyes
      canvas.drawCircle(Offset(cx - 14, cy - 12), 4.8, eyePaint);
      canvas.drawCircle(Offset(cx - 12.5, cy - 13.5), 1.8, sparklePaint);
      canvas.drawCircle(Offset(cx - 15.5, cy - 10.5), 1.0, sparklePaint);

      canvas.drawCircle(Offset(cx + 14, cy - 12), 4.8, eyePaint);
      canvas.drawCircle(Offset(cx + 15.5, cy - 13.5), 1.8, sparklePaint);
      canvas.drawCircle(Offset(cx + 12.5, cy - 10.5), 1.0, sparklePaint);
    }

    // 9. Character Nose & Mouth
    _drawMouthAndNose(canvas, cx, cy - 8);

    // 10. Procedural Wearable Outfits
    _drawAccessory(canvas, cx, cy - 8);
  }

  void _drawTail(Canvas canvas, double cx, double cy, double wag, Paint bodyPaint, Paint darkPaint) {
    final sp = species.toLowerCase();
    if (sp == 'bunny') {
      // Round cotton-ball tail
      canvas.drawCircle(Offset(cx + 30, cy + 28), 10, bodyPaint);
      canvas.drawCircle(Offset(cx + 30, cy + 28), 7, Paint()..color = Colors.white.withValues(alpha: 0.6));
    } else if (sp == 'cat') {
      // Long curled tail swaying
      canvas.save();
      canvas.translate(cx + 28, cy + 28);
      canvas.rotate(wag);
      final tailPath = Path()
        ..moveTo(0, 0)
        ..quadraticBezierTo(18, -10, 16, -28)
        ..quadraticBezierTo(14, -36, 6, -34);
      final catTailPaint = Paint()
        ..color = bodyPaint.color
        ..style = PaintingStyle.stroke
        ..strokeWidth = 9
        ..strokeCap = StrokeCap.round;
      canvas.drawPath(tailPath, catTailPaint);
      canvas.restore();
    } else if (sp == 'dog') {
      // Wagging ringlet tail
      canvas.save();
      canvas.translate(cx + 26, cy + 24);
      canvas.rotate(wag * 1.5);
      final dogTailPaint = Paint()
        ..color = bodyPaint.color
        ..style = PaintingStyle.stroke
        ..strokeWidth = 9
        ..strokeCap = StrokeCap.round;
      final dogTailPath = Path()
        ..moveTo(0, 0)
        ..quadraticBezierTo(16, -8, 12, -22)
        ..quadraticBezierTo(8, -28, 0, -22);
      canvas.drawPath(dogTailPath, dogTailPaint);
      canvas.restore();
    } else if (sp == 'panda') {
      // Dark stubby bear tail
      canvas.drawCircle(Offset(cx + 30, cy + 30), 8, darkPaint);
    }
  }

  void _drawEars(
    Canvas canvas,
    double cx,
    double cy,
    double angle,
    Paint bodyPaint,
    Paint innerPaint,
    Paint darkPaint,
  ) {
    final sp = species.toLowerCase();
    if (sp == 'cat') {
      // Pointy triangular cat ears
      final leftEar = Path()
        ..moveTo(cx - 32, cy - 10)
        ..lineTo(cx - 26, cy - 44)
        ..lineTo(cx - 8, cy - 26)
        ..close();
      canvas.drawPath(leftEar, bodyPaint);
      final leftInner = Path()
        ..moveTo(cx - 28, cy - 14)
        ..lineTo(cx - 24, cy - 38)
        ..lineTo(cx - 12, cy - 24)
        ..close();
      canvas.drawPath(leftInner, innerPaint);

      final rightEar = Path()
        ..moveTo(cx + 32, cy - 10)
        ..lineTo(cx + 26, cy - 44)
        ..lineTo(cx + 8, cy - 26)
        ..close();
      canvas.drawPath(rightEar, bodyPaint);
      final rightInner = Path()
        ..moveTo(cx + 28, cy - 14)
        ..lineTo(cx + 24, cy - 38)
        ..lineTo(cx + 12, cy - 24)
        ..close();
      canvas.drawPath(rightInner, innerPaint);
    } else if (sp == 'dog') {
      // Perky Shiba ears
      final leftEar = Path()
        ..moveTo(cx - 30, cy - 8)
        ..lineTo(cx - 24, cy - 42)
        ..lineTo(cx - 6, cy - 24)
        ..close();
      canvas.drawPath(leftEar, bodyPaint);
      final leftInner = Path()
        ..moveTo(cx - 26, cy - 12)
        ..lineTo(cx - 22, cy - 36)
        ..lineTo(cx - 10, cy - 22)
        ..close();
      canvas.drawPath(leftInner, innerPaint);

      final rightEar = Path()
        ..moveTo(cx + 30, cy - 8)
        ..lineTo(cx + 26, cy - 42)
        ..lineTo(cx + 6, cy - 24)
        ..close();
      canvas.drawPath(rightEar, bodyPaint);
      final rightInner = Path()
        ..moveTo(cx + 26, cy - 12)
        ..lineTo(cx + 22, cy - 36)
        ..lineTo(cx + 10, cy - 22)
        ..close();
      canvas.drawPath(rightInner, innerPaint);
    } else if (sp == 'panda') {
      // Round black bear ears
      canvas.drawCircle(Offset(cx - 26, cy - 30), 13, darkPaint);
      canvas.drawCircle(Offset(cx + 26, cy - 30), 13, darkPaint);
    } else {
      // Classic floppy bunny ears
      _drawFloppyEar(canvas, cx - 24, cy - 18, -0.45 + angle, bodyPaint, innerPaint);
      _drawFloppyEar(canvas, cx + 24, cy - 18, 0.45 - angle, bodyPaint, innerPaint);
    }
  }

  void _drawHeadMarkings(Canvas canvas, double cx, double cy, Paint darkPaint) {
    final sp = species.toLowerCase();
    if (sp == 'panda') {
      // Black eye patches
      canvas.save();
      canvas.translate(cx - 14, cy - 12);
      canvas.rotate(-0.25);
      canvas.drawOval(Rect.fromCenter(center: Offset.zero, width: 17, height: 13), darkPaint);
      canvas.restore();

      canvas.save();
      canvas.translate(cx + 14, cy - 12);
      canvas.rotate(0.25);
      canvas.drawOval(Rect.fromCenter(center: Offset.zero, width: 17, height: 13), darkPaint);
      canvas.restore();
    } else if (sp == 'dog') {
      // White eyebrow dots
      final browPaint = Paint()..color = Colors.white.withValues(alpha: 0.9);
      canvas.drawCircle(Offset(cx - 14, cy - 22), 3.5, browPaint);
      canvas.drawCircle(Offset(cx + 14, cy - 22), 3.5, browPaint);
    }
  }

  void _drawMouthAndNose(Canvas canvas, double cx, double cy) {
    final sp = species.toLowerCase();
    final mouthPaint = Paint()
      ..color = const Color(0xFF7A5050)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.6
      ..strokeCap = StrokeCap.round;

    if (sp == 'cat') {
      // Pink triangle nose
      final nosePaint = Paint()..color = const Color(0xFFFF8B94);
      final nosePath = Path()
        ..moveTo(cx - 3, cy - 2)
        ..lineTo(cx + 3, cy - 2)
        ..lineTo(cx, cy + 1.5)
        ..close();
      canvas.drawPath(nosePath, nosePaint);
      // :3 Cat smile
      canvas.drawArc(Rect.fromLTWH(cx - 6, cy + 0.5, 6, 5), 0.2, 2.7, false, mouthPaint);
      canvas.drawArc(Rect.fromLTWH(cx, cy + 0.5, 6, 5), 0.2, 2.7, false, mouthPaint);
    } else if (sp == 'dog') {
      // Black button nose
      final dogNosePaint = Paint()..color = const Color(0xFF222222);
      canvas.drawOval(Rect.fromCenter(center: Offset(cx, cy - 1), width: 7, height: 5), dogNosePaint);
      // Open smile with tongue blep
      canvas.drawLine(Offset(cx, cy + 1.5), Offset(cx, cy + 4.5), mouthPaint);
      canvas.drawArc(Rect.fromCenter(center: Offset(cx, cy + 4), width: 12, height: 8), 0.2, 2.7, false, mouthPaint);
      final tonguePaint = Paint()..color = const Color(0xFFFF6B81);
      canvas.drawRRect(
        RRect.fromRectAndRadius(Rect.fromCenter(center: Offset(cx, cy + 8), width: 6, height: 7), const Radius.circular(3)),
        tonguePaint,
      );
    } else if (sp == 'panda') {
      // Rounded bear nose
      final pandaNosePaint = Paint()..color = const Color(0xFF2D3436);
      canvas.drawOval(Rect.fromCenter(center: Offset(cx, cy - 1), width: 8, height: 5), pandaNosePaint);
      canvas.drawLine(Offset(cx, cy + 1.5), Offset(cx, cy + 5), mouthPaint);
      canvas.drawArc(Rect.fromLTWH(cx - 6, cy + 3.5, 6, 5), 0.2, 2.7, false, mouthPaint);
      canvas.drawArc(Rect.fromLTWH(cx, cy + 3.5, 6, 5), 0.2, 2.7, false, mouthPaint);
    } else {
      // Classic Bunny Nose
      final nosePaint = Paint()
        ..color = const Color(0xFFE57373)
        ..style = PaintingStyle.fill;
      canvas.drawCircle(Offset(cx, cy - 2), 2.2, nosePaint);
      canvas.drawLine(Offset(cx, cy - 2), Offset(cx, cy + 1), mouthPaint);
      canvas.drawArc(Rect.fromLTWH(cx - 5.5, cy, 5.5, 4.5), 0.2, 2.7, false, mouthPaint);
      canvas.drawArc(Rect.fromLTWH(cx, cy, 5.5, 4.5), 0.2, 2.7, false, mouthPaint);
    }
  }

  void _drawAccessory(Canvas canvas, double cx, double cy) {
    final accLower = accessory.toLowerCase();
    if (accLower.contains('natural') || accLower == 'none' || accLower.isEmpty) {
      return;
    }

    if (accLower.contains('ribbon') || accLower.contains('bow')) {
      final rx = cx - 20.0;
      final ry = cy - 26.0;
      final bowPaint = Paint()..color = const Color(0xFFFF6B81);
      final knotPaint = Paint()..color = const Color(0xFFFF3366);
      canvas.drawOval(Rect.fromCenter(center: Offset(rx - 5, ry), width: 11, height: 9), bowPaint);
      canvas.drawOval(Rect.fromCenter(center: Offset(rx + 5, ry), width: 11, height: 9), bowPaint);
      canvas.drawCircle(Offset(rx, ry), 3.0, knotPaint);
    } else if (accLower.contains('crown')) {
      final topY = cy - 38.0;
      final crownPaint = Paint()..color = const Color(0xFFFFD700);
      final rubyPaint = Paint()..color = const Color(0xFFFF1744);

      final path = Path()
        ..moveTo(cx - 13, topY + 5)
        ..lineTo(cx - 17, topY - 7)
        ..lineTo(cx - 6, topY - 2)
        ..lineTo(cx, topY - 11)
        ..lineTo(cx + 6, topY - 2)
        ..lineTo(cx + 17, topY - 7)
        ..lineTo(cx + 13, topY + 5)
        ..close();
      canvas.drawPath(path, crownPaint);
      canvas.drawCircle(Offset(cx, topY - 1), 2.8, rubyPaint);
    } else if (accLower.contains('sakura') || accLower.contains('flower')) {
      final fx = cx - 22.0;
      final fy = cy - 24.0;
      final petalPaint = Paint()..color = const Color(0xFFFFB7C5);
      final pollenPaint = Paint()..color = const Color(0xFFFFE082);
      for (var angle in [0, 72, 144, 216, 288]) {
        final rad = angle * math.pi / 180.0;
        final px = fx + math.cos(rad) * 5.0;
        final py = fy + math.sin(rad) * 5.0;
        canvas.drawCircle(Offset(px, py), 4.0, petalPaint);
      }
      canvas.drawCircle(Offset(fx, fy), 2.8, pollenPaint);
    } else if (accLower.contains('glasses')) {
      final glassPaint = Paint()
        ..color = const Color(0xFF2C3E50)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.2;
      canvas.drawCircle(Offset(cx - 14, cy - 12), 7.0, glassPaint);
      canvas.drawCircle(Offset(cx + 14, cy - 12), 7.0, glassPaint);
      canvas.drawLine(Offset(cx - 7, cy - 12), Offset(cx + 7, cy - 12), glassPaint);
    } else if (accLower.contains('hat')) {
      final hx = cx + 2.0;
      final hy = cy - 36.0;
      final hatPaint = Paint()..color = const Color(0xFF2B2B2B);
      final bandPaint = Paint()..color = const Color(0xFFE74C3C);
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromCenter(center: Offset(hx, hy + 5), width: 34, height: 5), const Radius.circular(2.5)), hatPaint);
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromCenter(center: Offset(hx, hy - 5), width: 22, height: 16), const Radius.circular(2.5)), hatPaint);
      canvas.drawRect(Rect.fromLTWH(hx - 11, hy - 1, 22, 3.5), bandPaint);
    } else if (accLower.contains('scarf')) {
      final scarfPaint = Paint()..color = const Color(0xFFFF7675);
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromCenter(center: Offset(cx, cy + 18), width: 44, height: 9), const Radius.circular(5)), scarfPaint);
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromLTWH(cx + 6, cy + 22, 9, 14), const Radius.circular(3.5)), scarfPaint);
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
      const Rect.fromLTWH(-10, 0, 20, 46),
      const Radius.circular(10),
    );
    canvas.drawRRect(outerRRect, outerPaint);

    final innerRRect = RRect.fromRectAndRadius(
      const Rect.fromLTWH(-6, 5, 12, 36),
      const Radius.circular(6),
    );
    canvas.drawRRect(innerRRect, innerPaint);

    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant PetPainter oldDelegate) {
    return oldDelegate.phase != phase ||
        oldDelegate.isDragging != isDragging ||
        oldDelegate.bodyColor != bodyColor ||
        oldDelegate.accessory != accessory ||
        oldDelegate.species != species;
  }
}

/**
 * Backward compatibility alias for tests and existing code.
 */
class BunnyPainter extends PetPainter {
  BunnyPainter({
    required super.phase,
    required super.isDragging,
    required super.bodyColor,
    required super.accessory,
  }) : super(species: 'bunny');
}
