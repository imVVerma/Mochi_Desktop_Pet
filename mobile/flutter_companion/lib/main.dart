import 'package:flutter/material.dart';
import 'bunny_painter.dart';
import 'pet_state.dart';

void main() {
  runApp(const MochiCompanionApp());
}

class MochiCompanionApp extends StatelessWidget {
  const MochiCompanionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mochi Pet',
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
    with SingleTickerProviderStateMixin {
  late final AnimationController _animController;
  final PetState _petState = PetState();

  Offset _position = const Offset(120, 300);
  bool _isDragging = false;
  String? _currentSpeech;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2400),
    )..repeat();
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  void _onPetTapped() {
    setState(() {
      _currentSpeech = _petState.petMochi();
    });
    Future.delayed(const Duration(milliseconds: 3000), () {
      if (mounted) {
        setState(() => _currentSpeech = null);
      }
    });
  }

  void _onFeedTapped() {
    setState(() {
      _currentSpeech = _petState.feedTreat();
    });
    Future.delayed(const Duration(milliseconds: 3000), () {
      if (mounted) {
        setState(() => _currentSpeech = null);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: const Color(0xFFF7F5F0),
      body: Stack(
        children: [
          // Background ambient cards / dashboard
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
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
                          const Text(
                            'Your Floating Pocket Companion',
                            style: TextStyle(color: Colors.black54),
                          ),
                        ],
                      ),
                      IconButton.filledTonal(
                        onPressed: _showWardrobeSheet,
                        icon: const Icon(Icons.palette_outlined),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  _buildStatCard(),
                  const Spacer(),
                  _buildActionBar(),
                ],
              ),
            ),
          ),

          // Floating Mochi Pet with Draggable gesture physics
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
                  // Magnetic docking to edges
                  final snapLeft = _position.dx < size.width / 2;
                  _position = Offset(
                    snapLeft ? 16 : size.width - 150 - 16,
                    _position.dy.clamp(60, size.height - 220),
                  );
                });
              },
              onTap: _onPetTapped,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (_currentSpeech != null)
                    Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
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
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                          color: Color(0xFF333333),
                        ),
                      ),
                    ),
                  AnimatedBuilder(
                    animation: _animController,
                    builder: (context, child) {
                      return CustomPaint(
                        size: const Size(140, 140),
                        painter: BunnyPainter(
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
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: const [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 12,
            offset: Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          _buildStatRow('💖 Happiness', _petState.happiness, Colors.pinkAccent),
          const SizedBox(height: 12),
          _buildStatRow('⚡ Energy', _petState.energy, Colors.amber),
          const SizedBox(height: 12),
          _buildStatRow('🎓 Focus Today', '${_petState.focusMinutes} min', Colors.deepPurpleAccent),
        ],
      ),
    );
  }

  Widget _buildStatRow(String label, dynamic value, Color barColor) {
    final double fraction = (value is int) ? (value / 100.0).clamp(0.0, 1.0) : 1.0;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
            Text(value is int ? '$value%' : '$value'),
          ],
        ),
        const SizedBox(height: 6),
        LinearProgressIndicator(
          value: fraction,
          backgroundColor: Colors.grey.shade200,
          color: barColor,
          borderRadius: BorderRadius.circular(8),
          minHeight: 8,
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
            icon: const Icon(Icons.favorite),
            label: const Text('Pet Mochi'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
              backgroundColor: const Color(0xFFFF9AA2),
              foregroundColor: Colors.white,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: ElevatedButton.icon(
            onPressed: _onFeedTapped,
            icon: const Icon(Icons.restaurant),
            label: const Text('Treat 🍓'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
              backgroundColor: const Color(0xFFFFB7B2),
              foregroundColor: Colors.white,
            ),
          ),
        ),
      ],
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
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '🎨 Wardrobe & Colors',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 12,
                children: [
                  _colorPill('Vanilla Cream', const Color(0xFFFFF8E7)),
                  _colorPill('Strawberry Milk', const Color(0xFFFFD1DC)),
                  _colorPill('Cloud White', const Color(0xFFFFFFFF)),
                  _colorPill('Matcha Cream', const Color(0xFFE8F5E9)),
                  _colorPill('Lilac Mist', const Color(0xFFEDE7F6)),
                ],
              ),
            ],
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
        setState(() => _petState.primaryColor = color);
        Navigator.pop(context);
      },
    );
  }
}
