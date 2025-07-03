import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/glass_container.dart';
import '../../../core/models/app_state.dart';
import '../providers/message_pools_providers.dart';

class MessagePoolsScreen extends ConsumerStatefulWidget {
  const MessagePoolsScreen({super.key});

  @override
  ConsumerState<MessagePoolsScreen> createState() => _MessagePoolsScreenState();
}

class _MessagePoolsScreenState extends ConsumerState<MessagePoolsScreen> {
  final _searchController = TextEditingController();
  String _selectedFilter = 'all';
  
  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final messages = ref.watch(messagePoolsProvider);
    final filteredMessages = ref.watch(filteredMessagesProvider(_selectedFilter));
    
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          _buildHeader(),
          
          const SizedBox(height: 24),
          
          // Filters and search
          _buildFiltersSection(),
          
          const SizedBox(height: 24),
          
          // Messages list
          Expanded(
            child: _buildMessagesList(filteredMessages),
          ),
          
          const SizedBox(height: 100), // Bottom navigation space
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Mesaj Havuzları',
            style: NeonTextStyles.neonTitle,
          ),
          const SizedBox(height: 8),
          Text(
            'AI destekli mesajları yönet ve düzenle',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 20),
          
          // Search and Filter Row
          Row(
            children: [
              // Search Bar
              Expanded(
                flex: 3,
                child: GlassContainer(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: TextField(
                    onChanged: (value) {
                      // TODO: Implement search functionality
                      ref.read(searchQueryProvider.notifier).state = value;
                    },
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Mesajlarda ara...',
                      hintStyle: TextStyle(color: Colors.white54),
                      prefixIcon: Icon(
                        Icons.search,
                        color: AppTheme.neonColors.blue,
                      ),
                      border: InputBorder.none,
                      suffixIcon: IconButton(
                        icon: Icon(
                          Icons.clear,
                          color: Colors.white54,
                        ),
                        onPressed: () {
                          // Clear search
                          ref.read(searchQueryProvider.notifier).state = '';
                        },
                      ),
                    ),
                  ),
                ),
              ),
              
              const SizedBox(width: 16),
              
              // Filter Dropdown
              Expanded(
                flex: 1,
                child: GlassContainer(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: ref.watch(statusFilterProvider),
                      hint: Text(
                        'Status Filtre',
                        style: TextStyle(color: Colors.white54),
                      ),
                      dropdownColor: const Color(0xFF1A1A2E),
                      style: const TextStyle(color: Colors.white),
                      items: ['all', 'pending', 'sent', 'failed'].map((status) {
                        return DropdownMenuItem(
                          value: status,
                          child: Text(_getStatusText(status)),
                        );
                      }).toList(),
                      onChanged: (value) {
                        if (value != null) {
                          ref.read(statusFilterProvider.notifier).state = value;
                        }
                      },
                    ),
                  ),
                ),
              ),
              
              const SizedBox(width: 16),
              
              // Add Message Button
              AnimatedGlassContainer(
                padding: const EdgeInsets.all(12),
                onTap: () => _showAddMessageDialog(),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.add,
                      color: AppTheme.neonColors.green,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Yeni Mesaj',
                      style: TextStyle(
                        color: AppTheme.neonColors.green,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Statistics Row
          Row(
            children: [
              _buildStatChip(
                'Toplam: ${_getFilteredMessages().length}',
                AppTheme.neonColors.blue,
              ),
              const SizedBox(width: 12),
              _buildStatChip(
                'Bekleyen: ${_getFilteredMessages().where((m) => m.status == 'pending').length}',
                AppTheme.neonColors.yellow,
              ),
              const SizedBox(width: 12),
              _buildStatChip(
                'Gönderilen: ${_getFilteredMessages().where((m) => m.status == 'sent').length}',
                AppTheme.neonColors.green,
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildStatChip(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.5), width: 1),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
  
  List<MessageData> _getFilteredMessages() {
    final messages = ref.watch(messagesProvider).valueOrNull ?? [];
    final searchQuery = ref.watch(searchQueryProvider).toLowerCase();
    final statusFilter = ref.watch(statusFilterProvider);
    
    return messages.where((message) {
      final matchesSearch = searchQuery.isEmpty ||
          message.content.toLowerCase().contains(searchQuery) ||
          message.botId.toLowerCase().contains(searchQuery);
      
      final matchesStatus = statusFilter == 'all' || message.status == statusFilter;
      
      return matchesSearch && matchesStatus;
    }).toList();
  }
  
  String _getStatusText(String status) {
    switch (status) {
      case 'all': return 'Tümü';
      case 'pending': return 'Bekleyen';
      case 'sent': return 'Gönderilen';
      case 'failed': return 'Başarısız';
      default: return status;
    }
  }

  Widget _buildFiltersSection() {
    return Row(
      children: [
        // Search bar
        Expanded(
          flex: 2,
          child: GlassContainer(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: TextField(
              controller: _searchController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'Search messages...',
                hintStyle: TextStyle(color: Colors.white60),
                border: InputBorder.none,
                prefixIcon: Icon(
                  Icons.search,
                  color: AppTheme.neonColors.blue,
                ),
              ),
              onChanged: (value) {
                ref.read(searchQueryProvider.notifier).setQuery(value);
              },
            ),
          ),
        ),
        
        const SizedBox(width: 16),
        
        // Status filter
        Expanded(
          child: GlassContainer(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: DropdownButton<String>(
              value: _selectedFilter,
              isExpanded: true,
              dropdownColor: const Color(0xFF1A1A2E),
              style: const TextStyle(color: Colors.white),
              underline: Container(),
              icon: Icon(
                Icons.filter_list,
                color: AppTheme.neonColors.purple,
              ),
              items: [
                DropdownMenuItem(value: 'all', child: Text('All Messages')),
                DropdownMenuItem(value: 'pending', child: Text('Pending')),
                DropdownMenuItem(value: 'sent', child: Text('Sent')),
                DropdownMenuItem(value: 'failed', child: Text('Failed')),
                DropdownMenuItem(value: 'ai_enhanced', child: Text('AI Enhanced')),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    _selectedFilter = value;
                  });
                }
              },
            ),
          ),
        ),
        
        const SizedBox(width: 16),
        
        // Refresh button
        AnimatedGlassContainer(
          width: 48,
          height: 48,
          onTap: () => ref.refresh(messagePoolsProvider),
          child: Icon(
            Icons.refresh,
            color: AppTheme.neonColors.blue,
          ),
        ),
      ],
    ).animate().slideX(begin: -0.3, duration: 500.ms);
  }

  Widget _buildMessagesList(AsyncValue<List<MessageData>> messages) {
    return messages.when(
      data: (messageList) {
        if (messageList.isEmpty) {
          return _buildEmptyState();
        }
        
        return ListView.builder(
          itemCount: messageList.length,
          itemBuilder: (context, index) {
            final message = messageList[index];
            return _buildMessageCard(message, index);
          },
        );
      },
      loading: () => _buildLoadingState(),
      error: (error, stack) => _buildErrorState(error.toString()),
    );
  }

  Widget _buildMessageCard(MessageData message, int index) {
    final statusColor = _getStatusColor(message.status);
    
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: GlassContainer(
        padding: const EdgeInsets.all(20),
        isNeonBorder: message.status == 'failed',
        borderColor: message.status == 'failed' ? AppTheme.neonColors.red : null,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header row
            Row(
              children: [
                // Status indicator
                Container(
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    color: statusColor,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: statusColor.withOpacity(0.3),
                        blurRadius: 8,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(width: 12),
                
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        message.targetEntity,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Text(
                        message.sessionName,
                        style: TextStyle(
                          color: Colors.white60,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
                
                // AI Enhanced badge
                if (message.aiEnhanced)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      gradient: AppTheme.primaryGradient,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.auto_awesome,
                          size: 12,
                          color: Colors.white,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          'AI',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                
                const SizedBox(width: 12),
                
                // Actions
                PopupMenuButton<String>(
                  icon: Icon(Icons.more_vert, color: Colors.white60),
                  color: const Color(0xFF1A1A2E),
                  itemBuilder: (context) => [
                    PopupMenuItem(
                      value: 'edit',
                      child: Row(
                        children: [
                          Icon(Icons.edit, color: AppTheme.neonColors.blue, size: 16),
                          const SizedBox(width: 8),
                          Text('Edit', style: TextStyle(color: Colors.white)),
                        ],
                      ),
                    ),
                    PopupMenuItem(
                      value: 'duplicate',
                      child: Row(
                        children: [
                          Icon(Icons.copy, color: AppTheme.neonColors.green, size: 16),
                          const SizedBox(width: 8),
                          Text('Duplicate', style: TextStyle(color: Colors.white)),
                        ],
                      ),
                    ),
                    PopupMenuItem(
                      value: 'delete',
                      child: Row(
                        children: [
                          Icon(Icons.delete, color: AppTheme.neonColors.red, size: 16),
                          const SizedBox(width: 8),
                          Text('Delete', style: TextStyle(color: Colors.white)),
                        ],
                      ),
                    ),
                  ],
                  onSelected: (action) => _handleMessageAction(action, message),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Message content
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.05),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: Colors.white.withOpacity(0.1),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Original:',
                    style: TextStyle(
                      color: Colors.white60,
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    message.content,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                    ),
                  ),
                  
                  if (message.enhancedContent != null) ...[
                    const SizedBox(height: 12),
                    Divider(color: Colors.white.withOpacity(0.1)),
                    const SizedBox(height: 8),
                    Text(
                      'AI Enhanced:',
                      style: TextStyle(
                        color: AppTheme.neonColors.purple,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      message.enhancedContent!,
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            
            const SizedBox(height: 12),
            
            // Footer
            Row(
              children: [
                Icon(
                  Icons.access_time,
                  size: 14,
                  color: Colors.white60,
                ),
                const SizedBox(width: 4),
                Text(
                  _formatDateTime(message.createdAt),
                  style: TextStyle(
                    color: Colors.white60,
                    fontSize: 12,
                  ),
                ),
                
                const Spacer(),
                
                Text(
                  message.status.toUpperCase(),
                  style: TextStyle(
                    color: statusColor,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ],
        ),
      ).animate(delay: (index * 100).ms).slideY(begin: 0.3),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: GlassContainer(
        width: 300,
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.message_outlined,
              size: 64,
              color: Colors.white30,
            ),
            
            const SizedBox(height: 16),
            
            Text(
              'No Messages Found',
              style: NeonTextStyles.neonSubtitle.copyWith(
                color: Colors.white60,
              ),
            ),
            
            const SizedBox(height: 8),
            
            Text(
              'Create your first message to get started',
              style: TextStyle(
                color: Colors.white40,
                fontSize: 14,
              ),
              textAlign: TextAlign.center,
            ),
            
            const SizedBox(height: 24),
            
            ElevatedButton.icon(
              onPressed: () => _showAddMessageDialog(),
              icon: Icon(Icons.add),
              label: Text('Add Message'),
            ),
          ],
        ),
      ).animate().scale(duration: 600.ms),
    );
  }

  Widget _buildLoadingState() {
    return ListView.builder(
      itemCount: 5,
      itemBuilder: (context, index) => Padding(
        padding: const EdgeInsets.only(bottom: 16),
        child: GlassContainer(
          height: 150,
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              Row(
                children: [
                  Container(
                    width: 12,
                    height: 12,
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.1),
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Container(
                      height: 16,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Container(
                width: double.infinity,
                height: 60,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ],
          ),
        ).animate(onPlay: (controller) => controller.repeat())
            .shimmer(duration: 1.5.seconds),
      ),
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: GlassContainer(
        width: 300,
        padding: const EdgeInsets.all(32),
        borderColor: AppTheme.neonColors.red,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: AppTheme.neonColors.red,
            ),
            
            const SizedBox(height: 16),
            
            Text(
              'Error Loading Messages',
              style: NeonTextStyles.neonSubtitle.copyWith(
                color: AppTheme.neonColors.red,
              ),
            ),
            
            const SizedBox(height: 8),
            
            Text(
              error,
              style: TextStyle(
                color: Colors.white60,
                fontSize: 12,
              ),
              textAlign: TextAlign.center,
            ),
            
            const SizedBox(height: 24),
            
            ElevatedButton.icon(
              onPressed: () => ref.refresh(messagePoolsProvider),
              icon: Icon(Icons.refresh),
              label: Text('Retry'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.neonColors.red,
              ),
            ),
          ],
        ),
      ).animate().scale(duration: 600.ms),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'pending':
        return AppTheme.neonColors.yellow;
      case 'sent':
        return AppTheme.neonColors.green;
      case 'failed':
        return AppTheme.neonColors.red;
      default:
        return AppTheme.neonColors.blue;
    }
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }

  void _handleMessageAction(String action, MessageData message) {
    switch (action) {
      case 'edit':
        _showEditMessageDialog(message);
        break;
      case 'duplicate':
        _duplicateMessage(message);
        break;
      case 'delete':
        _deleteMessage(message);
        break;
    }
  }

  void _showAddMessageDialog() {
    showDialog(
      context: context,
      builder: (context) => _MessageDialog(),
    );
  }

  void _showEditMessageDialog(MessageData message) {
    showDialog(
      context: context,
      builder: (context) => _MessageDialog(message: message),
    );
  }

  void _duplicateMessage(MessageData message) {
    ref.read(messagePoolsProvider.notifier).duplicateMessage(message);
  }

  void _deleteMessage(MessageData message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A2E),
        title: Text('Delete Message', style: TextStyle(color: Colors.white)),
        content: Text(
          'Are you sure you want to delete this message?',
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              ref.read(messagePoolsProvider.notifier).deleteMessage(message.id);
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.neonColors.red,
            ),
            child: Text('Delete'),
          ),
        ],
      ),
    );
  }
}

