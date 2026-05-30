import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:html' as html;
import 'dart:js' as js;
import 'dart:convert';

// Telegram WebApp API Integration
class TelegramMiniApp {
  static TelegramMiniApp? _instance;
  static TelegramMiniApp get instance => _instance ??= TelegramMiniApp._();
  TelegramMiniApp._();

  bool _isInitialized = false;
  Map<String, dynamic>? _initData;
  TelegramUser? _user;
  TelegramChat? _chat;

  // Initialize Telegram MiniApp
  Future<bool> initialize() async {
    try {
      // Check if running inside Telegram
      if (!isTelegramWebApp) {
        print('Not running inside Telegram WebApp');
        return false;
      }

      // Get Telegram WebApp object
      final telegramWebApp = js.context['Telegram']['WebApp'];
      
      // Parse init data
      final initDataUnsafe = telegramWebApp['initDataUnsafe'];
      if (initDataUnsafe != null) {
        _initData = _jsObjectToMap(initDataUnsafe);
        
        // Parse user data
        if (_initData!['user'] != null) {
          _user = TelegramUser.fromJson(_initData!['user']);
        }
        
        // Parse chat data
        if (_initData!['chat'] != null) {
          _chat = TelegramChat.fromJson(_initData!['chat']);
        }
      }

      // Configure WebApp
      telegramWebApp.callMethod('ready');
      telegramWebApp.callMethod('expand');
      
      // Set theme
      _setTheme();
      
      _isInitialized = true;
      return true;
    } catch (e) {
      print('Failed to initialize Telegram MiniApp: $e');
      return false;
    }
  }

  // Check if running inside Telegram WebApp
  bool get isTelegramWebApp {
    try {
      return js.context.hasProperty('Telegram') && 
             js.context['Telegram'].hasProperty('WebApp');
    } catch (e) {
      return false;
    }
  }

  // Get current user
  TelegramUser? get currentUser => _user;

  // Get current chat
  TelegramChat? get currentChat => _chat;

  // Set theme colors
  void _setTheme() {
    try {
      final telegramWebApp = js.context['Telegram']['WebApp'];
      final themeParams = telegramWebApp['themeParams'];
      
      if (themeParams != null) {
        // Apply Telegram theme colors
        telegramWebApp.callMethod('setHeaderColor', ['#0A0A0F']);
        telegramWebApp.callMethod('setBackgroundColor', ['#0A0A0F']);
      }
    } catch (e) {
      print('Failed to set theme: $e');
    }
  }

  // Show main button
  void showMainButton({
    required String text,
    required VoidCallback onPressed,
    Color? color,
    Color? textColor,
  }) {
    try {
      final telegramWebApp = js.context['Telegram']['WebApp'];
      final mainButton = telegramWebApp['MainButton'];
      
      mainButton.callMethod('setText', [text]);
      if (color != null) {
        mainButton.callMethod('setParams', [
          js.JsObject.jsify({
            'color': '#${color.value.toRadixString(16).substring(2)}',
            'text_color': '#${(textColor ?? Colors.white).value.toRadixString(16).substring(2)}',
          })
        ]);
      }
      
      // Set click handler
      mainButton.callMethod('onClick', [
        js.allowInterop((_) => onPressed())
      ]);
      
      mainButton.callMethod('show');
    } catch (e) {
      print('Failed to show main button: $e');
    }
  }

  // Hide main button
  void hideMainButton() {
    try {
      final telegramWebApp = js.context['Telegram']['WebApp'];
      final mainButton = telegramWebApp['MainButton'];
      mainButton.callMethod('hide');
    } catch (e) {
      print('Failed to hide main button: $e');
    }
  }

  // Show back button
  void showBackButton(VoidCallback onPressed) {
    try {
      final telegramWebApp = js.context['Telegram']['WebApp'];
      final backButton = telegramWebApp['BackButton'];
      
      backButton.callMethod('onClick', [
        js.allowInterop((_) => onPressed())
      ]);
      
      backButton.callMethod('show');
    } catch (e) {
      print('Failed to show back button: $e');
    }
  }

  // Hide back button
  void hideBackButton() {
    try {
      final telegramWebApp = js.context['Telegram']['WebApp'];
      final backButton = telegramWebApp['BackButton'];
      backButton.callMethod('hide');
    } catch (e) {
      print('Failed to hide back button: $e');
    }
  }

