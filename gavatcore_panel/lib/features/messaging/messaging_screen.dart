import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/services/telegram_service.dart';
import '../../shared/widgets/glass_container.dart';

class MessagingScreen extends ConsumerStatefulWidget {
  const MessagingScreen({super.key});

  @override
  ConsumerState<MessagingScreen> createState() => _MessagingScreenState();
}

class _MessagingScreenState extends ConsumerState<MessagingScreen>
    with TickerProviderStateMixin {
  final _messageController = TextEditingController();
  final _chatIdController = TextEditingController();
  
  List<Map<String, dynamic>> _chats = [];
  List<Map<String, dynamic>> _messages = [];
  String? _selectedChatId;
  String? _selectedBotName = 'lara';
  bool _isLoading = false;
  bool _isLoadingChats = false;
  bool _isLoadingMessages = false;
  
  final List<String> _availableBots = ['lara', 'babagavat', 'geisha'];
  
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadChats();
  }

  @override
  void dispose() {
    _messageController.dispose();
    _chatIdController.dispose();
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadChats() async {
    setState(() => _isLoadingChats = true);
    
    try {
      final telegramService = TelegramService();
      final chats = await telegramService.getChats();
      setState(() => _chats = chats);
    } catch (e) {
      _showError('Failed to load chats: $e');
    } finally {
      setState(() => _isLoadingChats = false);
    }
  }

  Future<void> _loadMessages() async {
    if (_selectedChatId == null) return;
    
    setState(() => _isLoadingMessages = true);
    
    try {
      final telegramService = TelegramService();
      final messages = await telegramService.getMessages(chatId: _selectedChatId);
      setState(() => _messages = messages);
    } catch (e) {
      _showError('Failed to load messages: $e');
    } finally {
      setState(() => _isLoadingMessages = false);
    }
  }

  Future<void> _sendMessage() async {
    final message = _messageController.text.trim();
    final chatId = _selectedChatId ?? _chatIdController.text.trim();
    
    if (message.isEmpty || chatId.isEmpty) {
      _showError('Please enter both message and chat ID');
      return;
    }

    setState(() => _isLoading = true);
    
    try {
      final telegramService = TelegramService();
      await telegramService.sendMessage(
        chatId: chatId,
        message: message,
        botName: _selectedBotName,
      );
      
      _messageController.clear();
      _showSuccess('Message sent successfully!');
      
      if (_selectedChatId != null) {
        await _loadMessages();
      }
    } catch (e) {
      _showError('Failed to send message: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _enableAutomation() async {
    try {
      _showSuccess('Message automation enabled for $_selectedBotName');
    } catch (e) {
      _showError('Failed to enable automation: $e');
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        duration: const Duration(seconds: 4),
      ),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        title: const Text(
          'Telegram Messaging',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF1A1A2E),
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.purple,
          unselectedLabelColor: Colors.grey,
          indicatorColor: Colors.purple,
          tabs: const [
            Tab(text: 'Send Messages'),
            Tab(text: 'Automation'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildMessagingTab(),
          _buildAutomationTab(),
        ],
      ),
    );
  }

  Widget _buildMessagingTab() {
    return Row(
      children: [
        // Chat List Sidebar
        Container(
          width: 300,
          decoration: const BoxDecoration(
            border: Border(right: BorderSide(color: Colors.grey, width: 0.5)),
          ),
          child: _buildChatList(),
        ),
        // Message Area
        Expanded(child: _buildMessageArea()),
      ],
    );
  }

  Widget _buildChatList() {
    return Column(
      children: [
        // Header
        Container(
          padding: const EdgeInsets.all(16),
          decoration: const BoxDecoration(
            border: Border(bottom: BorderSide(color: Colors.grey, width: 0.5)),
          ),
          child: Row(
            children: [
              const Text(
                'Chats',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const Spacer(),
              IconButton(
                onPressed: _loadChats,
                icon: _isLoadingChats
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.purple,
                        ),
                      )
                    : const Icon(Icons.refresh, color: Colors.purple),
              ),
            ],
          ),
        ),
        // Chat List
        Expanded(
          child: _isLoadingChats
              ? const Center(
                  child: CircularProgressIndicator(color: Colors.purple),
                )
              : ListView.builder(
                  itemCount: _chats.length,
                  itemBuilder: (context, index) {
                    final chat = _chats[index];
                    final isSelected = _selectedChatId == chat['id'];
                    
                    return ListTile(
                      selected: isSelected,
                      selectedTileColor: Colors.purple.withOpacity(0.2),
                      title: Text(
                        chat['title'] ?? chat['first_name'] ?? 'Unknown',
                        style: const TextStyle(color: Colors.white),
                      ),
                      subtitle: Text(
                        'ID: ${chat['id']}',
                        style: TextStyle(color: Colors.grey[400], fontSize: 12),
                      ),
                      leading: CircleAvatar(
                        backgroundColor: Colors.purple,
                        child: Text(
                          (chat['title'] ?? chat['first_name'] ?? 'U')[0],
                          style: const TextStyle(color: Colors.white),
                        ),
                      ),
                      onTap: () {
                        setState(() => _selectedChatId = chat['id']);
                        _loadMessages();
                      },
                    );
                  },
                ),
        ),
      ],
    );
  }

  Widget _buildMessageArea() {
    return Column(
      children: [
        // Messages
        Expanded(
          child: _selectedChatId == null
              ? const Center(
                  child: Text(
                    'Select a chat to view messages',
                    style: TextStyle(color: Colors.grey, fontSize: 16),
                  ),
                )
              : _isLoadingMessages
                  ? const Center(
                      child: CircularProgressIndicator(color: Colors.purple),
                    )
                  : ListView.builder(
                      reverse: true,
                      itemCount: _messages.length,
                      itemBuilder: (context, index) {
                        final message = _messages[_messages.length - 1 - index];
                        return _buildMessageBubble(message);
                      },
                    ),
        ),
        // Message Input
        _buildMessageInput(),
      ],
    );
  }

  Widget _buildMessageBubble(Map<String, dynamic> message) {
    final isOutgoing = message['from_bot'] == true;
    
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Row(
        mainAxisAlignment:
            isOutgoing ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          if (!isOutgoing) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.grey,
              child: Text(
                (message['from_name'] ?? 'U')[0],
                style: const TextStyle(color: Colors.white, fontSize: 12),
              ),
            ),
            const SizedBox(width: 8),
          ],
          Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.4,
            ),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: isOutgoing ? Colors.purple : Colors.grey[800],
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  message['text'] ?? '',
                  style: const TextStyle(color: Colors.white),
                ),
                const SizedBox(height: 4),
                Text(
                  _formatTime(message['date']),
                  style: TextStyle(
                    color: Colors.grey[400],
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          if (isOutgoing) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.purple,
              child: Text(
                (_selectedBotName ?? 'B')[0].toUpperCase(),
                style: const TextStyle(color: Colors.white, fontSize: 12),
              ),
            ),
          ],
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
          // Bot Selector
          Row(
            children: [
              const Text(
                'Bot:',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
              ),
              const SizedBox(width: 8),
              DropdownButton<String>(
                value: _selectedBotName,
                dropdownColor: const Color(0xFF1A1A2E),
                style: const TextStyle(color: Colors.white),
                items: _availableBots.map((bot) {
                  return DropdownMenuItem(
                    value: bot,
                    child: Text(bot.toUpperCase()),
                  );
                }).toList(),
                onChanged: (value) => setState(() => _selectedBotName = value),
              ),
            ],
          ),
          const SizedBox(height: 12),
          // Manual Chat ID Input (if no chat selected)
          if (_selectedChatId == null) ...[
            TextFormField(
              controller: _chatIdController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                labelText: 'Chat ID',
                hintText: 'Enter chat ID manually',
                prefixIcon: const Icon(Icons.chat, color: Colors.purple),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: Colors.purple),
                ),
              ),
            ),
            const SizedBox(height: 12),
          ],
          // Message Input
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: _messageController,
                  maxLines: null,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    hintText: 'Type your message...',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(25),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(25),
                      borderSide: const BorderSide(color: Colors.purple),
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 12,
                    ),
                  ),
                  onFieldSubmitted: (_) => _sendMessage(),
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
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.send, color: Colors.white),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAutomationTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Message Automation',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Configure automated messaging for your bots',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[400],
            ),
          ),
          const SizedBox(height: 32),
          _buildAutomationCard(
            'Auto-Reply',
            'Automatically respond to incoming messages',
            Icons.reply_all,
            () => _enableAutomation(),
          ),
          const SizedBox(height: 16),
          _buildAutomationCard(
            'Scheduled Messages',
            'Send messages at specific times',
            Icons.schedule,
            () => _enableAutomation(),
          ),
          const SizedBox(height: 16),
          _buildAutomationCard(
            'Mass Messaging',
            'Send messages to multiple chats',
            Icons.broadcast_on_personal,
            () => _enableAutomation(),
          ),
          const SizedBox(height: 16),
          _buildAutomationCard(
            'AI Enhancement',
            'Use AI to enhance message content',
            Icons.auto_awesome,
            () => _enableAutomation(),
          ),
        ],
      ),
    );
  }

  Widget _buildAutomationCard(
    String title,
    String description,
    IconData icon,
    VoidCallback onTap,
  ) {
    return GlassContainer(
      child: ListTile(
        leading: Icon(icon, color: Colors.purple, size: 32),
        title: Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        subtitle: Text(
          description,
          style: TextStyle(color: Colors.grey[400]),
        ),
        trailing: const Icon(Icons.arrow_forward_ios, color: Colors.purple),
        onTap: onTap,
      ),
    );
  }

  String _formatTime(dynamic timestamp) {
    if (timestamp == null) return '';
    
    try {
      DateTime dateTime;
      if (timestamp is int) {
        dateTime = DateTime.fromMillisecondsSinceEpoch(timestamp * 1000);
      } else if (timestamp is String) {
        dateTime = DateTime.parse(timestamp);
      } else {
        return '';
      }
      
      return '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return '';
    }
  }
}