import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/glass_container.dart';
import '../../../core/providers/app_providers.dart';
import '../../dashboard/presentation/dashboard_screen.dart';
import '../../message_pools/presentation/message_pools_screen.dart';
import '../../scheduler/presentation/scheduler_config_screen.dart';
import '../../ai_prompts/presentation/ai_prompts_screen.dart';
import '../../logs/presentation/logs_screen.dart';
import '../../billing/presentation/billing_screen.dart';
import '../../admin/presentation/admin_panel_screen.dart';
import '../../failsafe/presentation/failsafe_screen.dart';

class MainLayout extends ConsumerWidget {
  const MainLayout({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      body: Stack(
        children: [
          // Background gradient
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  theme.primaryColor.withOpacity(0.1),
                  theme.colorScheme.secondary.withOpacity(0.05),
                  Colors.transparent,
                ],
              ),
            ),
          ),
          // Main content
          Positioned.fill(
            bottom: 80,
            child: IndexedStack(
              index: appState.selectedIndex,
              children: _screens,
            ),
          ),
          // Custom bottom navigation
          Positioned(
            left: 16,
            right: 16,
            bottom: 16,
            child: GlassContainer(
              borderRadius: 28,
              blur: 20,
              child: Container(
                height: 64,
                padding: const EdgeInsets.symmetric(horizontal: 8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: List.generate(_screens.length, (index) {
                    final isSelected = appState.selectedIndex == index;
                    final icon = _getIconForIndex(index);
                    final label = _getLabelForIndex(index);
                    
                    return Expanded(
                      child: GestureDetector(
                        onTap: () => ref.read(appStateProvider.notifier).setSelectedIndex(index),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 300),
                          curve: Curves.easeInOut,
                          margin: const EdgeInsets.all(4),
                          padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
                          decoration: BoxDecoration(
                            color: isSelected 
                              ? theme.primaryColor.withOpacity(0.2)
                              : Colors.transparent,
                            borderRadius: BorderRadius.circular(20),
                            border: isSelected 
                              ? Border.all(color: theme.primaryColor.withOpacity(0.5), width: 1)
                              : null,
                          ),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              AnimatedContainer(
                                duration: const Duration(milliseconds: 300),
                                child: Icon(
                                  icon,
                                  color: isSelected 
                                    ? theme.primaryColor
                                    : theme.iconTheme.color?.withOpacity(0.6),
                                  size: isSelected ? 24 : 20,
                                ),
                              ),
                              const SizedBox(height: 2),
                              AnimatedDefaultTextStyle(
                                duration: const Duration(milliseconds: 300),
                                style: TextStyle(
                                  color: isSelected 
                                    ? theme.primaryColor
                                    : theme.textTheme.bodySmall?.color?.withOpacity(0.6),
                                  fontSize: isSelected ? 10 : 9,
                                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                                ),
                                child: Text(
                                  label,
                                  textAlign: TextAlign.center,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  }),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  IconData _getIconForIndex(int index) {
    switch (index) {
      case 0: return Icons.dashboard_outlined;
      case 1: return Icons.message_outlined;
      case 2: return Icons.schedule_outlined;
      case 3: return Icons.psychology_outlined;
      case 4: return Icons.analytics_outlined;
      case 5: return Icons.account_balance_wallet_outlined;
      case 6: return Icons.admin_panel_settings_outlined;
      case 7: return Icons.warning_amber_outlined;
      default: return Icons.dashboard_outlined;
    }
  }

  String _getLabelForIndex(int index) {
    switch (index) {
      case 0: return 'Dashboard';
      case 1: return 'Mesajlar';
      case 2: return 'Zamanlama';
      case 3: return 'AI Prompt';
      case 4: return 'Loglar';
      case 5: return 'Hesap';
      case 6: return 'Admin';
      case 7: return 'Güvenlik';
      default: return 'Dashboard';
    }
  }
} 