// Message Dialog Widget
class _MessageDialog extends ConsumerStatefulWidget {
  final MessageData? message;
  
  const _MessageDialog({this.message});

  @override
  ConsumerState<_MessageDialog> createState() => _MessageDialogState();
}

class _MessageDialogState extends ConsumerState<_MessageDialog> {
  late final TextEditingController _contentController;
  late final TextEditingController _targetController;
  late String _selectedSession;
  late String _messageType;
  late bool _aiEnhanced;

  @override
  void initState() {
    super.initState();
    
    _contentController = TextEditingController(
      text: widget.message?.content ?? '',
    );
    _targetController = TextEditingController(
      text: widget.message?.targetEntity ?? '',
    );
    _selectedSession = widget.message?.sessionName ?? 'yayincilara';
    _messageType = widget.message?.messageType ?? 'text';
    _aiEnhanced = widget.message?.aiEnhanced ?? true;
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.transparent,
      child: GlassContainer(
        width: 500,
        padding: const EdgeInsets.all(24),
        isNeonBorder: true,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.message != null ? 'Edit Message' : 'New Message',
              style: NeonTextStyles.neonTitle,
            ),
            
            const SizedBox(height: 24),
            
            // Target Entity
            TextField(
              controller: _targetController,
              style: TextStyle(color: Colors.white),
              decoration: InputDecoration(
                labelText: 'Target Entity',
                hintText: '@channel or user ID',
                prefixIcon: Icon(Icons.target, color: AppTheme.neonColors.blue),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Session Selection
            DropdownButtonFormField<String>(
              value: _selectedSession,
              decoration: InputDecoration(
                labelText: 'Bot Session',
                prefixIcon: Icon(Icons.smart_toy, color: AppTheme.neonColors.green),
              ),
              dropdownColor: const Color(0xFF1A1A2E),
              style: TextStyle(color: Colors.white),
              items: [
                DropdownMenuItem(value: 'yayincilara', child: Text('Yayıncılara')),
                DropdownMenuItem(value: 'xxxgeisha', child: Text('XXXGeisha')),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    _selectedSession = value;
                  });
                }
              },
            ),
            
