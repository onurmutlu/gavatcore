import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/glass_container.dart';
import '../../../core/models/app_state.dart';
import '../../../core/providers/app_providers.dart';

class AIPromptsScreen extends ConsumerStatefulWidget {
  const AIPromptsScreen({super.key});

  @override
  ConsumerState<AIPromptsScreen> createState() => _AIPromptsScreenState();
}

class _AIPromptsScreenState extends ConsumerState<AIPromptsScreen>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  final TextEditingController _searchController = TextEditingController();
  String _selectedType = 'all';
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _animationController.repeat();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final prompts = ref.watch(aiPromptsProvider);

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Column(
        children: [
          _buildHeader(),
          Expanded(
            child: prompts.when(
              data: (data) => _buildPromptsContent(data),
              loading: () => _buildLoadingState(),
              error: (error, stack) => _buildErrorState(error.toString()),
            ),
          ),
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
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  gradient: AppTheme.primaryGradient,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.neonColors.purple.withOpacity(0.3),
                      blurRadius: 15,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: Icon(
                  Icons.psychology,
                  color: Colors.white,
                  size: 24,
                ),
              ).animate(controller: _animationController)
                  .scale(begin: 1.0, end: 1.1)
                  .then()
                  .scale(begin: 1.1, end: 1.0),
              
              const SizedBox(width: 16),
              
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'AI Prompt Blending',
                      style: NeonTextStyles.neonTitle,
                    ),
                    Text(
                      'AI enhancement prompt\'larını yönet ve test et',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
              
              AnimatedGlassContainer(
                padding: const EdgeInsets.all(12),
                onTap: () => _showCreatePromptDialog(),
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
                      'Yeni Prompt',
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
          
          const SizedBox(height: 20),
          
          // Search and Filter Row
          Row(
            children: [
              Expanded(
                flex: 3,
                child: GlassContainer(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: TextField(
                    controller: _searchController,
                    onChanged: (value) {
                      setState(() {
                        _searchQuery = value;
                      });
                    },
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Prompt\'larda ara...',
                      hintStyle: TextStyle(color: Colors.white54),
                      prefixIcon: Icon(
                        Icons.search,
                        color: AppTheme.neonColors.blue,
                      ),
                      border: InputBorder.none,
                      suffixIcon: _searchQuery.isNotEmpty
                          ? IconButton(
                              icon: Icon(
                                Icons.clear,
                                color: Colors.white54,
                              ),
                              onPressed: () {
                                _searchController.clear();
                                setState(() {
                                  _searchQuery = '';
                                });
                              },
                            )
                          : null,
                    ),
                  ),
                ),
              ),
              
              const SizedBox(width: 16),
              
              Expanded(
                flex: 1,
                child: GlassContainer(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: _selectedType,
                      dropdownColor: const Color(0xFF1A1A2E),
                      style: const TextStyle(color: Colors.white),
                      items: [
                        'all', 'persuasive', 'friendly', 'professional', 
                        'casual', 'flirty', 'sales'
                      ].map((type) {
                        return DropdownMenuItem(
                          value: type,
                          child: Text(_getTypeDisplayName(type)),
                        );
                      }).toList(),
                      onChanged: (value) {
                        if (value != null) {
                          setState(() {
                            _selectedType = value;
                          });
                        }
                      },
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPromptsContent(List<AIPromptData> prompts) {
    final filteredPrompts = _filterPrompts(prompts);
    
    if (filteredPrompts.isEmpty) {
      return _buildEmptyState();
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        children: [
          // Statistics Row
          _buildStatsRow(prompts),
          
          const SizedBox(height: 20),
          
          // Prompts Grid
          Expanded(
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                childAspectRatio: 1.2,
              ),
              itemCount: filteredPrompts.length,
              itemBuilder: (context, index) {
                final prompt = filteredPrompts[index];
                return _buildPromptCard(prompt, index);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsRow(List<AIPromptData> prompts) {
    final totalPrompts = prompts.length;
    final activePrompts = prompts.where((p) => p.isActive).length;
    final totalUsage = prompts.fold<int>(0, (sum, p) => sum + p.usageCount);
    final avgResponseTime = prompts.isNotEmpty
        ? prompts.fold<double>(0, (sum, p) => sum + p.avgResponseTime) / prompts.length
        : 0.0;

    return Row(
      children: [
        _buildStatChip(
          'Toplam: $totalPrompts',
          AppTheme.neonColors.blue,
          Icons.psychology,
        ),
        const SizedBox(width: 12),
        _buildStatChip(
          'Aktif: $activePrompts',
          AppTheme.neonColors.green,
          Icons.check_circle,
        ),
        const SizedBox(width: 12),
        _buildStatChip(
          'Kullanım: ${_formatNumber(totalUsage)}',
          AppTheme.neonColors.orange,
          Icons.trending_up,
        ),
        const SizedBox(width: 12),
        _buildStatChip(
          'Ortalama: ${avgResponseTime.toStringAsFixed(1)}s',
          AppTheme.neonColors.purple,
          Icons.speed,
        ),
      ],
    );
  }

  Widget _buildStatChip(String text, Color color, IconData icon) {
    return Expanded(
      child: GlassContainer(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: color, size: 16),
            const SizedBox(width: 6),
            Expanded(
              child: Text(
                text,
                style: TextStyle(
                  color: color,
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPromptCard(AIPromptData prompt, int index) {
    final typeColor = _getTypeColor(prompt.type);
    
    return AnimatedGlassContainer(
      padding: const EdgeInsets.all(16),
      onTap: () => _showPromptDetails(prompt),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: typeColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: typeColor.withOpacity(0.5)),
                ),
                child: Text(
                  _getTypeDisplayName(prompt.type),
                  style: TextStyle(
                    color: typeColor,
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              
              const Spacer(),
              
              // Status indicator
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: prompt.isActive 
                      ? AppTheme.neonColors.green 
                      : AppTheme.neonColors.red,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: (prompt.isActive 
                          ? AppTheme.neonColors.green 
                          : AppTheme.neonColors.red).withOpacity(0.5),
                      blurRadius: 8,
                      spreadRadius: 2,
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Title
          Text(
            prompt.name,
            style: NeonTextStyles.neonSubtitle.copyWith(
              fontSize: 16,
              color: Colors.white,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          
          const SizedBox(height: 8),
          
          // Prompt preview
          Text(
            prompt.prompt.length > 80 
                ? '${prompt.prompt.substring(0, 80)}...'
                : prompt.prompt,
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              height: 1.3,
            ),
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
          ),
          
          const Spacer(),
          
          // Stats row
          Row(
            children: [
              Icon(
                Icons.analytics,
                color: AppTheme.neonColors.blue,
                size: 14,
              ),
              const SizedBox(width: 4),
              Text(
                '${_formatNumber(prompt.usageCount)} kullanım',
                style: TextStyle(
                  color: AppTheme.neonColors.blue,
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                ),
              ),
              
              const Spacer(),
              
              Icon(
                Icons.speed,
                color: AppTheme.neonColors.orange,
                size: 14,
              ),
              const SizedBox(width: 4),
              Text(
                '${prompt.avgResponseTime.toStringAsFixed(1)}s',
                style: TextStyle(
                  color: AppTheme.neonColors.orange,
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ],
      ),
    ).animate(delay: Duration(milliseconds: index * 100))
        .fadeIn()
        .slideY(begin: 0.3, end: 0);
  }

  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.psychology,
              color: Colors.white,
              size: 30,
            ),
          ).animate(onPlay: (controller) => controller.repeat())
              .rotate(duration: 2.seconds),
          
          const SizedBox(height: 24),
          
          Text(
            'AI Prompt\'lar yükleniyor...',
            style: NeonTextStyles.neonSubtitle,
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: GlassContainer(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.error_outline,
              color: AppTheme.neonColors.red,
              size: 48,
            ),
            const SizedBox(height: 16),
            Text(
              'Prompt\'lar yüklenemedi',
              style: NeonTextStyles.neonSubtitle.copyWith(
                color: AppTheme.neonColors.red,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              error,
              style: TextStyle(color: Colors.white60, fontSize: 12),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            AnimatedGlassContainer(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              onTap: () => ref.invalidate(aiPromptsProvider),
              child: Text(
                'Tekrar Dene',
                style: TextStyle(
                  color: AppTheme.neonColors.blue,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: GlassContainer(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.psychology_outlined,
              color: AppTheme.neonColors.purple,
              size: 64,
            ),
            const SizedBox(height: 16),
            Text(
              'Henüz prompt yok',
              style: NeonTextStyles.neonSubtitle,
            ),
            const SizedBox(height: 8),
            Text(
              'İlk AI enhancement prompt\'ını oluştur',
              style: TextStyle(color: Colors.white60),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            AnimatedGlassContainer(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              onTap: () => _showCreatePromptDialog(),
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
                    'Prompt Oluştur',
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
      ),
    );
  }

  // Helper methods
  List<AIPromptData> _filterPrompts(List<AIPromptData> prompts) {
    return prompts.where((prompt) {
      final matchesSearch = _searchQuery.isEmpty ||
          prompt.name.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          prompt.prompt.toLowerCase().contains(_searchQuery.toLowerCase());
      
      final matchesType = _selectedType == 'all' || prompt.type == _selectedType;
      
      return matchesSearch && matchesType;
    }).toList();
  }

  String _getTypeDisplayName(String type) {
    switch (type) {
      case 'all': return 'Tümü';
      case 'persuasive': return 'İkna Edici';
      case 'friendly': return 'Arkadaşça';
      case 'professional': return 'Profesyonel';
      case 'casual': return 'Günlük';
      case 'flirty': return 'Flörtöz';
      case 'sales': return 'Satış';
      default: return type;
    }
  }

  Color _getTypeColor(String type) {
    switch (type) {
      case 'persuasive': return AppTheme.neonColors.purple;
      case 'friendly': return AppTheme.neonColors.green;
      case 'professional': return AppTheme.neonColors.blue;
      case 'casual': return AppTheme.neonColors.yellow;
      case 'flirty': return AppTheme.neonColors.pink;
      case 'sales': return AppTheme.neonColors.orange;
      default: return AppTheme.neonColors.cyan;
    }
  }

  String _formatNumber(int number) {
    if (number >= 1000000) {
      return '${(number / 1000000).toStringAsFixed(1)}M';
    } else if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)}K';
    }
    return number.toString();
  }

  void _showCreatePromptDialog() {
    // TODO: Implement create prompt dialog
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Prompt oluşturma özelliği yakında geliyor!'),
        backgroundColor: AppTheme.neonColors.blue,
      ),
    );
  }

  void _showPromptDetails(AIPromptData prompt) {
    // TODO: Implement prompt details dialog
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('${prompt.name} detayları yakında geliyor!'),
        backgroundColor: AppTheme.neonColors.purple,
      ),
    );
  }
} 