  // Send data to Telegram
  void sendData(Map<String, dynamic> data) {
    try {
      final telegramWebApp = js.context['Telegram']['WebApp'];
      telegramWebApp.callMethod('sendData', [json.encode(data)]);
    } catch (e) {
      print('Failed to send data: $e');
    }
  }

  // Close MiniApp
  void close() {
    try {
      final telegramWebApp = js.context['Telegram']['WebApp'];
      telegramWebApp.callMethod('close');
    } catch (e) {
      print('Failed to close MiniApp: $e');
    }
  }

  // Show popup
  void showPopup({
    required String title,
    required String message,
    List<PopupButton>? buttons,
  }) {
    try {
      final telegramWebApp = js.context['Telegram']['WebApp'];
      
      final popupParams = <String, dynamic>{
        'title': title,
        'message': message,
      };
      
      if (buttons != null && buttons.isNotEmpty) {
        popupParams['buttons'] = buttons.map((button) => button.toJson()).toList();
      }
      
      telegramWebApp.callMethod('showPopup', [
        js.JsObject.jsify(popupParams)
      ]);
    } catch (e) {
      print('Failed to show popup: $e');
    }
  }

  // Show confirm dialog
  void showConfirm({
    required String message,
    required VoidCallback onConfirm,
    VoidCallback? onCancel,
  }) {
    try {
      final telegramWebApp = js.context['Telegram']['WebApp'];
      
      telegramWebApp.callMethod('showConfirm', [
        message,
        js.allowInterop((bool confirmed) {
          if (confirmed) {
            onConfirm();
          } else {
            onCancel?.call();
          }
        })
      ]);
    } catch (e) {
      print('Failed to show confirm: $e');
    }
  }

  // Show alert
  void showAlert({
    required String message,
    VoidCallback? onClose,
  }) {
    try {
      final telegramWebApp = js.context['Telegram']['WebApp'];
      
      telegramWebApp.callMethod('showAlert', [
        message,
        if (onClose != null) js.allowInterop((_) => onClose())
      ]);
    } catch (e) {
      print('Failed to show alert: $e');
    }
  }

  // Haptic feedback
  void hapticFeedback(HapticFeedbackType type) {
    try {
      final telegramWebApp = js.context['Telegram']['WebApp'];
      final hapticFeedback = telegramWebApp['HapticFeedback'];
      
      String typeString;
      switch (type) {
        case HapticFeedbackType.light:
          typeString = 'impact';
          break;
        case HapticFeedbackType.medium:
          typeString = 'notification';
          break;
        case HapticFeedbackType.heavy:
          typeString = 'selection';
          break;
      }
      
      hapticFeedback.callMethod('impactOccurred', [typeString]);
    } catch (e) {
      print('Failed to trigger haptic feedback: $e');
    }
  }

  // Open invoice
  void openInvoice({
    required String invoiceUrl,
    required VoidCallback onSuccess,
    VoidCallback? onFailure,
  }) {
    try {
      final telegramWebApp = js.context['Telegram']['WebApp'];
      
      telegramWebApp.callMethod('openInvoice', [
        invoiceUrl,
        js.allowInterop((String status) {
          if (status == 'paid') {
            onSuccess();
          } else {
            onFailure?.call();
          }
        })
      ]);
    } catch (e) {
      print('Failed to open invoice: $e');
    }
  }

  // Utils
  Map<String, dynamic> _jsObjectToMap(jsObject) {
    try {
      return json.decode(js.context['JSON'].callMethod('stringify', [jsObject]));
    } catch (e) {
      return {};
    }
  }
}

// Models
class TelegramUser {
  final int id;
  final String firstName;
  final String? lastName;
  final String? username;
  final String? languageCode;
  final bool? isPremium;
  final String? photoUrl;

  TelegramUser({
    required this.id,
    required this.firstName,
    this.lastName,
    this.username,
    this.languageCode,
    this.isPremium,
    this.photoUrl,
  });

  factory TelegramUser.fromJson(Map<String, dynamic> json) {
    return TelegramUser(
      id: json['id'],
      firstName: json['first_name'],
      lastName: json['last_name'],
      username: json['username'],
      languageCode: json['language_code'],
      isPremium: json['is_premium'],
      photoUrl: json['photo_url'],
    );
  }

