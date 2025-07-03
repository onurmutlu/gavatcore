import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';
import '../../core/services/api_service.dart';
import '../../core/storage/storage_service.dart';
import '../../shared/themes/app_colors.dart';
import '../../shared/themes/app_colors.dart';
import '../../shared/widgets/loading_overlay.dart';

// Onboarding state
class OnboardingState {
  final int currentStep;
  final String? shovcuName;
  final String? paparaIban;
  final String? selectedCharacter;
  final String? selectedTone;
  final Map<String, dynamic>? customPrompt;
  final bool isCompleted;
  
  OnboardingState({
    this.currentStep = 0,
    this.shovcuName,
    this.paparaIban,
    this.selectedCharacter,
    this.selectedTone,
    this.customPrompt,
    this.isCompleted = false,
  });
  
  OnboardingState copyWith({
    int? currentStep,
    String? shovcuName,
    String? paparaIban,
    String? selectedCharacter,
    String? selectedTone,
    Map<String, dynamic>? customPrompt,
    bool? isCompleted,
  }) {
    return OnboardingState(
      currentStep: currentStep ?? this.currentStep,
      shovcuName: shovcuName ?? this.shovcuName,
      paparaIban: paparaIban ?? this.paparaIban,
      selectedCharacter: selectedCharacter ?? this.selectedCharacter,
      selectedTone: selectedTone ?? this.selectedTone,
      customPrompt: customPrompt ?? this.customPrompt,
      isCompleted: isCompleted ?? this.isCompleted,
    );
  }
}

// Provider
final onboardingProvider = StateNotifierProvider<OnboardingNotifier, OnboardingState>((ref) {
  return OnboardingNotifier(ref);
});

class OnboardingNotifier extends StateNotifier<OnboardingState> {
  final Ref ref;
  
  OnboardingNotifier(this.ref) : super(OnboardingState());
  
  void nextStep() {
    if (state.currentStep < 4) {
      state = state.copyWith(currentStep: state.currentStep + 1);
    }
  }
  
  void previousStep() {
    if (state.currentStep > 0) {
      state = state.copyWith(currentStep: state.currentStep - 1);
    }
  }
  
  void updateShowcuInfo(String name, String iban) {
    state = state.copyWith(shovcuName: name, paparaIban: iban);
  }
  
  void selectCharacter(String character, String tone) {
    state = state.copyWith(selectedCharacter: character, selectedTone: tone);
  }
  
  void updateCustomPrompt(Map<String, dynamic> prompt) {
    state = state.copyWith(customPrompt: prompt);
  }
  
  Future<bool> completeOnboarding() async {
    try {
      final api = ref.read(apiServiceProvider);
      
      final response = await api.post('/api/showcu/register', {
        'name': state.shovcuName,
        'papara_iban': state.paparaIban,
        'character': state.selectedCharacter,
        'tone': state.selectedTone,
        'custom_prompt': state.customPrompt,
      });
      
      if (response['success']) {
        state = state.copyWith(isCompleted: true);
        
        // Save to local storage
        final storage = ref.read(storageServiceProvider);
        await storage.setString('showcu_id', response['showcu_id']);
        await storage.setBool('onboarding_completed', true);
        
        return true;
      }
      
      return false;
    } catch (e) {
      return false;
    }
  }
}

class ShowcuOnboardingScreen extends ConsumerStatefulWidget {
  const ShowcuOnboardingScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<ShowcuOnboardingScreen> createState() => _ShowcuOnboardingScreenState();
}

class _ShowcuOnboardingScreenState extends ConsumerState<ShowcuOnboardingScreen> {
  final PageController _pageController = PageController();
  
  // Form controllers
  final _nameController = TextEditingController();
  final _ibanController = TextEditingController();
  final _promptController = TextEditingController();
  
  // Character options
  final _characters = [
    {
      'id': 'lara',
      'name': 'Lara',
      'description': 'Flörtöz Rus güzeli',
      'emoji': '💋',
      'color': Colors.pink,
    },
    {
      'id': 'babagavat',
      'name': 'BabaGavat',
      'description': 'Sokak adamı',
      'emoji': '😤',
      'color': Colors.orange,
    },
    {
      'id': 'geisha',
      'name': 'Geisha',
      'description': 'Mistik bilge',
      'emoji': '🌸',
      'color': Colors.purple,
    },
  ];
  
