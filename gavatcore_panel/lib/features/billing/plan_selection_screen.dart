import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/services/api_service.dart';

class PlanSelectionScreen extends ConsumerStatefulWidget {
  const PlanSelectionScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<PlanSelectionScreen> createState() => _PlanSelectionScreenState();
}

class _PlanSelectionScreenState extends ConsumerState<PlanSelectionScreen> {
  Map<String, dynamic>? _plans;
  SubscriptionStatus? _currentSubscription;
  bool _isLoading = true;
  String? _selectedPlan;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    
    try {
      final apiService = ApiService();
      final saasService = SaasApiService(apiService);
      
      // Load pricing plans and current subscription in parallel
      final results = await Future.wait([
        saasService.getPricingPlans(),
        saasService.getSubscriptionStatus(),
      ]);
      
      setState(() {
        _plans = results[0] as Map<String, dynamic>;
        _currentSubscription = results[1] as SubscriptionStatus;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Veriler yüklenirken hata: $e')),
      );
    }
  }

  Future<void> _selectPlan(String planName) async {
    if (_currentSubscription?.hasSubscription == true && 
        _currentSubscription?.subscription?.planName == planName) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Bu plan zaten aktif!')),
      );
      return;
    }

    setState(() => _selectedPlan = planName);

    try {
      final apiService = ApiService();
      final saasService = SaasApiService(apiService);
      
      // Create checkout session
      final checkoutResponse = await saasService.createCheckout(
        planName: planName,
        successUrl: 'https://panel.gavatcore.com/payment/success',
        cancelUrl: 'https://panel.gavatcore.com/payment/cancel',
      );

      // Open Stripe checkout in web browser
      final uri = Uri.parse(checkoutResponse.sessionUrl);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        throw 'Ödeme sayfası açılamadı';
      }

    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ödeme başlatılamadı: $e')),
      );
    } finally {
      setState(() => _selectedPlan = null);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0a0a0a),
      appBar: AppBar(
        title: const Text('Plan Seçimi', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildPlanSelection(),
    );
  }

  Widget _buildPlanSelection() {
    if (_plans == null) {
      return const Center(
        child: Text('Planlar yüklenemedi', style: TextStyle(color: Colors.white)),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Current subscription status
          if (_currentSubscription?.hasSubscription == true)
            _buildCurrentSubscription(),
          
          const SizedBox(height: 32),
          
          // Plans grid
          const Text(
            '🚀 GavatCore SaaS Planları',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Bot-as-a-Service platformunda en uygun planı seçin',
            style: TextStyle(fontSize: 16, color: Colors.grey),
          ),
          
          const SizedBox(height: 32),
          
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              childAspectRatio: 0.8,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
            ),
            itemCount: _plans!['plans'].length,
            itemBuilder: (context, index) {
              final planEntry = _plans!['plans'].entries.elementAt(index);
              final planKey = planEntry.key;
              final plan = planEntry.value;
              
              return _buildPlanCard(planKey, plan);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildCurrentSubscription() {
    final subscription = _currentSubscription!.subscription!;
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.green.withOpacity(0.1),
        border: Border.all(color: Colors.green, width: 1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.check_circle, color: Colors.green, size: 24),
              const SizedBox(width: 8),
              Text(
                'Aktif Plan: ${subscription.planName.toUpperCase()}',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Icon(Icons.schedule, color: Colors.grey[400], size: 16),
              const SizedBox(width: 4),
              Text(
                '${subscription.daysRemaining} gün kaldı',
                style: TextStyle(color: Colors.grey[400]),
              ),
              const Spacer(),
              if (subscription.isTrial)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.orange.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'DENEME',
                    style: TextStyle(
                      color: Colors.orange,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Özellikler: ${subscription.features.join(", ")}',
            style: TextStyle(color: Colors.grey[300], fontSize: 14),
          ),
        ],
      ),
    );
  }

  Widget _buildPlanCard(String planKey, Map<String, dynamic> plan) {
    final isCurrentPlan = _currentSubscription?.subscription?.planName == planKey;
    final isSelected = _selectedPlan == planKey;
    final isTrial = planKey == 'trial';
    final isPro = planKey == 'pro';
    
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: isPro
              ? [Colors.purple.withOpacity(0.3), Colors.blue.withOpacity(0.1)]
              : [Colors.grey.withOpacity(0.1), Colors.black.withOpacity(0.3)],
        ),
        border: Border.all(
          color: isCurrentPlan
              ? Colors.green
              : isPro
                  ? Colors.purple
                  : Colors.grey.withOpacity(0.3),
          width: isCurrentPlan ? 2 : 1,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Plan header
            Row(
              children: [
                Text(
                  plan['name'],
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const Spacer(),
                if (isPro)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.purple,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Text(
                      'POPULAR',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Price
            if (isTrial)
              const Text(
                'ÜCRETSİZ',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              )
            else
              RichText(
                text: TextSpan(
                  children: [
                    TextSpan(
                      text: '₺${plan['price']}',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    TextSpan(
                      text: ' / ${plan['duration']}',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[400],
                      ),
                    ),
                  ],
                ),
              ),
            
            const SizedBox(height: 16),
            
            // Features
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (final feature in plan['features'])
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        children: [
                          Icon(
                            Icons.check,
                            color: Colors.green[400],
                            size: 16,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              feature,
                              style: TextStyle(
                                color: Colors.grey[300],
                                fontSize: 14,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Action button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: isCurrentPlan || isSelected
                    ? null
                    : () => _selectPlan(planKey),
                style: ElevatedButton.styleFrom(
                  backgroundColor: isCurrentPlan
                      ? Colors.green
                      : isPro
                          ? Colors.purple
                          : Colors.blue,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: isSelected
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation(Colors.white),
                        ),
                      )
                    : Text(
                        isCurrentPlan
                            ? 'AKTİF PLAN'
                            : isTrial
                                ? 'DENE'
                                : 'SATIN AL',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
} 