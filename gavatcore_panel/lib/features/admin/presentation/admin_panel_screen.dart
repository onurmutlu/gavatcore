import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/glass_container.dart';

class AdminPanelScreen extends ConsumerWidget {
  const AdminPanelScreen({super.key});

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
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.admin_panel_settings,
                      size: 64,
                      color: AppTheme.neonColors.red,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Admin Override Panel',
                      style: NeonTextStyles.neonTitle,
                    ),
                    const SizedBox(height: 8),
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Admin Override Panel',
            style: NeonTextStyles.neonTitle,
          ),
          const SizedBox(height: 8),
          Text(
            'Execute admin commands and system overrides',
            style: TextStyle(color: Colors.white70),
          ),
        ],
      ),
    ).animate().slideY(begin: -0.3, duration: 600.ms);
  }
} 