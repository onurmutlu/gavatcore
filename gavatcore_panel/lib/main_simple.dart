import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_web_plugins/url_strategy.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  usePathUrlStrategy();
  
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: Color(0xFF0A0A0F),
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );

  runApp(
    const ProviderScope(
      child: GavatCoreApp(),
    ),
  );
}

class GavatCoreApp extends StatelessWidget {
  const GavatCoreApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GavatCore Panel',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF9C27B0),
          brightness: Brightness.dark,
        ),
        cardTheme: CardThemeData(
          color: const Color(0xFF1A1A1F),
          elevation: 2,
          margin: const EdgeInsets.all(8),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      home: const TelegramAuthScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

// Simple Telegram Authentication Screen
class TelegramAuthScreen extends StatefulWidget {
  const TelegramAuthScreen({Key? key}) : super(key: key);

  @override
  State<TelegramAuthScreen> createState() => _TelegramAuthScreenState();
}

class _TelegramAuthScreenState extends State<TelegramAuthScreen> {
  final _phoneController = TextEditingController();
  final _codeController = TextEditingController();
  final _twoFactorController = TextEditingController();
  
  AuthStep _currentStep = AuthStep.phoneInput;
  bool _isLoading = false;
  String? _errorMessage;
  String? _phoneCodeHash;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: SizedBox(
              width: MediaQuery.of(context).size.width > 600 ? 400 : double.infinity,
              child: Card(
                elevation: 8,
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      _buildHeader(),
                      const SizedBox(height: 40),
                      if (_isLoading)
                        const CircularProgressIndicator(color: Colors.purple)
                      else
                        _buildCurrentStep(),
                      if (_errorMessage != null) ...[
                        const SizedBox(height: 16),
                        _buildErrorMessage(),
                      ],
                      const SizedBox(height: 24),
                      _buildActionButtons(),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    String title;
    String subtitle;
    
    switch (_currentStep) {
      case AuthStep.phoneInput:
        title = 'Telegram Authentication';
        subtitle = 'Enter your phone number to connect';
        break;
      case AuthStep.codeVerification:
        title = 'Enter Verification Code';
        subtitle = 'Check your Telegram for the code';
        break;
      case AuthStep.twoFactorAuth:
        title = 'Two-Factor Authentication';
        subtitle = 'Enter your 2FA password';
        break;
      case AuthStep.success:
        title = 'Authentication Success!';
        subtitle = 'You can now manage your bots';
        break;
    }

    return Column(
      children: [
        const Icon(
          Icons.telegram,
          size: 64,
          color: Colors.blue,
        ),
        const SizedBox(height: 16),
        Text(
          title,
          style: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          subtitle,
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey[400],
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildCurrentStep() {
    switch (_currentStep) {
      case AuthStep.phoneInput:
        return _buildPhoneInput();
      case AuthStep.codeVerification:
        return _buildCodeInput();
      case AuthStep.twoFactorAuth:
        return _buildTwoFactorInput();
      case AuthStep.success:
        return _buildSuccessScreen();
    }
  }

  Widget _buildPhoneInput() {
    return TextFormField(
      controller: _phoneController,
      keyboardType: TextInputType.phone,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        labelText: 'Phone Number',
        hintText: '+1234567890',
        prefixIcon: const Icon(Icons.phone, color: Colors.purple),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Colors.purple),
        ),
      ),
    );
  }

  Widget _buildCodeInput() {
    return TextFormField(
      controller: _codeController,
      keyboardType: TextInputType.number,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        labelText: 'Verification Code',
        hintText: '12345',
        prefixIcon: const Icon(Icons.security, color: Colors.purple),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Colors.purple),
        ),
      ),
    );
  }

  Widget _buildTwoFactorInput() {
    return TextFormField(
      controller: _twoFactorController,
      obscureText: true,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        labelText: '2FA Password',
        hintText: 'Enter your 2FA password',
        prefixIcon: const Icon(Icons.lock, color: Colors.purple),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Colors.purple),
        ),
      ),
    );
  }

  Widget _buildSuccessScreen() {
    return Column(
      children: [
        const Icon(
          Icons.check_circle,
          size: 80,
          color: Colors.green,
        ),
        const SizedBox(height: 24),
        const Text(
          'Successfully authenticated!',
          style: TextStyle(
            fontSize: 18,
            color: Colors.green,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        ElevatedButton.icon(
          onPressed: () {
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (_) => const MessagingScreen()),
            );
          },
          icon: const Icon(Icons.message),
          label: const Text('Start Messaging'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.purple,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          ),
        ),
      ],
    );
  }

  Widget _buildActionButtons() {
    if (_currentStep == AuthStep.success) return const SizedBox.shrink();
    
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: _handleAction,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.purple,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: Text(
              _getButtonText(),
              style: const TextStyle(fontSize: 16, color: Colors.white),
            ),
          ),
        ),
        if (_currentStep != AuthStep.phoneInput) ...[
          const SizedBox(height: 12),
          TextButton(
            onPressed: _goBack,
            child: const Text(
              'Go Back',
              style: TextStyle(color: Colors.grey),
            ),
          ),
        ],
      ],
    );
  }

  String _getButtonText() {
    switch (_currentStep) {
      case AuthStep.phoneInput:
        return 'Send Code';
      case AuthStep.codeVerification:
        return 'Verify Code';
      case AuthStep.twoFactorAuth:
        return 'Authenticate';
      default:
        return 'Continue';
    }
  }

  Widget _buildErrorMessage() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.withOpacity(0.5)),
      ),
      child: Row(
        children: [
          const Icon(Icons.error, color: Colors.red, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              _errorMessage!,
              style: const TextStyle(color: Colors.red, fontSize: 14),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _handleAction() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      switch (_currentStep) {
        case AuthStep.phoneInput:
          await _sendCode();
          break;
        case AuthStep.codeVerification:
          await _verifyCode();
          break;
        case AuthStep.twoFactorAuth:
          await _verifyTwoFactor();
          break;
        default:
          break;
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _sendCode() async {
    if (_phoneController.text.trim().isEmpty) {
      throw Exception('Please enter your phone number');
    }

    try {
      final response = await http.post(
        Uri.parse('http://localhost:5050/api/telegram/send-code'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'phone_number': _phoneController.text.trim()}),
      );

      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        setState(() {
          _phoneCodeHash = result['phone_code_hash'];
          _currentStep = AuthStep.codeVerification;
          _isLoading = false;
        });
        _showSuccess('Verification code sent!');
      } else {
        throw Exception('Failed to send code: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Future<void> _verifyCode() async {
    if (_codeController.text.trim().isEmpty) {
      throw Exception('Please enter the verification code');
    }

    try {
      final response = await http.post(
        Uri.parse('http://localhost:5050/api/telegram/verify-code'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'phone_number': _phoneController.text.trim(),
          'code': _codeController.text.trim(),
          'phone_code_hash': _phoneCodeHash,
        }),
      );

      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        
        if (result['needs_password'] == true) {
          setState(() {
            _currentStep = AuthStep.twoFactorAuth;
            _isLoading = false;
          });
        } else {
          setState(() {
            _currentStep = AuthStep.success;
            _isLoading = false;
          });
        }
      } else {
        throw Exception('Code verification failed');
      }
    } catch (e) {
      throw Exception('Verification error: $e');
    }
  }

  Future<void> _verifyTwoFactor() async {
    if (_twoFactorController.text.trim().isEmpty) {
      throw Exception('Please enter your 2FA password');
    }

    try {
      final response = await http.post(
        Uri.parse('http://localhost:5050/api/telegram/verify-2fa'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'password': _twoFactorController.text.trim()}),
      );

      if (response.statusCode == 200) {
        setState(() {
          _currentStep = AuthStep.success;
          _isLoading = false;
        });
      } else {
        throw Exception('2FA verification failed');
      }
    } catch (e) {
      throw Exception('2FA error: $e');
    }
  }

  void _goBack() {
    setState(() {
      if (_currentStep == AuthStep.twoFactorAuth) {
        _currentStep = AuthStep.codeVerification;
      } else if (_currentStep == AuthStep.codeVerification) {
        _currentStep = AuthStep.phoneInput;
      }
    });
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
      ),
    );
  }
}

