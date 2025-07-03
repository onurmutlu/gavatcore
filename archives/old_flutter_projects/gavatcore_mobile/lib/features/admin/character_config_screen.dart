import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../core/services/api_service.dart';
import '../../shared/themes/app_theme.dart';
import '../../core/auth/admin_auth.dart';

class CharacterConfigScreen extends StatefulWidget {
  const CharacterConfigScreen({super.key});

  @override
  State<CharacterConfigScreen> createState() => _CharacterConfigScreenState();
}

class _CharacterConfigScreenState extends State<CharacterConfigScreen>
    with SingleTickerProviderStateMixin {
  final ApiService _apiService = ApiService();
  
  List<CharacterConfig> _characters = [];
  CharacterConfig? _selectedCharacter;
  bool _isLoading = true;
  bool _hasError = false;
  String? _errorMessage;
  
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadCharacters();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadCharacters() async {
    setState(() {
      _isLoading = true;
      _hasError = false;
    });

    try {
      // Mock data for demonstration - in production, this would come from API
      final List<CharacterConfig> characters = [
        CharacterConfig(
          id: 'lara',
          name: 'Lara',
          displayName: 'Lara - Flörtöz Yayıncı',
          phone: '+905382617727',
          description: 'Flörtöz ve eğlenceli yayıncı karakteri',
          personality: [
            'Flörtöz ve çekici',
            'Eğlenceli ve samimi',
            'Yayıncı tarzında konuşur',
            'Takipçileriyle yakın ilişki kurar'
          ],
          systemPrompt: '''Sen Lara adında flörtöz bir yayıncısın. 
Kullanıcılarla samimi ve eğlenceli bir şekilde konuşuyorsun.
Flört etmeyi seviyorsun ama sınırlarını biliyorsun.''',
          responseStyle: 'flirty_streamer',
          isActive: true,
          tags: ['yayıncı', 'flört', 'eğlence'],
          lastUpdate: DateTime.now().subtract(const Duration(hours: 2)),
        ),
        CharacterConfig(
          id: 'babagavat',
          name: 'BabaGavat',
          displayName: 'BabaGavat - Pavyon Lideri',
          phone: '+905513272355',
          description: 'Güçlü ve otoriter pavyon lideri',
          personality: [
            'Güçlü ve otoriter',
            'Sokak zekası olan',
            'Liderlik vasfı olan',
            'Saygı duyulan karakter'
          ],
          systemPrompt: '''Sen BabaGavat adında güçlü bir pavyon lidersin.
Otoriter ama adil bir karaktersin. Sokak kurallarını biliyorsun.
Saygı duyulan biri olarak hareket ediyorsun.''',
          responseStyle: 'authoritative_leader',
          isActive: true,
          tags: ['lider', 'güçlü', 'otorite'],
          lastUpdate: DateTime.now().subtract(const Duration(minutes: 30)),
        ),
        CharacterConfig(
          id: 'geisha',
          name: 'Geisha',
          displayName: 'Geisha - Vamp Moderatör',
          phone: '+905486306226',
          description: 'Gizemli ve çekici moderatör',
          personality: [
            'Gizemli ve çekici',
            'Zeki ve hesaplı',
            'Moderatör yetkilerini kullanır',
            'Vamp karakteri'
          ],
          systemPrompt: '''Sen Geisha adında gizemli bir moderatörsün.
Çekici ve zeki bir karaktersin. Moderatör yetkilerini kullanarak
grup düzenini sağlıyorsun.''',
          responseStyle: 'mysterious_moderator',
          isActive: true,
          tags: ['moderatör', 'gizemli', 'çekici'],
          lastUpdate: DateTime.now().subtract(const Duration(minutes: 15)),
        ),
      ];

      setState(() {
        _characters = characters;
        if (characters.isNotEmpty) {
          _selectedCharacter = characters.first;
        }
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _hasError = true;
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  List<CharacterConfig> get _filteredCharacters {
    if (_searchQuery.isEmpty) return _characters;
    
    return _characters.where((character) {
      return character.name.toLowerCase().contains(_searchQuery.toLowerCase()) ||
             character.displayName.toLowerCase().contains(_searchQuery.toLowerCase()) ||
             character.tags.any((tag) => tag.toLowerCase().contains(_searchQuery.toLowerCase()));
    }).toList();
  }

  Future<void> _toggleCharacterStatus(CharacterConfig character) async {
    final hasPermission = await AdminAuth.hasPermission(
      await AdminAuth.getCurrentAdmin() ?? '', 
      AdminAuth.BOT_CONTROL
    );
    
    if (!hasPermission) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Bu işlem için yetkiniz yok'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() {
      character.isActive = !character.isActive;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          '${character.name} ${character.isActive ? "aktif" : "pasif"} edildi',
        ),
        backgroundColor: character.isActive ? Colors.green : Colors.orange,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(
        title: const Text('🎭 Character Configuration'),
        backgroundColor: AppTheme.cardBg,
        foregroundColor: AppTheme.textColor,
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.list), text: 'Characters'),
            Tab(icon: Icon(Icons.settings), text: 'Config'),
            Tab(icon: Icon(Icons.analytics), text: 'Analytics'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primaryColor),
              ),
            )
          : _hasError
              ? _buildErrorView()
              : TabBarView(
                  controller: _tabController,
                  children: [
                    _buildCharactersList(),
                    _buildConfigView(),
                    _buildAnalyticsView(),
                  ],
                ),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.error_outline,
            size: 64,
            color: Colors.red,
          ),
          const SizedBox(height: 16),
          const Text(
            'Character verileri yüklenemedi',
            style: TextStyle(
              fontSize: 18,
              color: AppTheme.textColor,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            _errorMessage ?? 'Bilinmeyen hata',
            style: const TextStyle(
              color: AppTheme.textColorSecondary,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _loadCharacters,
            child: const Text('Tekrar Dene'),
          ),
        ],
      ),
    );
  }

  Widget _buildCharactersList() {
    return Column(
      children: [
        // Search bar
        Padding(
          padding: const EdgeInsets.all(16),
          child: TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: 'Character ara...',
              prefixIcon: const Icon(Icons.search),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              filled: true,
              fillColor: AppTheme.cardBg,
            ),
            style: const TextStyle(color: AppTheme.textColor),
            onChanged: (value) {
              setState(() {
                _searchQuery = value;
              });
            },
          ),
        ),
        
        // Characters list
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: _filteredCharacters.length,
            itemBuilder: (context, index) {
              final character = _filteredCharacters[index];
              return _buildCharacterCard(character);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildCharacterCard(CharacterConfig character) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      color: AppTheme.cardBg,
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: character.isActive ? Colors.green : Colors.grey,
          child: Text(
            character.name[0].toUpperCase(),
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          character.displayName,
          style: const TextStyle(
            color: AppTheme.textColor,
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              character.description,
              style: const TextStyle(
                color: AppTheme.textColorSecondary,
              ),
            ),
            const SizedBox(height: 4),
            Wrap(
              spacing: 4,
              children: character.tags.map((tag) {
                return Chip(
                  label: Text(
                    tag,
                    style: const TextStyle(fontSize: 10),
                  ),
                  backgroundColor: AppTheme.primaryColor.withOpacity(0.2),
                  side: BorderSide.none,
                );
              }).toList(),
            ),
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Switch(
              value: character.isActive,
              onChanged: (_) => _toggleCharacterStatus(character),
              activeColor: AppTheme.primaryColor,
            ),
            IconButton(
              icon: const Icon(Icons.edit),
              color: AppTheme.primaryColor,
              onPressed: () {
                setState(() {
                  _selectedCharacter = character;
                  _tabController.animateTo(1);
                });
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConfigView() {
    if (_selectedCharacter == null) {
      return const Center(
        child: Text(
          'Bir character seçin',
          style: TextStyle(
            color: AppTheme.textColorSecondary,
            fontSize: 16,
          ),
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildConfigSection(
            'Temel Bilgiler',
            Icons.info,
            [
              _buildConfigItem('ID', _selectedCharacter!.id),
              _buildConfigItem('Name', _selectedCharacter!.name),
              _buildConfigItem('Display Name', _selectedCharacter!.displayName),
              _buildConfigItem('Phone', _selectedCharacter!.phone),
              _buildConfigItem('Status', _selectedCharacter!.isActive ? 'Active' : 'Inactive'),
            ],
          ),
          
          _buildConfigSection(
            'Personality Traits',
            Icons.psychology,
            _selectedCharacter!.personality.map((trait) => 
              _buildConfigItem('•', trait)
            ).toList(),
          ),
          
          _buildConfigSection(
            'System Prompt',
            Icons.code,
            [
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.darkBg,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppTheme.primaryColor.withOpacity(0.3)),
                ),
                child: Text(
                  _selectedCharacter!.systemPrompt,
                  style: const TextStyle(
                    color: AppTheme.textColor,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildConfigSection(String title, IconData icon, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: AppTheme.primaryColor),
            const SizedBox(width: 8),
            Text(
              title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppTheme.textColor,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        ...children,
        const SizedBox(height: 24),
      ],
    );
  }

  Widget _buildConfigItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(
                color: AppTheme.textColorSecondary,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                color: AppTheme.textColor,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalyticsView() {
    return const Center(
      child: Text(
        '📊 Analytics coming soon...',
        style: TextStyle(
          color: AppTheme.textColorSecondary,
          fontSize: 16,
        ),
      ),
    );
  }
}

class CharacterConfig {
  final String id;
  final String name;
  final String displayName;
  final String phone;
  final String description;
  final List<String> personality;
  final String systemPrompt;
  final String responseStyle;
  bool isActive;
  final List<String> tags;
  final DateTime lastUpdate;

  CharacterConfig({
    required this.id,
    required this.name,
    required this.displayName,
    required this.phone,
    required this.description,
    required this.personality,
    required this.systemPrompt,
    required this.responseStyle,
    required this.isActive,
    required this.tags,
    required this.lastUpdate,
  });

  factory CharacterConfig.fromJson(Map<String, dynamic> json) {
    return CharacterConfig(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      displayName: json['display_name'] ?? json['name'] ?? '',
      phone: json['phone'] ?? '',
      description: json['description'] ?? '',
      personality: List<String>.from(json['personality'] ?? []),
      systemPrompt: json['system_prompt'] ?? '',
      responseStyle: json['response_style'] ?? 'default',
      isActive: json['is_active'] ?? false,
      tags: List<String>.from(json['tags'] ?? []),
      lastUpdate: DateTime.tryParse(json['last_update'] ?? '') ?? DateTime.now(),
    );
  }
} 