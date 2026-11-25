import 'package:flutter/material.dart';

/**
 * PetCharacter & Sprite Specification:
 * Modular specification inspired by the awesome-codex-pet open-source registry.
 * Encapsulates character metadata, procedural and spritesheet render modes,
 * and crops for AI image/clipart-to-sprite conversions.
 */
enum RenderMode { procedural, spriteSheet }

class PetCharacter {
  final String id;
  final String name;
  final String emoji;
  final String species;
  final String description;
  final Color defaultColor;
  final RenderMode renderMode;
  final String? spritesheetPath;
  final Rect? headCropRatio; // [left, top, width, height] in normalized 0.0-1.0 space

  const PetCharacter({
    required this.id,
    required this.name,
    required this.emoji,
    required this.species,
    required this.description,
    required this.defaultColor,
    this.renderMode = RenderMode.procedural,
    this.spritesheetPath,
    this.headCropRatio,
  });

  static const List<PetCharacter> presetCharacters = [
    PetCharacter(
      id: 'mochi_bunny',
      name: 'Mochi',
      emoji: '🐰',
      species: 'bunny',
      description: 'Gentle floppy-eared bunny who loves fresh strawberries and quiet cuddles.',
      defaultColor: Color(0xFFFFF8E7), // Vanilla Cream
      headCropRatio: Rect.fromLTWH(0.15, 0.0, 0.70, 0.60),
    ),
    PetCharacter(
      id: 'luna_cat',
      name: 'Luna',
      emoji: '🐱',
      species: 'cat',
      description: 'Playful neko kitty with perky triangular ears, whiskers, and a curious tail.',
      defaultColor: Color(0xFFF5F6FA), // Pearl White
      headCropRatio: Rect.fromLTWH(0.15, 0.0, 0.70, 0.58),
    ),
    PetCharacter(
      id: 'kiko_shiba',
      name: 'Kiko',
      emoji: '🐶',
      species: 'dog',
      description: 'Energetic loyal Shiba Inu with white eyebrow dots and a happy wagging tail.',
      defaultColor: Color(0xFFF6B93B), // Golden Shiba
      headCropRatio: Rect.fromLTWH(0.15, 0.0, 0.70, 0.60),
    ),
    PetCharacter(
      id: 'bao_panda',
      name: 'Bao',
      emoji: '🐼',
      species: 'panda',
      description: 'Chubby peaceful panda bear who loves bamboo snacks and afternoon loafing.',
      defaultColor: Color(0xFFFFFFFF), // Pure Cloud
      headCropRatio: Rect.fromLTWH(0.15, 0.0, 0.70, 0.60),
    ),
  ];

  static PetCharacter findBySpecies(String species) {
    return presetCharacters.firstWhere(
      (c) => c.species.toLowerCase() == species.toLowerCase(),
      orElse: () => presetCharacters.first,
    );
  }
}
