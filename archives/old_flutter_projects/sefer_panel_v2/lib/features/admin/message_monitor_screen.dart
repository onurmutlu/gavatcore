import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/models/message_model.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/loading_view.dart';
import '../../shared/widgets/message_bubble.dart';

class MessageMonitorScreen extends ConsumerStatefulWidget {
  const MessageMonitorScreen({super.key});

  @override
  ConsumerState<MessageMonitorScreen> createState() => _MessageMonitorScreenState();
}

class _MessageMonitorScreenState extends ConsumerState<MessageMonitorScreen> {
  final _apiService = ApiService();
  List<MessageModel>? _messages;
  bool _isLoading = true;
  String _error = '';
  String? _selectedBotId;
  DateTime? _startDate;
  DateTime? _endDate;
  final _scrollController = ScrollController();
  bool _hasMoreMessages = true;
  static const _pageSize = 50;

  @override
  void initState() {
    super.initState();
    _loadMessages();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent * 0.8 &&
        !_isLoading &&
        _hasMoreMessages) {
      _loadMoreMessages();
    }
  }

  Future<void> _loadMessages({bool refresh = true}) async {
    try {
      setState(() {
        if (refresh) {
          _messages = null;
        }
        _isLoading = true;
      });

      final messages = await _apiService.getMessages(
        botId: _selectedBotId,
        startDate: _startDate,
        endDate: _endDate,
        limit: _pageSize,
        offset: refresh ? 0 : _messages?.length ?? 0,
      );

      setState(() {
        if (refresh) {
          _messages = messages;
        } else {
          _messages = [...?_messages, ...messages];
        }
        _hasMoreMessages = messages.length == _pageSize;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Mesajlar yüklenirken hata oluştu: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _loadMoreMessages() async {
    if (_isLoading || !_hasMoreMessages) return;
    await _loadMessages(refresh: false);
  }

  Future<void> _showDateRangePicker() async {
    final picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
      initialDateRange: _startDate != null && _endDate != null
          ? DateTimeRange(start: _startDate!, end: _endDate!)
          : null,
    );

    if (picked != null) {
      setState(() {
        _startDate = picked.start;
        _endDate = picked.end;
      });
      _loadMessages();
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading && _messages == null) {
      return const LoadingView();
    }

    if (_error.isNotEmpty && _messages == null) {
      return ErrorView(
        error: _error,
        onRetry: () => _loadMessages(),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mesaj İzleme'),
        actions: [
          IconButton(
            icon: const Icon(Icons.calendar_today),
            onPressed: _showDateRangePicker,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => _loadMessages(),
          ),
        ],
      ),
      body: Column(
        children: [
          // Filtreler
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    decoration: const InputDecoration(
                      labelText: 'Bot Seç',
                      border: OutlineInputBorder(),
                    ),
                    value: _selectedBotId,
                    items: const [
                      DropdownMenuItem(
                        value: null,
                        child: Text('Tümü'),
                      ),
                      // TODO: Bot listesini API'den al
                    ],
                    onChanged: (value) {
                      setState(() => _selectedBotId = value);
                      _loadMessages();
                    },
                  ),
                ),
                const SizedBox(width: 16),
                if (_startDate != null && _endDate != null)
                  Chip(
                    label: Text(
                      '${_startDate!.day}/${_startDate!.month} - ${_endDate!.day}/${_endDate!.month}',
                    ),
                    onDeleted: () {
                      setState(() {
                        _startDate = null;
                        _endDate = null;
                      });
                      _loadMessages();
                    },
                  ),
              ],
            ),
          ),

          // Mesaj Listesi
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: (_messages?.length ?? 0) + (_isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == _messages?.length) {
                  return const Center(
                    child: CircularProgressIndicator(),
                  );
                }

                final message = _messages![index];
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: MessageBubble(
                    message: message,
                    onTap: () {
                      // TODO: Mesaj detayları
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
} 