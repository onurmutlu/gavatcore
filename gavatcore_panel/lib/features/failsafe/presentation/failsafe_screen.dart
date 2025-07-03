import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/glass_container.dart';

class FailSafeScreen extends ConsumerWidget {
  const FailSafeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 24),
          Expanded(
            child: Center(
              child: GlassContainer(
                width: 300,
                padding: const EdgeInsets.all(32),
                isNeonBorder: true,
                borderColor: AppTheme.neonColors.red,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.emergency,
                      size: 64,
                      color: AppTheme.neonColors.red,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Fail-Safe Reset',
                      style: NeonTextStyles.neonTitle.copyWith(
                        color: AppTheme.neonColors.red,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Emergency Controls',
                      style: TextStyle(color: Colors.white60),
                    ),
                    const SizedBox(height: 24),
                    Text(
                      'Coming Soon',
                      style: TextStyle(color: Colors.white60),
                    ),
                  ],
                ),
              ).animate().scale(duration: 600.ms),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return GlassContainer(
      padding: const EdgeInsets.all(24),
      isNeonBorder: true,
      borderColor: AppTheme.neonColors.red,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.warning,
                color: AppTheme.neonColors.red,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                'Fail-Safe Reset Triggers',
                style: NeonTextStyles.neonTitle,
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Emergency system reset and recovery controls',
            style: TextStyle(color: Colors.white70),
          ),
        ],
      ),
    ).animate().slideY(begin: -0.3, duration: 600.ms);
  }
} 