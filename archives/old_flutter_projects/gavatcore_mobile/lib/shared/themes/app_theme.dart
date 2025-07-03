import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color darkBg = Color(0xFF1A1A1A);
  static const Color cardBg = Color(0xFF2A2A2A);
  static const Color lightBg = Color(0xFFF5F5F5);
  static const Color lightCardBg = Color(0xFFFFFFFF);
  
  static const Color primaryColor = Color(0xFF6200EE);
  static const Color secondaryColor = Color(0xFF03DAC6);
  static const Color errorColor = Color(0xFFCF6679);
  static const Color successColor = Color(0xFF4CAF50);
  static const Color warningColor = Color(0xFFFF9800);
  
  static const Color textColor = Colors.white;
  static const Color textColorSecondary = Color(0xFFB3B3B3);
  static const Color textColorDark = Color(0xFF212121);
  static const Color textColorDarkSecondary = Color(0xFF757575);
  static const Color borderColor = Color(0xFF3A3A3A);

  // Getter properties for backward compatibility
  static Color get backgroundColor => darkBg;
  static Color get cardColor => cardBg;
  static Color get accentColor => secondaryColor;

  static ThemeData dark() {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      primaryColor: primaryColor,
      scaffoldBackgroundColor: darkBg,
      cardColor: cardBg,
      textTheme: GoogleFonts.interTextTheme(
        ThemeData.dark().textTheme,
      ),
      colorScheme: const ColorScheme.dark(
        primary: primaryColor,
        secondary: secondaryColor,
        error: errorColor,
        surface: cardBg,
      ),
    );
  }

  static ThemeData light() {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      primaryColor: primaryColor,
      scaffoldBackgroundColor: lightBg,
      cardColor: lightCardBg,
      textTheme: GoogleFonts.interTextTheme(
        ThemeData.light().textTheme,
      ),
      colorScheme: const ColorScheme.light(
        primary: primaryColor,
        secondary: secondaryColor,
        error: errorColor,
        surface: lightCardBg,
      ),
    );
  }

  static ThemeData get darkTheme => dark();
  static ThemeData get lightTheme => light();
} 