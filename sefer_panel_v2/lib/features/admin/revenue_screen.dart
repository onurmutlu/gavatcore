import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/loading_view.dart';
import '../../shared/widgets/chart_card.dart';

class RevenueScreen extends ConsumerStatefulWidget {
  const RevenueScreen({super.key});

  @override
  ConsumerState<RevenueScreen> createState() => _RevenueScreenState();
}

class _RevenueScreenState extends ConsumerState<RevenueScreen> {
  final _apiService = ApiService();
  Map<String, dynamic>? _revenueData;
  bool _isLoading = true;
  String _error = '';
  String _selectedTimeRange = 'week';
  String? _selectedSource;

  @override
  void initState() {
    super.initState();
    _loadRevenueData();
  }

  Future<void> _loadRevenueData() async {
    try {
      setState(() => _isLoading = true);

      DateTime? startDate;
      final now = DateTime.now();

      switch (_selectedTimeRange) {
        case 'week':
          startDate = now.subtract(const Duration(days: 7));
          break;
        case 'month':
          startDate = DateTime(now.year, now.month - 1, now.day);
          break;
        case 'year':
          startDate = DateTime(now.year - 1, now.month, now.day);
          break;
      }

      final data = await _apiService.getRevenue(
        startDate: startDate,
        endDate: now,
        source: _selectedSource,
      );

      setState(() {
        _revenueData = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Gelir verileri yüklenirken hata oluştu: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const LoadingView();
    }

    if (_error.isNotEmpty) {
      return ErrorView(
        error: _error,
        onRetry: _loadRevenueData,
      );
    }

    final totalRevenue = _revenueData?['totalRevenue'] ?? 0.0;
    final revenueBySource = _revenueData?['revenueBySource'] ?? {};
    final dailyRevenue = _revenueData?['dailyRevenue'] ?? [];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Gelir Takibi'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadRevenueData,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Filtreler
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    decoration: const InputDecoration(
                      labelText: 'Zaman Aralığı',
                      border: OutlineInputBorder(),
                    ),
                    value: _selectedTimeRange,
                    items: const [
                      DropdownMenuItem(
                        value: 'week',
                        child: Text('Son 7 Gün'),
                      ),
                      DropdownMenuItem(
                        value: 'month',
                        child: Text('Son 30 Gün'),
                      ),
                      DropdownMenuItem(
                        value: 'year',
                        child: Text('Son 1 Yıl'),
                      ),
                    ],
                    onChanged: (value) {
                      if (value != null) {
                        setState(() => _selectedTimeRange = value);
                        _loadRevenueData();
                      }
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    decoration: const InputDecoration(
                      labelText: 'Gelir Kaynağı',
                      border: OutlineInputBorder(),
                    ),
                    value: _selectedSource,
                    items: const [
                      DropdownMenuItem(
                        value: null,
                        child: Text('Tümü'),
                      ),
                      DropdownMenuItem(
                        value: 'subscription',
                        child: Text('Abonelikler'),
                      ),
                      DropdownMenuItem(
                        value: 'donation',
                        child: Text('Bağışlar'),
                      ),
                      DropdownMenuItem(
                        value: 'service',
                        child: Text('Hizmetler'),
                      ),
                    ],
                    onChanged: (value) {
                      setState(() => _selectedSource = value);
                      _loadRevenueData();
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Toplam Gelir Kartı
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Toplam Gelir',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '₺${totalRevenue.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Gelir Grafikleri
            Row(
              children: [
                Expanded(
                  flex: 2,
                  child: ChartCard(
                    title: 'Günlük Gelir',
                    data: dailyRevenue,
                    dataKey: 'amount',
                    color: Colors.green,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ChartCard(
                    title: 'Gelir Kaynakları',
                    data: revenueBySource.entries.toList(),
                    dataKey: 'value',
                    color: Colors.blue,
                    isDonut: true,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
} 