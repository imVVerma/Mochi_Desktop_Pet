import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'character_models.dart';
import 'pet_painter.dart';
import 'pet_state.dart';

void main() {
  runApp(const MochiCompanionApp());
}

class MochiCompanionApp extends StatelessWidget {
  const MochiCompanionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mochi Pet Companion',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFFFFB7B2)),
        useMaterial3: true,
        fontFamily: 'Roboto',
      ),
      home: const FloatingCompanionScreen(),
    );
  }
}

class FloatingCompanionScreen extends StatefulWidget {
  const FloatingCompanionScreen({super.key});

  @override
  State<FloatingCompanionScreen> createState() => _FloatingCompanionScreenState();
}

class _FloatingCompanionScreenState extends State<FloatingCompanionScreen>
    with SingleTickerProviderStateMixin, WidgetsBindingObserver {
  static const _overlayChannel = MethodChannel('com.mochi.companion/overlay');

  late final AnimationController _animController;
  final PetState _petState = PetState();

  Offset _position = const Offset(120, 300);
  bool _isDragging = false;
  String? _currentSpeech;
  bool _isFloatingActive = false;
  bool _isFocusing = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2400),
    )..repeat();

    _refreshStatsAndOverlayStatus();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _animController.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      _refreshStatsAndOverlayStatus();
    }
  }

  Future<void> _refreshStatsAndOverlayStatus() async {
    try {
      final bool isRunning =
          await _overlayChannel.invokeMethod('isServiceRunning') ?? false;
      final dynamic statsData =
          await _overlayChannel.invokeMethod('getPetStats');

      if (mounted) {
        setState(() {
          _isFloatingActive = isRunning;
          if (statsData is Map) {
            _petState.updateFromMap(statsData);
          }
        });
      }
    } catch (_) {}
  }

  Future<void> _toggleFloatingOverlay() async {
    try {
      final bool hasPermission =
          await _overlayChannel.invokeMethod('checkOverlayPermission') ?? false;

      if (!hasPermission) {
        // Explain permission clearly to user first
        if (mounted) {
          final shouldProceed = await showDialog<bool>(
            context: context,
            builder: (ctx) => AlertDialog(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              title: const Text('Enable Floating Mochi 🐾'),
              content: const Text(
                'Mochi needs permission to "Display over other apps" so he can float over your screen while you use WhatsApp, YouTube, and other apps.\n\nTap "Open Settings" and enable Mochi Companion.',
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx, false),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () => Navigator.pop(ctx, true),
                  child: const Text('Open Settings'),
                ),
              ],
            ),
          );

          if (shouldProceed == true) {
            await _overlayChannel.invokeMethod('requestOverlayPermission');
          }
        }
        return;
      }

      if (_isFloatingActive) {
        await _overlayChannel.invokeMethod('stopFloatingPet');
        if (mounted) {
          setState(() => _isFloatingActive = false);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Mochi tucked in for resting.')),
          );
        }
      } else {
        await _overlayChannel.invokeMethod('startFloatingPet');
        if (mounted) {
          setState(() => _isFloatingActive = true);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('🐾 Mochi is now floating over your screen! Feel free to switch to any app.'),
              backgroundColor: Color(0xFF6C5CE7),
              duration: Duration(seconds: 4),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Overlay notice: $e')),
        );
      }
    }
  }

  Future<void> _onPetTapped() async {
    try {
      final dynamic res = await _overlayChannel.invokeMethod('petMochi');
      if (res is Map && mounted) {
        final reaction = res['reaction'] as String? ?? 'Purr... ✨';
        final stats = res['stats'] as Map?;
        setState(() {
          _currentSpeech = reaction;
          if (stats != null) _petState.updateFromMap(stats);
        });
      }
    } catch (_) {
      setState(() {
        _currentSpeech = 'Purr... I love you! ✨';
      });
    }

    Future.delayed(const Duration(milliseconds: 3200), () {
      if (mounted) {
        setState(() => _currentSpeech = null);
      }
    });
  }

  Future<void> _onFeedTapped() async {
    try {
      final dynamic res = await _overlayChannel.invokeMethod('feedTreat');
      if (res is Map && mounted) {
        final reaction = res['reaction'] as String? ?? 'Yum! Crunchy strawberry! 🍓';
        final stats = res['stats'] as Map?;
        setState(() {
          _currentSpeech = reaction;
          if (stats != null) _petState.updateFromMap(stats);
        });
      }
    } catch (_) {
      setState(() {
        _currentSpeech = 'Yum! Crunchy strawberry! 🍓';
      });
    }

    Future.delayed(const Duration(milliseconds: 3200), () {
      if (mounted) {
        setState(() => _currentSpeech = null);
      }
    });
  }

  Future<void> _onFocusSessionTapped() async {
    try {
      final dynamic res = await _overlayChannel.invokeMethod('recordFocusSession', {'minutes': 25});
      if (res is Map && mounted) {
        final reaction = res['reaction'] as String? ?? 'Great 25 min focus sprint! 🎓';
        final stats = res['stats'] as Map?;
        setState(() {
          _currentSpeech = reaction;
          _isFocusing = true;
          if (stats != null) _petState.updateFromMap(stats);
        });
      }
    } catch (_) {
      setState(() {
        _currentSpeech = 'Great 25 min focus sprint! 🎓';
      });
    }

    Future.delayed(const Duration(milliseconds: 4000), () {
      if (mounted) {
        setState(() {
          _currentSpeech = null;
          _isFocusing = false;
        });
      }
    });
  }

  Future<void> _updateWardrobe({Color? color, String? accessory}) async {
    final newColor = color ?? _petState.primaryColor;
    final newAccessory = accessory ?? _petState.accessory;

    setState(() {
      _petState.primaryColor = newColor;
      _petState.accessory = newAccessory;
    });

    try {
      final colorHex = PetState.colorToHex(newColor);
      final dynamic updated = await _overlayChannel.invokeMethod('setAppearance', {
        'baseColor': colorHex,
        'accessory': newAccessory,
      });
      if (updated is Map && mounted) {
        setState(() {
          _petState.updateFromMap(updated);
        });
      }
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: const Color(0xFFF7F5F0),
      body: Stack(
        children: [
          // Sanctuary Dashboard
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _petState.name,
                            style: const TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF2C3E50),
                            ),
                          ),
                          Text(
                            '${PetCharacter.findBySpecies(_petState.species).emoji} Floating Pocket Companion',
                            style: const TextStyle(color: Colors.black54, fontSize: 13),
                          ),
                        ],
                      ),
                      Row(
                        children: [
                          IconButton.filledTonal(
                            onPressed: _showCharacterSelectorSheet,
                            icon: const Text('🐾', style: TextStyle(fontSize: 16)),
                            tooltip: 'Choose Pet Companion',
                          ),
                          const SizedBox(width: 8),
                          IconButton.filledTonal(
                            onPressed: _showWardrobeSheet,
                            icon: const Icon(Icons.palette_outlined),
                            tooltip: 'Wardrobe & Fur Color',
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _buildStatCard(),
                  const Spacer(),
                  // Prominent Floating Overlay Toggle Button
                  Container(
                    width: double.infinity,
                    margin: const EdgeInsets.only(bottom: 12),
                    child: ElevatedButton.icon(
                      onPressed: _toggleFloatingOverlay,
                      icon: Icon(_isFloatingActive
                          ? Icons.visibility_off
                          : Icons.open_in_new),
                      label: Text(
                        _isFloatingActive
                            ? 'Dismiss Floating Mochi'
                            : '✨ Summon Floating Mochi',
                        style: const TextStyle(
                            fontSize: 15, fontWeight: FontWeight.bold),
                      ),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        backgroundColor: _isFloatingActive
                            ? Colors.blueGrey.shade700
                            : const Color(0xFF6C5CE7),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16)),
                        elevation: 4,
                      ),
                    ),
                  ),
                  _buildActionBar(),
                ],
              ),
            ),
          ),

          // In-App Interactive Canvas Avatar
          Positioned(
            left: _position.dx,
            top: _position.dy,
            child: GestureDetector(
              onPanStart: (_) => setState(() => _isDragging = true),
              onPanUpdate: (details) {
                setState(() {
                  _position += details.delta;
                });
              },
              onPanEnd: (_) {
                setState(() {
                  _isDragging = false;
                  final snapLeft = _position.dx < size.width / 2;
                  _position = Offset(
                    snapLeft ? 16 : size.width - 150 - 16,
                    _position.dy.clamp(60, size.height - 240),
                  );
                });
              },
              onTap: _onPetTapped,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (_currentSpeech != null)
                    ConstrainedBox(
                      constraints: BoxConstraints(maxWidth: math.min(size.width - 48, 220)),
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 8),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 14, vertical: 8),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: const [
                            BoxShadow(
                              color: Colors.black12,
                              blurRadius: 8,
                              offset: Offset(0, 3),
                            ),
                          ],
                        ),
                        child: Text(
                          _currentSpeech!,
                          textAlign: TextAlign.center,
                          softWrap: true,
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 13,
                            color: Color(0xFF333333),
                          ),
                        ),
                      ),
                    ),
                  AnimatedBuilder(
                    animation: _animController,
                    builder: (context, child) {
                      return CustomPaint(
                        size: const Size(150, 150),
                        painter: PetPainter(
                          species: _petState.species,
                          phase: _animController.value,
                          isDragging: _isDragging,
                          bodyColor: _petState.primaryColor,
                          accessory: _petState.accessory,
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: const [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 10,
            offset: Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          _buildStatRow('💖 Happiness', _petState.happiness, Colors.pinkAccent),
          const SizedBox(height: 10),
          _buildStatRow('⚡ Energy', _petState.energy, Colors.amber),
          const SizedBox(height: 10),
          _buildStatRow('🎓 Focus Today', '${_petState.focusMinutes} min',
              Colors.deepPurpleAccent),
        ],
      ),
    );
  }

  Widget _buildStatRow(String label, dynamic value, Color barColor) {
    final double fraction =
        (value is int) ? (value / 100.0).clamp(0.0, 1.0) : 1.0;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
            Text(value is int ? '$value%' : '$value',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
          ],
        ),
        const SizedBox(height: 5),
        LinearProgressIndicator(
          value: fraction,
          backgroundColor: Colors.grey.shade200,
          color: barColor,
          borderRadius: BorderRadius.circular(8),
          minHeight: 7,
        ),
      ],
    );
  }

  Widget _buildActionBar() {
    return Row(
      children: [
        Expanded(
          child: ElevatedButton.icon(
            onPressed: _onPetTapped,
            icon: const Icon(Icons.favorite, size: 18),
            label: const FittedBox(fit: BoxFit.scaleDown, child: Text('Pet')),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 6),
              backgroundColor: const Color(0xFFFF9AA2),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            ),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: ElevatedButton.icon(
            onPressed: _onFeedTapped,
            icon: const Icon(Icons.restaurant, size: 18),
            label: const FittedBox(fit: BoxFit.scaleDown, child: Text('Treat 🍓')),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 6),
              backgroundColor: const Color(0xFFFFB7B2),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            ),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: ElevatedButton.icon(
            onPressed: _onFocusSessionTapped,
            icon: const Icon(Icons.timer_outlined, size: 18),
            label: const FittedBox(fit: BoxFit.scaleDown, child: Text('Focus ⏱️')),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 6),
              backgroundColor: const Color(0xFFB39DDB),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _switchCharacter(PetCharacter char) async {
    setState(() {
      _petState.species = char.species;
      _petState.name = char.name;
      _petState.primaryColor = char.defaultColor;
    });

    try {
      final colorHex = PetState.colorToHex(char.defaultColor);
      final dynamic updated = await _overlayChannel.invokeMethod('setCharacter', {
        'species': char.species,
        'name': char.name,
        'baseColor': colorHex,
        'accessory': _petState.accessory,
      });
      if (updated is Map && mounted) {
        setState(() => _petState.updateFromMap(updated));
      }
    } catch (_) {}

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('🐾 Switched companion to ${char.name} ${char.emoji}! Full body in app, face badge in overlay.'),
          backgroundColor: const Color(0xFF6C5CE7),
          duration: const Duration(seconds: 3),
        ),
      );
    }
  }

  void _showCharacterSelectorSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      '🐾 Choose Companion',
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFF6C5CE7).withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Text(
                        'App: Full Body • Overlay: Face',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF6C5CE7),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                const Text(
                  'Choose your pet companion. The app displays their full animated body; the floating screen overlay shows a compact, unobtrusive face badge.',
                  style: TextStyle(fontSize: 12, color: Colors.black54),
                ),
                const SizedBox(height: 16),
                ...PetCharacter.presetCharacters.map((char) {
                  final isSelected = _petState.species.toLowerCase() == char.species.toLowerCase();
                  return Container(
                    margin: const EdgeInsets.only(bottom: 10),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? const Color(0xFF6C5CE7).withValues(alpha: 0.08)
                          : Colors.white,
                      border: Border.all(
                        color: isSelected
                            ? const Color(0xFF6C5CE7)
                            : Colors.grey.shade300,
                        width: isSelected ? 2 : 1,
                      ),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor: char.defaultColor,
                        child: Text(char.emoji, style: const TextStyle(fontSize: 20)),
                      ),
                      title: Row(
                        children: [
                          Text(
                            '${char.name} (${char.species})',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          if (isSelected) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: const Color(0xFF6C5CE7),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Text(
                                'Active',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                      subtitle: Text(
                        char.description,
                        style: const TextStyle(fontSize: 12),
                      ),
                      onTap: () {
                        _switchCharacter(char);
                        Navigator.pop(context);
                      },
                    ),
                  );
                }),
                const SizedBox(height: 12),
                // AI Character Forge Extensibility Card
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        const Color(0xFF6C5CE7).withValues(alpha: 0.10),
                        const Color(0xFFFF9AA2).withValues(alpha: 0.10),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFF6C5CE7).withValues(alpha: 0.2)),
                  ),
                  child: const Row(
                    children: [
                      Text('✨', style: TextStyle(fontSize: 24)),
                      SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'AI Character Forge (Next Phase)',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF2C3E50),
                              ),
                            ),
                            SizedBox(height: 2),
                            Text(
                              'Upload any photo, clipart, or drawing. Our vision LLM will convert it into an animated full-body sprite with floating face badge!',
                              style: TextStyle(fontSize: 11, color: Colors.black87),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showWardrobeSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      '🐾 Companion Species',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    TextButton(
                      onPressed: () {
                        Navigator.pop(context);
                        _showCharacterSelectorSheet();
                      },
                      child: const Text('View All'),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: PetCharacter.presetCharacters.map((c) {
                    final isSel = _petState.species.toLowerCase() == c.species.toLowerCase();
                    return ChoiceChip(
                      avatar: Text(c.emoji),
                      label: Text(c.name),
                      selected: isSel,
                      onSelected: (_) {
                        _switchCharacter(c);
                        Navigator.pop(context);
                      },
                    );
                  }).toList(),
                ),
                const SizedBox(height: 20),
                const Text(
                  '🎨 Fur Color & Palettes',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 14),
                Wrap(
                  spacing: 10,
                  runSpacing: 8,
                  children: [
                    _colorPill('Vanilla Cream', const Color(0xFFFFF8E7)),
                    _colorPill('Strawberry Milk', const Color(0xFFFFD1DC)),
                    _colorPill('Cloud White', const Color(0xFFFFFFFF)),
                    _colorPill('Golden Fur', const Color(0xFFF6B93B)),
                    _colorPill('Matcha Cream', const Color(0xFFE8F5E9)),
                    _colorPill('Lilac Mist', const Color(0xFFEDE7F6)),
                  ],
                ),
                const SizedBox(height: 20),
                const Text(
                  '👗 Outfits & Accessories',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 14),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _accessoryChip('🎀 Silk Ribbon'),
                    _accessoryChip('👑 Royal Crown'),
                    _accessoryChip('🌸 Sakura Flower'),
                    _accessoryChip('👓 Smart Glasses'),
                    _accessoryChip('🎩 Top Hat'),
                    _accessoryChip('🧣 Cozy Scarf'),
                    _accessoryChip('🐾 Natural'),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _colorPill(String name, Color color) {
    return ActionChip(
      avatar: CircleAvatar(backgroundColor: color),
      label: Text(name),
      onPressed: () {
        _updateWardrobe(color: color);
        Navigator.pop(context);
      },
    );
  }

  Widget _accessoryChip(String acc) {
    final isSelected = _petState.accessory == acc;
    return ChoiceChip(
      label: Text(acc),
      selected: isSelected,
      onSelected: (_) {
        _updateWardrobe(accessory: acc);
        Navigator.pop(context);
      },
    );
  }
}
