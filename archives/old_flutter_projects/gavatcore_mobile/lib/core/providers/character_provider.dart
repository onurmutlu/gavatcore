import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/character.dart';
import '../services/api_service.dart';

// Selected character state
final selectedCharacterProvider = StateProvider<Character?>((ref) => null);

// Characters state
class CharactersState {
  final List<Character> characters;
  final bool isLoading;
  final String? error;
  final bool isSaving;

  const CharactersState({
    this.characters = const [],
    this.isLoading = false,
    this.error,
    this.isSaving = false,
  });

  CharactersState copyWith({
    List<Character>? characters,
    bool? isLoading,
    String? error,
    bool? isSaving,
  }) {
    return CharactersState(
      characters: characters ?? this.characters,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      isSaving: isSaving ?? this.isSaving,
    );
  }
}

// Characters notifier
class CharactersNotifier extends StateNotifier<CharactersState> {
  final ApiService _apiService;

  CharactersNotifier(this._apiService) : super(const CharactersState()) {
    loadCharacters();
  }

  Future<void> loadCharacters() async {
    print('🔄 CharacterProvider: Starting to load characters...');
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      print('🔄 CharacterProvider: Calling API service...');
      final response = await _apiService.getCharacters();
      print('📦 CharacterProvider: API Response: $response');
      
      if (response['success'] == true) {
        final List<dynamic> charactersData = response['characters'] ?? [];
        print('📋 CharacterProvider: Found ${charactersData.length} characters');
        
        final characters = charactersData
            .map((data) => Character.fromJson(data as Map<String, dynamic>))
            .toList();
        
        print('✅ CharacterProvider: Successfully parsed ${characters.length} characters');
        for (final char in characters) {
          print('   - ${char.name} (@${char.id}): ${char.mode} mode, ${char.tone} tone');
        }
        
        state = state.copyWith(
          characters: characters,
          isLoading: false,
        );
      } else {
        throw Exception(response['message'] ?? 'Karakterler yüklenemedi');
      }
    } catch (e, stack) {
      print('❌ CharacterProvider: Error loading characters: $e');
      print('📍 CharacterProvider: Stack trace: $stack');
      state = state.copyWith(
        isLoading: false,
        error: 'Karakterler yüklenirken hata oluştu: $e',
      );
    }
  }

  Future<bool> updateCharacter(String characterId, Character updatedCharacter) async {
    state = state.copyWith(isSaving: true, error: null);
    
    try {
      final response = await _apiService.put('/characters/$characterId', {
        'mode': updatedCharacter.mode,
        'tone': updatedCharacter.tone,
        'system_prompt': updatedCharacter.systemPrompt,
        'model': updatedCharacter.model,
        'humanizer': updatedCharacter.humanizer,
      });
      
      if (response['success'] == true) {
        // Update local state
        final updatedCharacters = state.characters.map((char) {
          if (char.id == characterId) {
            return updatedCharacter;
          }
          return char;
        }).toList();
        
        state = state.copyWith(
          characters: updatedCharacters,
          isSaving: false,
        );
        
        return true;
      } else {
        throw Exception(response['message'] ?? 'Karakter güncellenemedi');
      }
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        error: 'Karakter güncellenirken hata oluştu: $e',
      );
      return false;
    }
  }

  Future<Map<String, dynamic>> testReply(String characterId, String message) async {
    try {
      final response = await _apiService.post('/characters/$characterId/test', {
        'message': message,
      });
      return response;
    } catch (e) {
      throw Exception('Test mesajı gönderilirken hata oluştu: $e');
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

// Characters provider
final charactersProvider = StateNotifierProvider<CharactersNotifier, CharactersState>((ref) {
  final apiService = ref.watch(apiServiceProvider);
  return CharactersNotifier(apiService);
}); 