  final _tones = [
    {'id': 'flirty', 'name': 'Flörtöz', 'icon': Icons.favorite},
    {'id': 'soft', 'name': 'Yumuşak', 'icon': Icons.spa},
    {'id': 'dark', 'name': 'Karanlık', 'icon': Icons.nights_stay},
    {'id': 'mystic', 'name': 'Mistik', 'icon': Icons.auto_awesome},
    {'id': 'aggressive', 'name': 'Agresif', 'icon': Icons.whatshot},
  ];
  
  @override
  void dispose() {
    _pageController.dispose();
    _nameController.dispose();
    _ibanController.dispose();
    _promptController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    final onboardingState = ref.watch(onboardingProvider);
    
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          children: [
            // Progress indicator
            Padding(
              padding: const EdgeInsets.all(24),
              child: SmoothPageIndicator(
                controller: _pageController,
                count: 5,
                effect: WormEffect(
                  dotColor: AppColors.surface,
                  activeDotColor: AppColors.primary,
                  dotHeight: 8,
                  dotWidth: 8,
                  spacing: 16,
                ),
              ),
            ),
            
            // Pages
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: const NeverScrollableScrollPhysics(),
                children: [
                  _buildWelcomePage(),
                  _buildShowcuInfoPage(),
                  _buildCharacterSelectionPage(),
                  _buildCustomizationPage(),
                  _buildCompletionPage(),
                ],
              ),
            ),
            
            // Navigation buttons
            if (!onboardingState.isCompleted)
              Padding(
                padding: const EdgeInsets.all(24),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    if (onboardingState.currentStep > 0)
                      TextButton.icon(
                        onPressed: () {
                          ref.read(onboardingProvider.notifier).previousStep();
                          _pageController.previousPage(
                            duration: const Duration(milliseconds: 300),
                            curve: Curves.easeInOut,
                          );
                        },
                        icon: const Icon(Icons.arrow_back),
                        label: const Text('Geri'),
                      )
                    else
                      const SizedBox(width: 80),
                    
                    ElevatedButton(
                      onPressed: _canProceed() ? () {
                        if (onboardingState.currentStep == 4) {
                          _completeOnboarding();
                        } else {
                          ref.read(onboardingProvider.notifier).nextStep();
                          _pageController.nextPage(
                            duration: const Duration(milliseconds: 300),
                            curve: Curves.easeInOut,
                          );
                        }
                      } : null,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 32,
                          vertical: 16,
                        ),
                      ),
                      child: Text(
                        onboardingState.currentStep == 4 ? 'Tamamla' : 'İleri',
                        style: const TextStyle(fontSize: 16),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildWelcomePage() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.celebration,
            size: 120,
            color: AppColors.primary,
          ),
          const SizedBox(height: 32),
          const Text(
            'GavatCore\'a Hoş Geldin! 🎉',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          Text(
            'Kendi AI karakterini oluştur ve para kazanmaya başla!',
            style: TextStyle(
              fontSize: 18,
              color: AppColors.textSecondary,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 48),
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              children: [
                _buildFeatureItem(
                  Icons.smart_toy,
                  'AI Destekli Karakterler',
                  'GPT-4 ile güçlendirilmiş',
                ),
                const SizedBox(height: 16),
                _buildFeatureItem(
                  Icons.attach_money,
                  'Gerçek Para Kazan',
                  'VIP üyelerden gelir elde et',
                ),
                const SizedBox(height: 16),
                _buildFeatureItem(
                  Icons.dashboard,
                  'Detaylı Panel',
                  'Tüm istatistikleri takip et',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildShowcuInfoPage() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Showcu Bilgileri 🎭',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Kazançlarını alabilmen için bilgilere ihtiyacımız var',
            style: TextStyle(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 32),
          
          // Name field
          TextField(
            controller: _nameController,
            decoration: InputDecoration(
              labelText: 'Showcu Adın',
              hintText: 'Örn: StarGirl, MysteryLady',
              prefixIcon: const Icon(Icons.person),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              filled: true,
              fillColor: AppColors.surface,
            ),
            onChanged: (value) {
              // Update state immediately
            },
          ),
          
          const SizedBox(height: 24),
          
          // IBAN field
          TextField(
            controller: _ibanController,
            decoration: InputDecoration(
              labelText: 'Papara IBAN',
              hintText: 'TR00 0000 0000 0000 0000 0000 00',
              prefixIcon: const Icon(Icons.account_balance),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              filled: true,
              fillColor: AppColors.surface,
              helperText: 'Ödemeler bu hesaba yapılacak',
            ),
            onChanged: (value) {
              // Update state immediately
            },
          ),
          
          const SizedBox(height: 32),
          
          // Info cards
          _buildInfoCard(
            Icons.security,
            'Güvenlik',
            'Bilgilerin şifrelenerek saklanır',
            Colors.green,
          ),
          const SizedBox(height: 12),
          _buildInfoCard(
            Icons.payment,
            'Ödemeler',
            'Haftalık otomatik ödeme',
            Colors.blue,
          ),
          const SizedBox(height: 12),
          _buildInfoCard(
            Icons.support_agent,
            'Destek',
            '7/24 showcu desteği',
            Colors.orange,
          ),
        ],
      ),
    );
  }
  
