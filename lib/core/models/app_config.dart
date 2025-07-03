import 'package:flutter/material.dart';

class AppConfig {
  final String apiBaseUrl;
  final String appName;
  final ThemeMode themeMode;
  final Locale locale;
  final bool enableAnalytics;
  final bool enableCrashReporting;
  
  const AppConfig({
    required this.apiBaseUrl,
    this.appName = 'GavatCore',
    this.themeMode = ThemeMode.dark,
    this.locale = const Locale('tr', 'TR'),
    this.enableAnalytics = true,
    this.enableCrashReporting = true,
  });
  
  AppConfig copyWith({
    String? apiBaseUrl,
    String? appName,
    ThemeMode? themeMode,
    Locale? locale,
    bool? enableAnalytics,
    bool? enableCrashReporting,
  }) {
    return AppConfig(
      apiBaseUrl: apiBaseUrl ?? this.apiBaseUrl,
      appName: appName ?? this.appName,
      themeMode: themeMode ?? this.themeMode,
      locale: locale ?? this.locale,
      enableAnalytics: enableAnalytics ?? this.enableAnalytics,
      enableCrashReporting: enableCrashReporting ?? this.enableCrashReporting,
    );
  }
} 