            const SizedBox(height: 16),
            
            // Message Content
            TextField(
              controller: _contentController,
              style: TextStyle(color: Colors.white),
              maxLines: 4,
              decoration: InputDecoration(
                labelText: 'Message Content',
                hintText: 'Enter your message...',
                prefixIcon: Icon(Icons.message, color: AppTheme.neonColors.purple),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Options
            Row(
              children: [
                Expanded(
                  child: CheckboxListTile(
                    title: Text('AI Enhanced', style: TextStyle(color: Colors.white)),
                    value: _aiEnhanced,
                    onChanged: (value) {
                      setState(() {
                        _aiEnhanced = value ?? false;
                      });
                    },
                    activeColor: AppTheme.neonColors.purple,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 24),
            
            // Actions
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text('Cancel'),
                ),
                
                const SizedBox(width: 16),
                
                ElevatedButton(
                  onPressed: _saveMessage,
                  child: Text(widget.message != null ? 'Update' : 'Create'),
                ),
              ],
            ),
          ],
        ),
      ).animate().scale(duration: 300.ms),
    );
  }

  void _saveMessage() {
    if (_contentController.text.isEmpty || _targetController.text.isEmpty) {
      return;
    }

    final messageData = {
      'content': _contentController.text,
      'targetEntity': _targetController.text,
      'sessionName': _selectedSession,
      'messageType': _messageType,
      'aiEnhanced': _aiEnhanced,
    };

    if (widget.message != null) {
      ref.read(messagePoolsProvider.notifier).updateMessage(
        widget.message!.id,
        messageData,
      );
    } else {
      ref.read(messagePoolsProvider.notifier).addMessage(messageData);
    }

    Navigator.pop(context);
  }

  @override
  void dispose() {
    _contentController.dispose();
    _targetController.dispose();
    super.dispose();
  }
} 