import '../storage/storage_service.dart';

class AdminAuth {
  // 🔐 Authorized admin users
  static const List<String> authorizedAdmins = [
    'onur_mutlu',
    'admin',
    'siyahkare',
    'babagavat_admin',
    'system_admin'
  ];

  // 🎯 Admin roles and permissions
  static const Map<String, List<String>> adminRoles = {
    'onur_mutlu': ['super_admin', 'system_control', 'user_management', 'bot_control'],
    'admin': ['system_control', 'user_management'],
    'siyahkare': ['super_admin', 'system_control', 'bot_control'],
    'babagavat_admin': ['bot_control', 'user_management'],
    'system_admin': ['system_control'],
  };

  // ✅ Check if user is authorized admin
  static bool isAdmin(String username) {
    return authorizedAdmins.contains(username.toLowerCase());
  }

  // 🎫 Check specific permission
  static bool hasPermission(String username, String permission) {
    final userRoles = adminRoles[username.toLowerCase()] ?? [];
    return userRoles.contains(permission) || userRoles.contains('super_admin');
  }

  // 🔑 Current admin session
  static Future<String?> getCurrentAdmin() async {
    return StorageService.instance.getString('current_admin');
  }

  // 💾 Save admin session
  static Future<void> setCurrentAdmin(String username) async {
    if (isAdmin(username)) {
      await StorageService.instance.setString('current_admin', username);
      await StorageService.instance.setString('admin_login_time', DateTime.now().toIso8601String());
    }
  }

  // 🚪 Admin logout
  static Future<void> logout() async {
    await StorageService.instance.deleteKey('current_admin');
    await StorageService.instance.deleteKey('admin_login_time');
  }

  // ⏰ Check session validity (24 hours)
  static Future<bool> isSessionValid() async {
    final loginTime = StorageService.instance.getString('admin_login_time');
    if (loginTime == null) return false;

    try {
      final loginDateTime = DateTime.parse(loginTime);
      final now = DateTime.now();
      final difference = now.difference(loginDateTime);
      
      // Session valid for 24 hours
      return difference.inHours < 24;
    } catch (e) {
      return false;
    }
  }

  // 🔓 Full admin authentication check
  static Future<bool> isAuthenticated() async {
    final currentAdmin = await getCurrentAdmin();
    if (currentAdmin == null) return false;
    
    final isValidSession = await isSessionValid();
    return isAdmin(currentAdmin) && isValidSession;
  }

  // 📊 Get admin info
  static Future<Map<String, dynamic>?> getAdminInfo() async {
    final currentAdmin = await getCurrentAdmin();
    if (currentAdmin == null || !isAdmin(currentAdmin)) return null;

    return {
      'username': currentAdmin,
      'roles': adminRoles[currentAdmin] ?? [],
      'login_time': StorageService.instance.getString('admin_login_time'),
      'is_super_admin': hasPermission(currentAdmin, 'super_admin'),
    };
  }

  // 🛡️ Admin permissions enum for easy checking
  static const String SYSTEM_CONTROL = 'system_control';
  static const String USER_MANAGEMENT = 'user_management';
  static const String BOT_CONTROL = 'bot_control';
  static const String SUPER_ADMIN = 'super_admin';
} 