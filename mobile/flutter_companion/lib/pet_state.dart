import 'package:flutter/material.dart';

class PetState {
  String name = 'Mochi';
  Color primaryColor = const Color(0xFFFFF8E7); // Vanilla Cream
  String accessory = '🎀 Red Ribbon';
  int happiness = 92;
  int energy = 88;
  int focusMinutes = 45;

  String petMochi() {
    happiness = (happiness + 10).clamp(0, 100);
    energy = (energy - 2).clamp(10, 100);
    return 'Purr... I love spending time with you! ✨';
  }

  String feedTreat() {
    energy = (energy + 15).clamp(0, 100);
    happiness = (happiness + 8).clamp(0, 100);
    return 'Yum! Crunchy strawberry treat! 🍓';
  }

  void addFocusMinutes(int mins) {
    focusMinutes += mins;
    happiness = (happiness + (mins ~/ 5)).clamp(0, 100);
  }
}
