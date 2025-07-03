import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:uuid/uuid.dart';
import '../../../core/models/app_state.dart';
import '../../../core/services/api_service.dart';

part 'message_pools_providers.g.dart';

// Search and Filter Providers
final searchQueryProvider = StateProvider<String>((ref) => '');
final statusFilterProvider = StateProvider<String>((ref) => 'all');
final botFilterProvider = StateProvider<String>((ref) => 'all');
final enhancementTypeFilterProvider = StateProvider<String>((ref) => 'all');

// Pagination Provider
final currentPageProvider = StateProvider<int>((ref) => 1);
final itemsPerPageProvider = StateProvider<int>((ref) => 20);

// Selected Messages Provider (for bulk operations)
final selectedMessagesProvider = StateProvider<Set<String>>((ref) => {});

// Message Pools Data Provider
@riverpod
Future<List<MessageData>> messagePoolsData(MessagePoolsDataRef ref) async {
  final api = ref.read(apiServiceProvider);
  final page = ref.watch(currentPageProvider);
  final limit = ref.watch(itemsPerPageProvider);
  
  try {
    return await api.getMessages(page: page, limit: limit);
  } catch (e) {
    // Return mock data on error
    await Future.delayed(const Duration(milliseconds: 300));
    return _getMockMessages();
  }
}

// Filtered Messages Provider
@riverpod
List<MessageData> filteredMessages(FilteredMessagesRef ref) {
  final messages = ref.watch(messagePoolsDataProvider).valueOrNull ?? [];
  final searchQuery = ref.watch(searchQueryProvider).toLowerCase();
  final statusFilter = ref.watch(statusFilterProvider);
  final botFilter = ref.watch(botFilterProvider);
  final enhancementFilter = ref.watch(enhancementTypeFilterProvider);
  
  return messages.where((message) {
    final matchesSearch = searchQuery.isEmpty ||
        message.content.toLowerCase().contains(searchQuery) ||
        message.botId.toLowerCase().contains(searchQuery) ||
        (message.targetUserId?.toLowerCase().contains(searchQuery) ?? false);
    
    final matchesStatus = statusFilter == 'all' || message.status == statusFilter;
    final matchesBot = botFilter == 'all' || message.botId == botFilter;
    final matchesEnhancement = enhancementFilter == 'all' || 
        message.enhancementType == enhancementFilter;
    
    return matchesSearch && matchesStatus && matchesBot && matchesEnhancement;
  }).toList();
}

// Message Statistics Provider
@riverpod
Map<String, int> messageStats(MessageStatsRef ref) {
  final messages = ref.watch(messagePoolsDataProvider).valueOrNull ?? [];
  
  return {
    'total': messages.length,
    'pending': messages.where((m) => m.status == 'pending').length,
    'sent': messages.where((m) => m.status == 'sent').length,
    'failed': messages.where((m) => m.status == 'failed').length,
    'scheduled': messages.where((m) => m.isScheduled).length,
    'enhanced': messages.where((m) => m.enhancedContent != null).length,
  };
}

// Bot List Provider (for filter dropdown)
@riverpod
List<String> availableBots(AvailableBotsRef ref) {
  final messages = ref.watch(messagePoolsDataProvider).valueOrNull ?? [];
  final bots = messages.map((m) => m.botId).toSet().toList();
  bots.sort();
  return ['all', ...bots];
}

// Enhancement Types Provider (for filter dropdown)
@riverpod
List<String> availableEnhancementTypes(AvailableEnhancementTypesRef ref) {
  final messages = ref.watch(messagePoolsDataProvider).valueOrNull ?? [];
  final types = messages.map((m) => m.enhancementType).toSet().toList();
  types.sort();
  return ['all', ...types];
}

// Message Actions Provider
class MessageActionsNotifier extends StateNotifier<AsyncValue<void>> {
  MessageActionsNotifier(this.ref) : super(const AsyncValue.data(null));
  
  final Ref ref;
  
