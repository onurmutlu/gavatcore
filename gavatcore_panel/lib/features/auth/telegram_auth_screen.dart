import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers/auth_provider.dart';
import '../../core/services/telegram_service.dart';
import '../../core/models/user.dart';
import '../../shared/widgets/glass_container.dart';

class TelegramAuthScreen extends ConsumerStatefulWidget {
  const TelegramAuthScreen({super.key});

  @override
  ConsumerState<TelegramAuthScreen> createState() => _TelegramAuthScreenState();
}

class _TelegramAuthScreenState extends ConsumerState<TelegramAuthScreen> {
  final _codeController = TextEditingController();
  final _twoFactorController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  
  AuthStep _currentStep = AuthStep.botSelection;
  bool _isLoading = false;
  String? _errorMessage;
  String? _phoneCodeHash;
  String? _sessionId;
  bool _needsTwoFactor = false;
  
  List<Map<String, dynamic>> _availableBots = [];
  String? _selectedBotName;
  Map<String, dynamic>? _selectedBot;

  @override
  void initState() {
    super.initState();
    _loadAvailableBots();
  }

  @override
  void dispose() {
    _codeController.dispose();
    _twoFactorController.dispose();
    super.dispose();
  }

  Future<void> _loadAvailableBots() async {
    setState(() => _isLoading = true);
    
    try {
      final telegramService = TelegramService();
      final bots = await telegramService.getAvailableBots();
      
      setState(() {
        _availableBots = bots;
        // Set default bot selection to first available bot
        if (bots.isNotEmpty && _selectedBotName == null) {
          _selectedBotName = bots.first['name'];
          _selectedBot = bots.first;
        }
        _isLoading = false;
      });
      
      // Check if any bot already has a session
      for (final bot in bots) {
        if (bot['session_exists'] == true) {
          final hasValidSession = await telegramService.checkExistingSession(
            botName: bot['name']
          );
          if (hasValidSession) {
            final user = await telegramService.getCurrentUser();
            if (user != null) {
              ref.read(authProvider.notifier).login(user);
              if (mounted) {
                Navigator.of(context).pushReplacementNamed('/dashboard');
              }
              return;
            }
          }
        }
      }
    } catch (e) {
      _setError('Failed to load bots: $e');
    }
  }

  Future<void> _sendCode() async {
    if (_selectedBotName == null) {
      _setError('Please select a bot first');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final telegramService = TelegramService();
      final result = await telegramService.sendCode(_selectedBotName!);
      
      setState(() {
        _phoneCodeHash = result['phone_code_hash'];
        _sessionId = result['session_id'];
        _currentStep = AuthStep.codeVerification;
        _isLoading = false;
      });
      
      _showSuccessMessage('Verification code sent to ${result['phone']}');
    } catch (e) {
      _setError('Failed to send code: $e');
    }
  }

  Future<void> _verifyCode() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final telegramService = TelegramService();
      final result = await telegramService.verifyCode(
        _codeController.text.trim(),
        _phoneCodeHash!,
        _sessionId!,
      );

      if (result['needs_password'] == true) {
        setState(() {
          _needsTwoFactor = true;
          _currentStep = AuthStep.twoFactorAuth;
          _isLoading = false;
        });
        return;
      }

