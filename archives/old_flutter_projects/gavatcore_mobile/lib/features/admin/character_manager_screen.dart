import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/themes/app_colors.dart';
import '../../core/models/character.dart';
import '../../core/providers/character_provider.dart';

class CharacterManagerScreen extends ConsumerStatefulWidget {
  const CharacterManagerScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<CharacterManagerScreen> createState() => _CharacterManagerScreenState();
}

class _CharacterManagerScreenState extends ConsumerState<CharacterManagerScreen> {
  final _formKey = GlobalKey<FormState>();
  final _systemPromptController = TextEditingController();
  
  String? _selectedMode;
  String? _selectedTone;
  String? _selectedModel;
  bool _humanizerEnabled = false;

  @override
  void dispose() {
    _systemPromptController.dispose();
    super.dispose();
  }

  void _loadCharacterData(Character character) {
    setState(() {
      _selectedMode = character.mode;
      _selectedTone = character.tone;
      _selectedModel = character.model;
      _humanizerEnabled = character.humanizer;
      _systemPromptController.text = character.systemPrompt;
    });
  }

  Future<void> _saveCharacter() async {
    final selectedCharacter = ref.read(selectedCharacterProvider);
    if (selectedCharacter == null || !_formKey.currentState!.validate()) {
      return;
    }

    final updatedCharacter = selectedCharacter.copyWith(
      mode: _selectedMode!,
      tone: _selectedTone!,
      model: _selectedModel!,
      systemPrompt: _systemPromptController.text,
      humanizer: _humanizerEnabled,
    );

    final success = await ref
        .read(charactersProvider.notifier)
        .updateCharacter(selectedCharacter.id, updatedCharacter);

    if (success && mounted) {
      // Update selected character
      ref.read(selectedCharacterProvider.notifier).state = updatedCharacter;
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('✅ Ayarlar başarıyla kaydedildi'),
          backgroundColor: AppColors.success,
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final charactersState = ref.watch(charactersProvider);
    final selectedCharacter = ref.watch(selectedCharacterProvider);

    // Show error if exists
    ref.listen(charactersProvider, (previous, next) {
      if (next.error != null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ ${next.error}'),
            backgroundColor: AppColors.error,
            behavior: SnackBarBehavior.floating,
          ),
        );
        ref.read(charactersProvider.notifier).clearError();
      }
    });

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        title: const Text(
          '🎭 Karakter Yönetimi',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.read(charactersProvider.notifier).loadCharacters(),
            tooltip: 'Yenile',
          ),
        ],
        elevation: 0,
      ),
      body: charactersState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : Row(
              children: [
                // Character List Panel
                SizedBox(
                  width: 300,
                  child: _buildCharacterList(charactersState.characters),
                ),
                
                // Form Panel
                Expanded(
                  child: selectedCharacter == null
                      ? _buildEmptyState()
                      : _buildCharacterForm(selectedCharacter),
                ),
              ],
            ),
    );
  }

  Widget _buildCharacterList(List<Character> characters) {
    final selectedCharacter = ref.watch(selectedCharacterProvider);

    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border(right: BorderSide(color: AppColors.border)),
      ),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              'Karakterler (${characters.length})',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
          ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              itemCount: characters.length,
              itemBuilder: (context, index) {
                final character = characters[index];
                final isSelected = selectedCharacter?.id == character.id;
                
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  color: isSelected 
                      ? AppColors.primary.withOpacity(0.1)
                      : AppColors.background,
                  elevation: isSelected ? 4 : 1,
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: _getCharacterColor(character.id),
                      child: Text(
                        _getCharacterEmoji(character.id),
                        style: const TextStyle(fontSize: 18),
                      ),
                    ),
                    title: Text(
                      character.name,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '@${character.id}',
                          style: TextStyle(color: AppColors.textSecondary),
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            _buildStatusChip(character.mode, AppColors.info),
                            const SizedBox(width: 4),
                            _buildStatusChip(
                              CharacterModel.getDisplayName(character.model),
                              AppColors.warning,
                            ),
                          ],
                        ),
                      ],
                    ),
                    onTap: () {
                      ref.read(selectedCharacterProvider.notifier).state = character;
                      _loadCharacterData(character);
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

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.person_search,
            size: 64,
            color: AppColors.textSecondary,
          ),
          const SizedBox(height: 16),
          Text(
            'Karakter Seçin',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Soldan bir karakter seçerek ayarlarını düzenleyebilirsiniz',
            style: TextStyle(color: AppColors.textSecondary),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildCharacterForm(Character character) {
    final charactersState = ref.watch(charactersProvider);

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  CircleAvatar(
                    backgroundColor: _getCharacterColor(character.id),
                    radius: 24,
                    child: Text(
                      _getCharacterEmoji(character.id),
                      style: const TextStyle(fontSize: 24),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        character.name,
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '@${character.id}',
                        style: TextStyle(
                          color: AppColors.textSecondary,
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              
              const SizedBox(height: 32),
              
              // Form Fields
              Row(
                children: [
                  Expanded(
                    child: _buildDropdownField(
                      label: 'Mod',
                      value: _selectedMode,
                      items: CharacterMode.values,
                      itemBuilder: (mode) => CharacterMode.getDisplayName(mode),
                      onChanged: (value) => setState(() => _selectedMode = value),
                      validator: (value) => value == null ? 'Mod seçiniz' : null,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildDropdownField(
                      label: 'Ton',
                      value: _selectedTone,
                      items: CharacterTone.values,
                      itemBuilder: (tone) => CharacterTone.getDisplayName(tone),
                      onChanged: (value) => setState(() => _selectedTone = value),
                      validator: (value) => value == null ? 'Ton seçiniz' : null,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 24),
              
              _buildDropdownField(
                label: 'Model',
                value: _selectedModel,
                items: CharacterModel.values,
                itemBuilder: (model) => CharacterModel.getDisplayName(model),
                onChanged: (value) => setState(() => _selectedModel = value),
                validator: (value) => value == null ? 'Model seçiniz' : null,
              ),
              
              const SizedBox(height: 24),
              
              // Humanizer Toggle
              SwitchListTile(
                title: const Text('Humanizer'),
                subtitle: const Text('Mesajlara doğal delay ve variasyon ekler'),
                value: _humanizerEnabled,
                onChanged: (value) => setState(() => _humanizerEnabled = value),
                activeColor: AppColors.success,
                contentPadding: EdgeInsets.zero,
              ),
              
              const SizedBox(height: 24),
              
              // System Prompt
              TextFormField(
                controller: _systemPromptController,
                decoration: InputDecoration(
                  labelText: 'System Prompt',
                  hintText: 'Karakterin davranış talimatlarını girin...',
                  alignLabelWithHint: true,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  filled: true,
                  fillColor: AppColors.surface,
                ),
                maxLines: 8,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'System prompt gereklidir';
                  }
                  if (value.length < 20) {
                    return 'System prompt en az 20 karakter olmalıdır';
                  }
                  return null;
                },
              ),
              
              const SizedBox(height: 32),
              
              // Save Button
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton.icon(
                  onPressed: charactersState.isSaving ? null : _saveCharacter,
                  icon: charactersState.isSaving
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.save),
                  label: Text(
                    charactersState.isSaving ? 'Kaydediliyor...' : 'Kaydet',
                    style: const TextStyle(fontSize: 16),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDropdownField<T>({
    required String label,
    required T? value,
    required List<T> items,
    required String Function(T) itemBuilder,
    required void Function(T?) onChanged,
    String? Function(T?)? validator,
  }) {
    return DropdownButtonFormField<T>(
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        filled: true,
        fillColor: AppColors.surface,
      ),
      value: value,
      items: items
          .map((item) => DropdownMenuItem<T>(
                value: item,
                child: Text(itemBuilder(item)),
              ))
          .toList(),
      onChanged: onChanged,
      validator: validator,
    );
  }

  Widget _buildStatusChip(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.bold,
          color: color,
        ),
      ),
    );
  }

  Color _getCharacterColor(String characterId) {
    switch (characterId.toLowerCase()) {
      case 'lara':
      case 'yayincilara':
        return Colors.pink;
      case 'babagavat':
        return Colors.orange;
      case 'geisha':
      case 'xxxgeisha':
        return Colors.purple;
      case 'balkiz':
        return Colors.blue;
      default:
        return AppColors.primary;
    }
  }

  String _getCharacterEmoji(String characterId) {
    switch (characterId.toLowerCase()) {
      case 'lara':
      case 'yayincilara':
        return '💋';
      case 'babagavat':
        return '😤';
      case 'geisha':
      case 'xxxgeisha':
        return '🌸';
      case 'balkiz':
        return '💫';
      default:
        return '🎭';
    }
  }
} 