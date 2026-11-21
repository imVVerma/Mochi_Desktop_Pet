import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mochi_companion/main.dart';

void main() {
  testWidgets('Mochi Companion App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MochiCompanionApp());
    expect(find.byType(FloatingCompanionScreen), findsOneWidget);
  });
}