  Widget _buildCharacterSelectionPage() {
    final onboardingState = ref.watch(onboardingProvider);
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Karakter Seç 🎭',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Hangi karakterle çalışmak istersin?',
            style: TextStyle(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 32),
          
          // Character cards
          ..._characters.map((character) => Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: InkWell(
              onTap: () {
                ref.read(onboardingProvider.notifier).selectCharacter(
                  character['id'] as String,
                  _tones[0]['id'] as String, // Default tone
                );
              },
              borderRadius: BorderRadius.circular(16),
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: onboardingState.selectedCharacter == character['id']
                        ? character['color'] as Color
                        : Colors.transparent,
                    width: 2,
                  ),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 60,
                      height: 60,
                      decoration: BoxDecoration(
                        color: (character['color'] as Color).withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Center(
                        child: Text(
                          character['emoji'] as String,
                          style: const TextStyle(fontSize: 32),
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            character['name'] as String,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            character['description'] as String,
                            style: TextStyle(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    if (onboardingState.selectedCharacter == character['id'])
                      Icon(
                        Icons.check_circle,
                        color: character['color'] as Color,
                      ),
                  ],
                ),
              ),
            ),
          )).toList(),
          
          const SizedBox(height: 24),
          
          // Tone selection
          if (onboardingState.selectedCharacter != null) ...[
            const Text(
              'Ton Seç',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _tones.map((tone) => ChoiceChip(
                label: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      tone['icon'] as IconData,
                      size: 16,
                    ),
                    const SizedBox(width: 4),
                    Text(tone['name'] as String),
                  ],
                ),
                selected: onboardingState.selectedTone == tone['id'],
                onSelected: (selected) {
                  if (selected) {
                    ref.read(onboardingProvider.notifier).selectCharacter(
                      onboardingState.selectedCharacter!,
                      tone['id'] as String,
                    );
                  }
                },
                selectedColor: AppColors.primary,
              )).toList(),
            ),
          ],
        ],
      ),
    );
  }
  
  Widget _buildCustomizationPage() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Karakterini Özelleştir ✨',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Karakterine özel davranışlar ekle',
            style: TextStyle(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 32),
          
          // Custom prompt
          TextField(
            controller: _promptController,
            maxLines: 6,
            decoration: InputDecoration(
              labelText: 'Özel Prompt (İsteğe Bağlı)',
              hintText: 'Karakterinin nasıl davranmasını istersin?\n\nÖrnek: "Her zaman pozitif ol, müşterilere değer verdiklerini hissettir..."',
              alignLabelWithHint: true,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              filled: true,
              fillColor: AppColors.surface,
            ),
          ),
          
          const SizedBox(height: 24),
          
          // Preset behaviors
          const Text(
            'Hazır Davranışlar',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          
          _buildBehaviorOption(
            'Gizemli',
            'Her şeyi açıklama, merak uyandır',
            Icons.visibility_off,
            true,
          ),
          _buildBehaviorOption(
            'Dominant',
            'Kontrolü elinde tut, yönlendirici ol',
            Icons.psychology,
            false,
          ),
          _buildBehaviorOption(
            'Romantik',
            'Duygusal bağ kur, şiirsel konuş',
            Icons.favorite,
            true,
          ),
          _buildBehaviorOption(
            'Eğlenceli',
            'Espri yap, neşeli ol',
            Icons.mood,
            false,
          ),
          
          const SizedBox(height: 32),
          
          // Tips
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.info.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.info),
            ),
            child: Row(
              children: [
                Icon(Icons.lightbulb, color: AppColors.info),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'İpucu: Karakterin ne kadar özgün olursa, o kadar ilgi çeker!',
                    style: TextStyle(color: AppColors.info),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildCompletionPage() {
    final onboardingState = ref.watch(onboardingProvider);
    
    if (onboardingState.isCompleted) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.check_circle,
                size: 120,
                color: AppColors.success,
              ),
              const SizedBox(height: 32),
              const Text(
                'Tebrikler! 🎉',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'Karakterin hazır!',
                style: TextStyle(
                  fontSize: 18,
                  color: AppColors.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              ElevatedButton.icon(
                onPressed: () {
                  Navigator.pushReplacementNamed(context, '/dashboard');
                },
                icon: const Icon(Icons.dashboard),
                label: const Text('Dashboard\'a Git'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    }
    
    return const Center(
      child: CircularProgressIndicator(),
    );
  }
  
  Widget _buildFeatureItem(IconData icon, String title, String subtitle) {
    return Row(
      children: [
        Icon(icon, color: AppColors.primary, size: 32),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              Text(
                subtitle,
                style: TextStyle(
                  color: AppColors.textSecondary,
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
  
  Widget _buildInfoCard(IconData icon, String title, String subtitle, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, color: color),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
                Text(
                  subtitle,
                  style: const TextStyle(fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildBehaviorOption(String title, String description, IconData icon, bool selected) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () {
          // Toggle behavior
        },
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: selected ? AppColors.primary.withOpacity(0.1) : AppColors.surface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: selected ? AppColors.primary : Colors.transparent,
            ),
          ),
          child: Row(
            children: [
              Icon(
                icon,
                color: selected ? AppColors.primary : AppColors.textSecondary,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    Text(
                      description,
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              if (selected)
                Icon(
                  Icons.check_circle,
                  color: AppColors.primary,
                ),
            ],
          ),
        ),
      ),
    );
  }
  
  bool _canProceed() {
    final state = ref.read(onboardingProvider);
    
    switch (state.currentStep) {
      case 0:
        return true; // Welcome page
      case 1:
        return _nameController.text.isNotEmpty && _ibanController.text.isNotEmpty;
      case 2:
        return state.selectedCharacter != null && state.selectedTone != null;
      case 3:
        return true; // Customization is optional
      case 4:
        return true; // Ready to complete
      default:
        return false;
    }
  }
  
  Future<void> _completeOnboarding() async {
    // Update state with form data
    ref.read(onboardingProvider.notifier).updateShowcuInfo(
      _nameController.text,
      _ibanController.text,
    );
    
    if (_promptController.text.isNotEmpty) {
      ref.read(onboardingProvider.notifier).updateCustomPrompt({
        'custom_prompt': _promptController.text,
      });
    }
    
    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: Card(
          child: Padding(
            padding: EdgeInsets.all(24),
            child: CircularProgressIndicator(),
          ),
        ),
      ),
    );
    
    // Complete onboarding
    final success = await ref.read(onboardingProvider.notifier).completeOnboarding();
    
    // Hide loading
    Navigator.pop(context);
    
    if (success) {
      // Trigger rebuild to show completion page
      setState(() {});
    } else {
      // Show error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Bir hata oluştu, lütfen tekrar dene'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }
} 