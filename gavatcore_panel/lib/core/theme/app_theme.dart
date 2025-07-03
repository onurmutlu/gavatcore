import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const _neonPurple = Color(0xFF8B5CF6);
  static const _neonBlue = Color(0xFF06B6D4);
  static const _neonGreen = Color(0xFF10B981);
  static const _neonPink = Color(0xFFEC4899);
  static const _neonYellow = Color(0xFFF59E0B);
  static const _neonRed = Color(0xFFEF4444);
  
  static const _darkBg = Color(0xFF0A0A0F);
  static const _darkCard = Color(0xFF1A1A2E);
  static const _darkSurface = Color(0xFF16213E);
  
  static final _glassBorder = BorderRadius.circular(16);
  
  static ThemeData get neonDarkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: _darkBg,
      
      // Color Scheme
      colorScheme: const ColorScheme.dark(
        primary: _neonPurple,
        secondary: _neonBlue,
        tertiary: _neonGreen,
        surface: _darkCard,
        background: _darkBg,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: Colors.white,
        onBackground: Colors.white70,
        error: _neonRed,
      ),
      
      // Typography
      textTheme: GoogleFonts.interTextTheme(
        const TextTheme(
          displayLarge: TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.bold,
            color: Colors.white,
            letterSpacing: -0.5,
          ),
          displayMedium: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
          headlineLarge: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
          headlineMedium: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w500,
            color: Colors.white,
          ),
          titleLarge: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w500,
            color: Colors.white,
          ),
          titleMedium: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w500,
            color: Colors.white,
          ),
          bodyLarge: TextStyle(
            fontSize: 16,
            color: Colors.white70,
          ),
          bodyMedium: TextStyle(
            fontSize: 14,
            color: Colors.white60,
          ),
          labelLarge: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w500,
            color: Colors.white,
          ),
        ),
      ),
      
      // App Bar Theme
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        systemOverlayStyle: SystemUiOverlayStyle.light,
        titleTextStyle: GoogleFonts.inter(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      
      // Card Theme
      cardTheme: CardTheme(
        color: _darkCard.withOpacity(0.3),
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: _glassBorder,
          side: BorderSide(
            color: Colors.white.withOpacity(0.1),
            width: 1,
          ),
        ),
      ),
      
      // Elevated Button Theme
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: _neonPurple,
          foregroundColor: Colors.white,
          elevation: 8,
          shadowColor: _neonPurple.withOpacity(0.3),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          textStyle: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      
      // Input Decoration Theme
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: _darkCard.withOpacity(0.3),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(
            color: Colors.white.withOpacity(0.1),
          ),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(
            color: Colors.white.withOpacity(0.1),
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(
            color: _neonPurple,
            width: 2,
          ),
        ),
        labelStyle: const TextStyle(color: Colors.white60),
        hintStyle: const TextStyle(color: Colors.white30),
      ),
      
      // Bottom Navigation Bar Theme
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: _darkCard.withOpacity(0.9),
        selectedItemColor: _neonPurple,
        unselectedItemColor: Colors.white60,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
      ),
      
      // Icon Theme
      iconTheme: const IconThemeData(
        color: Colors.white70,
        size: 24,
      ),
      
      // Divider Theme
      dividerTheme: DividerThemeData(
        color: Colors.white.withOpacity(0.1),
        thickness: 1,
      ),
    );
  }
  
  // Neon Color Palette
  static const neonColors = NeonColors();
  
  // Glass Morphism Decorations
  static BoxDecoration get glassDecoration => BoxDecoration(
    borderRadius: _glassBorder,
    border: Border.all(
      color: Colors.white.withOpacity(0.1),
      width: 1,
    ),
    gradient: LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [
        Colors.white.withOpacity(0.1),
        Colors.white.withOpacity(0.05),
      ],
    ),
  );
  
  static BoxDecoration get neonGlassDecoration => BoxDecoration(
    borderRadius: _glassBorder,
    border: Border.all(
      color: _neonPurple.withOpacity(0.3),
      width: 1,
    ),
    gradient: LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [
        _neonPurple.withOpacity(0.1),
        _neonBlue.withOpacity(0.05),
      ],
    ),
    boxShadow: [
      BoxShadow(
        color: _neonPurple.withOpacity(0.2),
        blurRadius: 20,
        spreadRadius: 1,
      ),
    ],
  );
  
  static BoxDecoration get accentGlassDecoration => BoxDecoration(
    borderRadius: _glassBorder,
    border: Border.all(
      color: _neonBlue.withOpacity(0.3),
      width: 1,
    ),
    gradient: LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [
        _neonBlue.withOpacity(0.1),
        _neonGreen.withOpacity(0.05),
      ],
    ),
    boxShadow: [
      BoxShadow(
        color: _neonBlue.withOpacity(0.2),
        blurRadius: 15,
        spreadRadius: 1,
      ),
    ],
  );
  
  // Gradient Backgrounds
  static LinearGradient get primaryGradient => const LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [_neonPurple, _neonBlue],
  );
  
  static LinearGradient get accentGradient => const LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [_neonBlue, _neonGreen],
  );
  
  static LinearGradient get warningGradient => const LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [_neonYellow, _neonRed],
  );
  
  static LinearGradient get backgroundGradient => LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [
      _darkBg,
      _darkBg.withOpacity(0.8),
      _darkCard.withOpacity(0.3),
    ],
  );
}

class NeonColors {
  const NeonColors();
  
  Color get purple => const Color(0xFF8B5CF6);
  Color get blue => const Color(0xFF06B6D4);
  Color get green => const Color(0xFF10B981);
  Color get pink => const Color(0xFFEC4899);
  Color get yellow => const Color(0xFFF59E0B);
  Color get red => const Color(0xFFEF4444);
  Color get orange => const Color(0xFFF97316);
  Color get indigo => const Color(0xFF6366F1);
  
  // Glow variants
  Color get purpleGlow => const Color(0xFF8B5CF6).withOpacity(0.3);
  Color get blueGlow => const Color(0xFF06B6D4).withOpacity(0.3);
  Color get greenGlow => const Color(0xFF10B981).withOpacity(0.3);
  Color get pinkGlow => const Color(0xFFEC4899).withOpacity(0.3);
}

// Custom Neon Text Styles
class NeonTextStyles {
  static TextStyle get neonTitle => GoogleFonts.inter(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: Colors.white,
    shadows: [
      Shadow(
        color: AppTheme.neonColors.purple,
        blurRadius: 10,
      ),
    ],
  );
  
  static TextStyle get neonSubtitle => GoogleFonts.inter(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: Colors.white,
    shadows: [
      Shadow(
        color: AppTheme.neonColors.blue,
        blurRadius: 8,
      ),
    ],
  );
  
  static TextStyle get neonBody => GoogleFonts.inter(
    fontSize: 14,
    color: Colors.white70,
    shadows: [
      Shadow(
        color: AppTheme.neonColors.purple.withOpacity(0.5),
        blurRadius: 5,
      ),
    ],
  );
} 