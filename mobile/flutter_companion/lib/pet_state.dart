import 'package:flutter/material.dart';

/**
 * PetState:
 * In-memory representation of Mochi's current status and appearance.
 * Native PetStatsManager is the single source of truth across reboots.
 */
class PetState {
  String name = 'Mochi';
  Color primaryColor = const Color(0xFFFFF8E7); // Vanilla Cream
  String accessory = '🐾 Natural';
  int happiness = 92;
  int energy = 95;
  int focusMinutes = 0;

  void updateFromMap(Map<dynamic, dynamic> map) {
    if (map.containsKey('name')) name = map['name'] as String;
    if (map.containsKey('happiness')) happiness = (map['happiness'] as num).toInt();
    if (map.containsKey('energy')) energy = (map['energy'] as num).toInt();
    if (map.containsKey('focusMinutes')) focusMinutes = (map['focusMinutes'] as num).toInt();
    if (map.containsKey('accessory')) accessory = map['accessory'] as String;
    if (map.containsKey('baseColor')) {
      final hex = map['baseColor'] as String;
      primaryColor = hexToColor(hex);
    }
  }

  static Color hexToColor(String hex) {
    final cleanHex = hex.replaceAll('#', '').trim();
    if (cleanHex.length == 6) {
      return Color(int.parse('FF$cleanHex', radix: 16));
    } else if (cleanHex.length == 8) {
      return Color(int.parse(cleanHex, radix: 16));
    }
    return const Color(0xFFFFF8E7);
  }

  static String colorToHex(Color color) {
    return '#${color.value.toRadixString(16).padLeft(8, '0').substring(2).toUpperCase()}';
  }
}
