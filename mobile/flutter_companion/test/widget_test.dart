import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mochi_companion/character_models.dart';
import 'package:mochi_companion/main.dart';
import 'package:mochi_companion/pet_painter.dart';

void main() {
  testWidgets('Mochi Companion App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MochiCompanionApp());
    expect(find.byType(FloatingCompanionScreen), findsOneWidget);
  });

  test('Preset characters verify all species and default assets', () {
    expect(PetCharacter.presetCharacters.length, 4);

    final bunny = PetCharacter.findBySpecies('bunny');
    expect(bunny.name, 'Mochi');
    expect(bunny.emoji, '🐰');

    final cat = PetCharacter.findBySpecies('cat');
    expect(cat.name, 'Luna');
    expect(cat.emoji, '🐱');

    final dog = PetCharacter.findBySpecies('dog');
    expect(dog.name, 'Kiko');
    expect(dog.emoji, '🐶');

    final panda = PetCharacter.findBySpecies('panda');
    expect(panda.name, 'Bao');
    expect(panda.emoji, '🐼');
  });

  testWidgets('PetPainter renders without errors for all 4 species', (WidgetTester tester) async {
    for (final char in PetCharacter.presetCharacters) {
      await tester.pumpWidget(
        Directionality(
          textDirection: TextDirection.ltr,
          child: CustomPaint(
            size: const Size(150, 150),
            painter: PetPainter(
              species: char.species,
              phase: 0.25,
              isDragging: false,
              bodyColor: char.defaultColor,
              accessory: '👑 Royal Crown',
            ),
          ),
        ),
      );
      expect(find.byType(CustomPaint), findsOneWidget);
    }
  });
}