  Future<void> createMessage(Map<String, dynamic> messageData) async {
    state = const AsyncValue.loading();
    try {
      final api = ref.read(apiServiceProvider);
      await api.createMessage(messageData);
      
      // Refresh messages list
      ref.invalidate(messagePoolsDataProvider);
      
      state = const AsyncValue.data(null);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
  
  Future<void> updateMessage(String id, Map<String, dynamic> messageData) async {
    state = const AsyncValue.loading();
    try {
      final api = ref.read(apiServiceProvider);
      await api.updateMessage(id, messageData);
      
      // Refresh messages list
      ref.invalidate(messagePoolsDataProvider);
      
      state = const AsyncValue.data(null);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
  
  Future<void> deleteMessage(String id) async {
    state = const AsyncValue.loading();
    try {
      final api = ref.read(apiServiceProvider);
      await api.deleteMessage(id);
      
      // Refresh messages list
      ref.invalidate(messagePoolsDataProvider);
      
      state = const AsyncValue.data(null);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
  
  Future<void> bulkDeleteMessages(List<String> ids) async {
    state = const AsyncValue.loading();
    try {
      final api = ref.read(apiServiceProvider);
      
      // Delete all selected messages
      for (final id in ids) {
        await api.deleteMessage(id);
      }
      
      // Clear selection
      ref.read(selectedMessagesProvider.notifier).state = {};
      
      // Refresh messages list
      ref.invalidate(messagePoolsDataProvider);
      
      state = const AsyncValue.data(null);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
  
  void toggleMessageSelection(String messageId) {
    final currentSelection = ref.read(selectedMessagesProvider);
    final newSelection = Set<String>.from(currentSelection);
    
    if (newSelection.contains(messageId)) {
      newSelection.remove(messageId);
    } else {
      newSelection.add(messageId);
    }
    
    ref.read(selectedMessagesProvider.notifier).state = newSelection;
  }
  
  void selectAllFilteredMessages() {
    final filteredMessages = ref.read(filteredMessagesProvider);
    final allIds = filteredMessages.map((m) => m.id).toSet();
    ref.read(selectedMessagesProvider.notifier).state = allIds;
  }
  
  void clearSelection() {
    ref.read(selectedMessagesProvider.notifier).state = {};
  }
}

final messageActionsProvider = StateNotifierProvider<MessageActionsNotifier, AsyncValue<void>>(
  (ref) => MessageActionsNotifier(ref),
);

// Mock data helper
List<MessageData> _getMockMessages() {
  return [
    MessageData(
      id: '1',
      content: 'Selam tatlım, nasılsın bugün? 💋',
      originalContent: 'Merhaba, nasılsın?',
      enhancedContent: 'Selam tatlım, nasılsın bugün? 💋',
      status: 'sent',
      botId: 'lara',
      enhancementType: 'flirty',
      createdAt: DateTime.now().subtract(const Duration(minutes: 5)),
      sentAt: DateTime.now().subtract(const Duration(minutes: 4)),
      targetUserId: 'user123',
    ),
    MessageData(
      id: '2',
      content: 'Burada mısın yoksa uyuyor musun? 😴',
      originalContent: 'Burada mısın?',
      status: 'pending',
      botId: 'geisha',
      enhancementType: 'caring',
      isScheduled: true,
      scheduledAt: DateTime.now().add(const Duration(minutes: 10)),
      createdAt: DateTime.now().subtract(const Duration(minutes: 15)),
      targetUserId: 'user456',
    ),
    MessageData(
      id: '3',
      content: 'Heyyyy! Çok güzel bir gün değil mi? ✨🌟',
      originalContent: 'Güzel gün!',
      enhancedContent: 'Heyyyy! Çok güzel bir gün değil mi? ✨🌟',
      status: 'sent',
      botId: 'balkiz',
      enhancementType: 'bubbly',
      createdAt: DateTime.now().subtract(const Duration(hours: 1)),
      sentAt: DateTime.now().subtract(const Duration(minutes: 58)),
      targetUserId: 'user789',
    ),
    MessageData(
      id: '4',
      content: 'API hatası nedeniyle gönderilemedi',
      originalContent: 'Test mesajı',
      status: 'failed',
      botId: 'lara',
      enhancementType: 'professional',
      createdAt: DateTime.now().subtract(const Duration(hours: 2)),
      targetUserId: 'user101',
      metadata: {'error': 'API_RATE_LIMIT_EXCEEDED'},
    ),
    MessageData(
      id: '5',
      content: 'İyi geceler! Tatlı rüyalar 🌙✨',
      originalContent: 'İyi geceler',
      enhancedContent: 'İyi geceler! Tatlı rüyalar 🌙✨',
      status: 'sent',
      botId: 'geisha',
      enhancementType: 'caring',
      isScheduled: false,
      createdAt: DateTime.now().subtract(const Duration(hours: 5)),
      sentAt: DateTime.now().subtract(const Duration(hours: 5)),
      targetUserId: 'user202',
    ),
  ];
} 