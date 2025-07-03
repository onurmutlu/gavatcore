import 'package:hive_flutter/hive_flutter.dart';

class StorageService {
  static const String _authBoxName = 'auth_box';
  static const String _settingsBoxName = 'settings_box';
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_data';
  
  static late Box _authBox;
  static late Box _settingsBox;

  static Future<void> init() async {
    await Hive.initFlutter();
    _authBox = await Hive.openBox(_authBoxName);
    _settingsBox = await Hive.openBox(_settingsBoxName);
  }

  // Auth Token Methods
  static Future<String?> getAuthToken() async {
    try {
      return _authBox.get(_tokenKey);
    } catch (e) {
      return null;
    }
  }

  static Future<void> saveAuthToken(String token) async {
    try {
      await _authBox.put(_tokenKey, token);
    } catch (e) {
      // Handle error
    }
  }

  static Future<void> clearAuthToken() async {
    try {
      await _authBox.delete(_tokenKey);
    } catch (e) {
      // Handle error
    }
  }

  // User Data Methods
  static Future<Map<String, dynamic>?> getUser() async {
    try {
      final userData = _authBox.get(_userKey);
      if (userData is Map) {
        return Map<String, dynamic>.from(userData);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  static Future<void> saveUser(Map<String, dynamic> userData) async {
    try {
      await _authBox.put(_userKey, userData);
    } catch (e) {
      // Handle error
    }
  }

  static Future<void> clearUser() async {
    try {
      await _authBox.delete(_userKey);
    } catch (e) {
      // Handle error
    }
  }

  // Settings Methods
  static Future<T?> getSetting<T>(String key) async {
    try {
      return _settingsBox.get(key);
    } catch (e) {
      return null;
    }
  }

  static Future<void> saveSetting<T>(String key, T value) async {
    try {
      await _settingsBox.put(key, value);
    } catch (e) {
      // Handle error
    }
  }

  static Future<void> clearSetting(String key) async {
    try {
      await _settingsBox.delete(key);
    } catch (e) {
      // Handle error
    }
  }

  // Clear All Data
  static Future<void> clearAll() async {
    try {
      await _authBox.clear();
      await _settingsBox.clear();
    } catch (e) {
      // Handle error
    }
  }
} 