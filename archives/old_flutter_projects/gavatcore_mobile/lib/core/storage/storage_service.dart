import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:convert';

// StorageService provider for Riverpod
final storageServiceProvider = Provider<StorageService>((ref) {
  return StorageService.instance;
});

class StorageService {
  static SharedPreferences? _preferences;
  static StorageService? _instance;

  // Private constructor
  StorageService._();

  // Static instance getter
  static StorageService get instance {
    _instance ??= StorageService._();
    return _instance!;
  }

  // Initialize SharedPreferences
  static Future<void> init() async {
    _preferences = await SharedPreferences.getInstance();
  }

  // String operations
  Future<void> setString(String key, String value) async {
    _preferences ??= await SharedPreferences.getInstance();
    await _preferences!.setString(key, value);
  }

  String? getString(String key) {
    return _preferences?.getString(key);
  }

  // Bool operations  
  Future<void> setBool(String key, bool value) async {
    _preferences ??= await SharedPreferences.getInstance();
    await _preferences!.setBool(key, value);
  }

  bool? getBool(String key) {
    return _preferences?.getBool(key);
  }

  // Int operations
  Future<void> setInt(String key, int value) async {
    _preferences ??= await SharedPreferences.getInstance();
    await _preferences!.setInt(key, value);
  }

  int? getInt(String key) {
    return _preferences?.getInt(key);
  }

  // Double operations
  Future<void> setDouble(String key, double value) async {
    _preferences ??= await SharedPreferences.getInstance();
    await _preferences!.setDouble(key, value);
  }

  double? getDouble(String key) {
    return _preferences?.getDouble(key);
  }

  // List operations
  Future<void> setStringList(String key, List<String> value) async {
    _preferences ??= await SharedPreferences.getInstance();
    await _preferences!.setStringList(key, value);
  }

  List<String>? getStringList(String key) {
    return _preferences?.getStringList(key);
  }

  // Map operations - JSON encoding/decoding
  Future<void> setMap(String key, Map<String, dynamic> value) async {
    _preferences ??= await SharedPreferences.getInstance();
    final jsonString = jsonEncode(value);
    await _preferences!.setString(key, jsonString);
  }

  Map<String, dynamic>? getMap(String key) {
    try {
      final jsonString = _preferences?.getString(key);
      if (jsonString != null) {
        return Map<String, dynamic>.from(jsonDecode(jsonString));
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  // Delete operations
  Future<void> deleteKey(String key) async {
    _preferences ??= await SharedPreferences.getInstance();
    await _preferences!.remove(key);
  }

  Future<void> clear() async {
    _preferences ??= await SharedPreferences.getInstance();
    await _preferences!.clear();
  }

  // Check if key exists
  bool containsKey(String key) {
    return _preferences?.containsKey(key) ?? false;
  }

  // Get all keys
  Set<String> getKeys() {
    return _preferences?.getKeys() ?? {};
  }

  // Legacy constructor support for old code
  factory StorageService() {
    return instance;
  }

  // Auth specific methods - Static versions
  static Future<void> setAuthToken(String token) async {
    final instance = StorageService();
    await instance.setString('auth_token', token);
  }

  // Static version for getUserData
  static Future<Map<String, dynamic>?> getUserData() async {
    final instance = StorageService();
    return instance.getMap('user_data');
  }

  // Static version for setUserData  
  static Future<void> setUserData(Map<String, dynamic> userData) async {
    final instance = StorageService();
    await instance.setMap('user_data', userData);
  }

  String? getAuthToken() {
    return getString('auth_token');
  }

  Future<void> removeAuthToken() async {
    await deleteKey('auth_token');
  }

  // User data methods - Instance versions
  Future<void> setUserDataInstance(Map<String, dynamic> userData) async {
    await setMap('user_data', userData);
  }

  Future<void> saveUser(Map<String, dynamic> userData) async {
    await setUserDataInstance(userData);
  }

  Map<String, dynamic>? getUserDataInstance() {
    return getMap('user_data');
  }

  Future<Map<String, dynamic>?> getUser() async {
    return getUserDataInstance();
  }

  // Login status - Static version
  static Future<bool> isLoggedIn() async {
    final instance = StorageService();
    final token = instance.getAuthToken();
    return token != null && token.isNotEmpty;
  }

  // Clear all data
  Future<void> clearAll() async {
    await clear();
  }

  // Get all keys as list
  List<String> getAllKeys() {
    return getKeys().toList();
  }

  // Get all values
  Map<String, dynamic> getAllData() {
    final Map<String, dynamic> data = {};
    for (final key in getKeys()) {
      final value = getString(key);
      if (value != null) {
        data[key] = value;
      }
    }
    return data;
  }
}