import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'core/theme/app_theme.dart';
import 'core/providers/app_providers.dart';
import 'features/dashboard/presentation/main_layout.dart';

class GavatCoreApp extends ConsumerWidget {
  const GavatCoreApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);
    
    return MaterialApp(
      title: 'GavatCore Panel',
      debugShowCheckedModeBanner: false,
      
      // Theme
      theme: AppTheme.neonDarkTheme,
      themeMode: ThemeMode.dark,
      
      // Localization
      supportedLocales: const [
        Locale('en', 'US'),
        Locale('tr', 'TR'),
      ],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      
      // Home
      home: const MainLayout(),
      
      // Routes
      routes: {
        '/dashboard': (context) => const MainLayout(),
      },
      
      // Builder for custom styling
      builder: (context, child) {
        return Container(
          decoration: BoxDecoration(
            gradient: AppTheme.backgroundGradient,
          ),
          child: child,
        );
      },
    );
  }
} 