// Simple Messaging Screen
class MessagingScreen extends StatefulWidget {
  const MessagingScreen({Key? key}) : super(key: key);

  @override
  State<MessagingScreen> createState() => _MessagingScreenState();
}

class _MessagingScreenState extends State<MessagingScreen> {
  final _messageController = TextEditingController();
  final _chatIdController = TextEditingController();
  String _selectedBot = 'lara';
  bool _isLoading = false;
  List<Map<String, dynamic>> _chats = [];
  List<Map<String, dynamic>> _messages = [];
  String? _selectedChatId;

  @override
  void initState() {
    super.initState();
    _loadChats();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        title: const Text('GavatCore Messaging'),
        backgroundColor: const Color(0xFF1A1A2E),
        actions: [
          DropdownButton<String>(
            value: _selectedBot,
            dropdownColor: const Color(0xFF1A1A2E),
            items: ['lara', 'babagavat', 'geisha'].map((bot) {
              return DropdownMenuItem(
                value: bot,
                child: Text(bot.toUpperCase(), style: const TextStyle(color: Colors.white)),
              );
            }).toList(),
            onChanged: (value) => setState(() => _selectedBot = value!),
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadChats,
          ),
        ],
      ),
      body: Row(
        children: [
          // Chat list
          Container(
            width: 300,
            decoration: const BoxDecoration(
              border: Border(right: BorderSide(color: Colors.grey, width: 0.5)),
            ),
            child: Column(
              children: [
                const Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Chats',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                ),
                Expanded(
                  child: ListView.builder(
                    itemCount: _chats.length,
                    itemBuilder: (context, index) {
                      final chat = _chats[index];
                      return ListTile(
                        title: Text(
                          chat['title'] ?? chat['first_name'] ?? 'Unknown',
                          style: const TextStyle(color: Colors.white),
                        ),
                        subtitle: Text(
                          'ID: ${chat['id']}',
                          style: const TextStyle(color: Colors.grey, fontSize: 12),
                        ),
                        selected: _selectedChatId == chat['id'].toString(),
                        onTap: () {
                          setState(() => _selectedChatId = chat['id'].toString());
                          _loadMessages();
                        },
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
          // Message area
          Expanded(
            child: Column(
              children: [
                Expanded(
                  child: _selectedChatId == null
                      ? const Center(
                          child: Text(
                            'Select a chat to view messages',
                            style: TextStyle(color: Colors.grey),
                          ),
                        )
                      : ListView.builder(
                          reverse: true,
                          itemCount: _messages.length,
                          itemBuilder: (context, index) {
                            final message = _messages[_messages.length - 1 - index];
                            return ListTile(
                              title: Text(
                                message['text'] ?? '',
                                style: const TextStyle(color: Colors.white),
                              ),
                              subtitle: Text(
                                _formatTime(message['date']),
                                style: const TextStyle(color: Colors.grey, fontSize: 12),
                              ),
                            );
                          },
                        ),
                ),
                _buildMessageInput(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageInput() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Colors.grey, width: 0.5)),
      ),
      child: Column(
        children: [
          if (_selectedChatId == null)
            TextField(
              controller: _chatIdController,
              decoration: const InputDecoration(
                labelText: 'Chat ID',
                hintText: 'Enter chat ID manually',
              ),
            ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _messageController,
                  decoration: const InputDecoration(
                    hintText: 'Type your message...',
                    border: OutlineInputBorder(),
                  ),
                  onSubmitted: (_) => _sendMessage(),
                ),
              ),
              const SizedBox(width: 12),
              FloatingActionButton(
                mini: true,
                backgroundColor: Colors.purple,
                onPressed: _isLoading ? null : _sendMessage,
                child: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                      )
                    : const Icon(Icons.send),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _loadChats() async {
    try {
      final response = await http.get(
        Uri.parse('http://localhost:5050/api/telegram/chats'),
      );
      
      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        setState(() => _chats = List<Map<String, dynamic>>.from(result['chats'] ?? []));
      }
    } catch (e) {
      print('Failed to load chats: $e');
    }
  }

  Future<void> _loadMessages() async {
    if (_selectedChatId == null) return;
    
    try {
      final response = await http.get(
        Uri.parse('http://localhost:5050/api/telegram/messages?chat_id=$_selectedChatId'),
      );
      
      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        setState(() => _messages = List<Map<String, dynamic>>.from(result['messages'] ?? []));
      }
    } catch (e) {
      print('Failed to load messages: $e');
    }
  }

  Future<void> _sendMessage() async {
    final message = _messageController.text.trim();
    final chatId = _selectedChatId ?? _chatIdController.text.trim();
    
    if (message.isEmpty || chatId.isEmpty) return;

    setState(() => _isLoading = true);
    
    try {
      final response = await http.post(
        Uri.parse('http://localhost:5050/api/telegram/send-message'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'chat_id': chatId,
          'message': message,
          'bot_name': _selectedBot,
        }),
      );

      if (response.statusCode == 200) {
        _messageController.clear();
        _showSuccess('Message sent!');
        if (_selectedChatId != null) _loadMessages();
      }
    } catch (e) {
      _showError('Failed to send message: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  String _formatTime(dynamic timestamp) {
    if (timestamp == null) return '';
    try {
      DateTime dateTime = DateTime.parse(timestamp);
      return '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return '';
    }
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.green),
    );
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }
}

enum AuthStep {
  phoneInput,
  codeVerification,
  twoFactorAuth,
  success,
}