  String get fullName => lastName != null ? '$firstName $lastName' : firstName;
}

class TelegramChat {
  final int id;
  final String type;
  final String? title;
  final String? username;
  final String? photoUrl;

  TelegramChat({
    required this.id,
    required this.type,
    this.title,
    this.username,
    this.photoUrl,
  });

  factory TelegramChat.fromJson(Map<String, dynamic> json) {
    return TelegramChat(
      id: json['id'],
      type: json['type'],
      title: json['title'],
      username: json['username'],
      photoUrl: json['photo_url'],
    );
  }
}

class PopupButton {
  final String id;
  final String text;
  final String? type;

  PopupButton({
    required this.id,
    required this.text,
    this.type,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'text': text,
      if (type != null) 'type': type,
    };
  }
}

enum HapticFeedbackType {
  light,
  medium,
  heavy,
}

// Telegram MiniApp Wrapper Widget
class TelegramMiniAppWrapper extends StatefulWidget {
  final Widget child;
  final bool enableBackButton;
  final String? mainButtonText;
  final VoidCallback? onMainButtonPressed;
  final VoidCallback? onBackButtonPressed;

  const TelegramMiniAppWrapper({
    Key? key,
    required this.child,
    this.enableBackButton = false,
    this.mainButtonText,
    this.onMainButtonPressed,
    this.onBackButtonPressed,
  }) : super(key: key);

  @override
  State<TelegramMiniAppWrapper> createState() => _TelegramMiniAppWrapperState();
}

class _TelegramMiniAppWrapperState extends State<TelegramMiniAppWrapper> {
  final TelegramMiniApp _telegramMiniApp = TelegramMiniApp.instance;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initializeTelegramMiniApp();
  }

  Future<void> _initializeTelegramMiniApp() async {
    final success = await _telegramMiniApp.initialize();
    if (success) {
      setState(() {
        _isInitialized = true;
      });
      
      _setupButtons();
    }
  }

  void _setupButtons() {
    // Setup main button
    if (widget.mainButtonText != null && widget.onMainButtonPressed != null) {
      _telegramMiniApp.showMainButton(
        text: widget.mainButtonText!,
        onPressed: widget.onMainButtonPressed!,
        color: const Color(0xFF7B68EE),
      );
    }

    // Setup back button
    if (widget.enableBackButton) {
      _telegramMiniApp.showBackButton(
        widget.onBackButtonPressed ?? () => Navigator.of(context).pop(),
      );
    }
  }

  @override
  void dispose() {
    _telegramMiniApp.hideMainButton();
    _telegramMiniApp.hideBackButton();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return widget.child;
  }
}

// Telegram Theme Provider
class TelegramThemeProvider extends StatelessWidget {
  final Widget child;

  const TelegramThemeProvider({Key? key, required this.child}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final telegramMiniApp = TelegramMiniApp.instance;
    
    if (!telegramMiniApp.isTelegramWebApp) {
      return child;
    }

    // Apply Telegram-specific theme modifications
    return Theme(
      data: Theme.of(context).copyWith(
        colorScheme: Theme.of(context).colorScheme.copyWith(
          primary: const Color(0xFF7B68EE),
          secondary: const Color(0xFF9C27B0),
          background: const Color(0xFF0A0A0F),
          surface: const Color(0xFF1A1A2E),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1A1A2E),
          foregroundColor: Colors.white,
          elevation: 0,
        ),
      ),
      child: child,
    );
  }
}

// Telegram User Widget
class TelegramUserWidget extends StatelessWidget {
  final TelegramUser user;

  const TelegramUserWidget({Key? key, required this.user}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A2E),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          CircleAvatar(
            backgroundImage: user.photoUrl != null 
              ? NetworkImage(user.photoUrl!) 
              : null,
            child: user.photoUrl == null 
              ? Text(user.firstName[0].toUpperCase())
              : null,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  user.fullName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (user.username != null)
                  Text(
                    '@${user.username}',
                    style: const TextStyle(
                      color: Colors.grey,
                      fontSize: 12,
                    ),
                  ),
              ],
            ),
          ),
          if (user.isPremium == true)
            const Icon(
              Icons.star,
              color: Colors.amber,
              size: 16,
            ),
        ],
      ),
    );
  }
} 