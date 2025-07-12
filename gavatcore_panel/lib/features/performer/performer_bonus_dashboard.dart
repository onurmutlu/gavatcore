import 'package:flutter/material.dart';
import '../../shared/themes/app_theme.dart';

class PerformerBonusDashboard extends StatefulWidget {
  final String performerId;
  
  const PerformerBonusDashboard({
    Key? key,
    required this.performerId,
  }) : super(key: key);

  @override
  State<PerformerBonusDashboard> createState() => _PerformerBonusDashboardState();
}

class _PerformerBonusDashboardState extends State<PerformerBonusDashboard> {
  bool _isLoading = false;
  bool _isNightShift = false;
  int _currentBalance = 0;
  int _weeklyEarnings = 0;
  int _messagesToday = 0;
  int _nightShiftBonus = 0;
  int _messageBonus = 0;
  int _firstLoginBonus = 0;
  int _totalBonus = 0;

  @override
  void initState() {
    super.initState();
    _loadBonusData();
    _checkNightShift();
  }

  Future<void> _loadBonusData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // Simüle edilmiş veri
      await Future.delayed(const Duration(seconds: 1));
      
      setState(() {
        _currentBalance = 1250;
        _weeklyEarnings = 850;
        _messagesToday = 47;
        _nightShiftBonus = 35;
        _messageBonus = 141;
        _firstLoginBonus = 10;
        _totalBonus = _nightShiftBonus + _messageBonus + _firstLoginBonus;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _checkNightShift() {
    final now = DateTime.now();
    final hour = now.hour;
    setState(() {
      _isNightShift = hour >= 2 && hour < 6;
    });
  }

  Future<void> _startNightShift() async {
    setState(() {
      _isLoading = true;
    });

    try {
      await Future.delayed(const Duration(seconds: 1));
      
      setState(() {
        _isNightShift = true;
        _nightShiftBonus += 20;
        _totalBonus = _nightShiftBonus + _messageBonus + _firstLoginBonus;
        _isLoading = false;
      });
      
      _showSnackbar('🖤 Gece nöbeti başlatıldı! +20 TL bonus', Colors.green);
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      _showSnackbar('Hata: ${e.toString()}', Colors.red);
    }
  }

  Future<void> _requestPayment() async {
    setState(() {
      _isLoading = true;
    });

    try {
      await Future.delayed(const Duration(seconds: 2));
      
      setState(() {
        _currentBalance += _totalBonus;
        _weeklyEarnings += _totalBonus;
        _nightShiftBonus = 0;
        _messageBonus = 0;
        _firstLoginBonus = 0;
        _totalBonus = 0;
        _isLoading = false;
      });
      
      _showSnackbar('💸 Ödeme talep edildi! ${_totalBonus} TL hesabınıza aktarılacak', Colors.green);
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      _showSnackbar('Hata: ${e.toString()}', Colors.red);
    }
  }

  void _showSnackbar(String message, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: color,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: const Text(
          '💸 Bonus & Kazanç',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        backgroundColor: AppTheme.primaryColor,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _loadBonusData,
          ),
        ],
      ),
      body: _isLoading
        ? const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircularProgressIndicator(color: AppTheme.primaryColor),
                SizedBox(height: 16),
                Text(
                  'Veriler yükleniyor...',
                  style: TextStyle(color: Colors.white),
                ),
              ],
            ),
          )
        : RefreshIndicator(
            onRefresh: _loadBonusData,
            color: AppTheme.primaryColor,
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  // Ana bakiye kartı
                  _buildBalanceCard(),
                  const SizedBox(height: 20),
                  
                  // Gece nöbeti kartı
                  _buildNightShiftCard(),
                  const SizedBox(height: 20),
                  
                  // Bonus detayları
                  _buildBonusDetailsCard(),
                  const SizedBox(height: 20),
                  
                  // Haftalık istatistikler
                  _buildWeeklyStatsCard(),
                  const SizedBox(height: 20),
                  
                  // Ödeme butonu
                  _buildPaymentButton(),
                ],
              ),
            ),
          ),
    );
  }

  Widget _buildBalanceCard() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppTheme.primaryColor.withOpacity(0.8),
            AppTheme.accentColor.withOpacity(0.8),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              const Icon(
                Icons.account_balance_wallet,
                color: Colors.white,
                size: 28,
              ),
              const SizedBox(width: 12),
              const Text(
                'Toplam Bakiye',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            '${_currentBalance} TL',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 36,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Bu hafta: ${_weeklyEarnings} TL',
            style: TextStyle(
              color: Colors.white.withOpacity(0.8),
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNightShiftCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _isNightShift 
          ? Colors.green.withOpacity(0.1)
          : AppTheme.cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: _isNightShift 
            ? Colors.green.withOpacity(0.3)
            : Colors.white.withOpacity(0.1),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Icon(
                _isNightShift ? Icons.nightlight : Icons.nightlight_round,
                color: _isNightShift ? Colors.green : Colors.white70,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                '🖤 Gece Nöbeti',
                style: TextStyle(
                  color: _isNightShift ? Colors.green : Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: _isNightShift ? Colors.green : Colors.grey,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  _isNightShift ? 'AKTİF' : 'PASİF',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            _isNightShift 
              ? 'Gece nöbeti aktif! 02:00-06:00 arası bonus kazanıyorsun.'
              : 'Gece nöbeti (02:00-06:00) başlatmak için butona bas.',
            style: TextStyle(
              color: Colors.white.withOpacity(0.8),
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 16),
          if (!_isNightShift)
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _startNightShift,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'Gece Nöbeti Başlat',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildBonusDetailsCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.white.withOpacity(0.1),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              const Icon(
                Icons.monetization_on,
                color: AppTheme.accentColor,
                size: 24,
              ),
              const SizedBox(width: 12),
              const Text(
                'Bonus Detayları',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          _buildBonusItem(
            'Gece Nöbeti',
            '${_nightShiftBonus} TL',
            Icons.nightlight,
            Colors.green,
          ),
          const SizedBox(height: 12),
          
          _buildBonusItem(
            'Mesaj Bonusu',
            '${_messageBonus} TL',
            Icons.message,
            Colors.blue,
          ),
          const SizedBox(height: 12),
          
          _buildBonusItem(
            'İlk Giriş',
            '${_firstLoginBonus} TL',
            Icons.star,
            Colors.orange,
          ),
          
          const Divider(color: Colors.white12, height: 32),
          
          _buildBonusItem(
            'TOPLAM',
            '${_totalBonus} TL',
            Icons.account_balance_wallet,
            AppTheme.accentColor,
            isTotal: true,
          ),
        ],
      ),
    );
  }

  Widget _buildBonusItem(String title, String amount, IconData icon, Color color, {bool isTotal = false}) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            icon,
            color: color,
            size: 20,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            title,
            style: TextStyle(
              color: Colors.white.withOpacity(0.8),
              fontSize: isTotal ? 16 : 14,
              fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ),
        Text(
          amount,
          style: TextStyle(
            color: color,
            fontSize: isTotal ? 18 : 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildWeeklyStatsCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.white.withOpacity(0.1),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              const Icon(
                Icons.analytics,
                color: AppTheme.accentColor,
                size: 24,
              ),
              const SizedBox(width: 12),
              const Text(
                'Haftalık İstatistikler',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          Row(
            children: [
              Expanded(
                child: _buildStatItem(
                  'Bugünkü Mesaj',
                  '${_messagesToday}',
                  Icons.message,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildStatItem(
                  'Haftalık Kazanç',
                  '${_weeklyEarnings} TL',
                  Icons.trending_up,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(
          icon,
          color: AppTheme.accentColor,
          size: 24,
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withOpacity(0.7),
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildPaymentButton() {
    return Container(
      width: double.infinity,
      height: 60,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppTheme.accentColor,
            AppTheme.accentColor.withOpacity(0.8),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppTheme.accentColor.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: _totalBonus > 0 ? _requestPayment : null,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.payment,
              color: Colors.white,
              size: 24,
            ),
            const SizedBox(width: 12),
            Text(
              _totalBonus > 0 
                ? '💸 ${_totalBonus} TL Ödeme Talep Et'
                : 'Ödenecek bonus yok',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }
} 