      final user = User.fromJson(result['user']);
      await ref.read(authProvider.notifier).login(user);
      
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/dashboard');
      }
    } catch (e) {
      _setError('Code verification failed: $e');
    }
  }

  Future<void> _verifyTwoFactor() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final telegramService = TelegramService();
      final result = await telegramService.verifyTwoFactor(
        _twoFactorController.text.trim(),
        _sessionId!,
      );

      final user = User.fromJson(result['user']);
      await ref.read(authProvider.notifier).login(user);
      
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/dashboard');
      }
    } catch (e) {
      _setError('Two-factor authentication failed: $e');
    }
  }

  void _setError(String message) {
    setState(() {
      _errorMessage = message;
      _isLoading = false;
    });
  }

  void _showSuccessMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  void _goBack() {
    if (_currentStep == AuthStep.twoFactorAuth) {
      setState(() => _currentStep = AuthStep.codeVerification);
    } else if (_currentStep == AuthStep.codeVerification) {
      setState(() => _currentStep = AuthStep.botSelection);
    }
  }

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
              child: GlassContainer(
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Form(
                    key: _formKey,
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
                        if (_currentStep != AuthStep.botSelection) ...[
                          TextButton(
                            onPressed: _goBack,
                            child: const Text(
                              'Go Back',
                              style: TextStyle(color: Colors.grey),
                            ),
                          ),
                        ],
                      ],
                    ),
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
      case AuthStep.botSelection:
        title = 'Select Telegram Bot';
        subtitle = 'Choose which bot to authenticate';
        break;
      case AuthStep.codeVerification:
        title = 'Enter Verification Code';
        subtitle = 'Check your Telegram for the code';
        break;
      case AuthStep.twoFactorAuth:
        title = 'Two-Factor Authentication';
        subtitle = 'Enter your 2FA password';
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
      case AuthStep.botSelection:
        return _buildBotSelection();
      case AuthStep.codeVerification:
        return _buildCodeInput();
      case AuthStep.twoFactorAuth:
        return _buildTwoFactorInput();
    }
  }

  Widget _buildBotSelection() {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey.withOpacity(0.3)),
            borderRadius: BorderRadius.circular(12),
          ),
          child: DropdownButtonFormField<String>(
            value: _selectedBotName,
            style: const TextStyle(color: Colors.white),
            dropdownColor: const Color(0xFF1A1A1F),
            decoration: const InputDecoration(
              labelText: 'Select Bot',
              border: InputBorder.none,
              prefixIcon: Icon(Icons.smart_toy, color: Colors.purple),
            ),
            items: _availableBots.map((bot) {
              return DropdownMenuItem<String>(
                value: bot['name'],
                child: Row(
                  children: [
                    Icon(
                      bot['session_exists'] ? Icons.check_circle : Icons.circle,
                      color: bot['session_exists'] ? Colors.green : Colors.grey,
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            bot['display_name'] ?? bot['name'],
                            style: const TextStyle(color: Colors.white, fontSize: 14),
                          ),
                          Text(
                            bot['phone'] ?? '',
                            style: TextStyle(
                              color: Colors.grey[400],
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
            onChanged: (value) {
              setState(() {
                _selectedBotName = value;
                _selectedBot = _availableBots.firstWhere(
                  (bot) => bot['name'] == value,
                );
              });
            },
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please select a bot';
              }
              return null;
            },
          ),
        ),
        if (_selectedBot != null) ..[
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.purple.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.purple.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                Icon(
                  _selectedBot!['session_exists'] ? Icons.info : Icons.warning,
                  color: _selectedBot!['session_exists'] ? Colors.blue : Colors.orange,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _selectedBot!['session_exists']
                        ? 'Bot already authenticated - will re-authenticate'
                        : 'Bot needs authentication - SMS code will be sent to ${_selectedBot!['phone']}',
                    style: TextStyle(
                      color: Colors.grey[300],
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
        const SizedBox(height: 24),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: _selectedBotName != null ? _sendCode : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.purple,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Text(
              'Send Code',
              style: TextStyle(fontSize: 16, color: Colors.white),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCodeInput() {
    return Column(
      children: [
        TextFormField(
          controller: _codeController,
          keyboardType: TextInputType.number,
          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
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
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'Please enter the verification code';
            }
            if (value.length < 5) {
              return 'Verification code must be at least 5 digits';
            }
            return null;
          },
        ),
        const SizedBox(height: 24),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: _verifyCode,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.purple,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Text(
              'Verify Code',
              style: TextStyle(fontSize: 16, color: Colors.white),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildTwoFactorInput() {
    return Column(
      children: [
        TextFormField(
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
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'Please enter your 2FA password';
            }
            return null;
          },
        ),
        const SizedBox(height: 24),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: _verifyTwoFactor,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.purple,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Text(
              'Authenticate',
              style: TextStyle(fontSize: 16, color: Colors.white),
            ),
          ),
        ),
      ],
    );
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
}

enum AuthStep {
  botSelection,
  codeVerification,
  twoFactorAuth,
}