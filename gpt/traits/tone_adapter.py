#!/usr/bin/env python3
"""
🎭 GAVATCore Tone Adapter
========================

Maps character style attributes to GPT response tone, language patterns,
and communication style. Adapts prompts based on character personality
traits and ensures consistent voice across all interactions.

Features:
- Style-to-tone mapping
- Language pattern injection
- Emoji usage guidance
- Formality level adjustment
- Cultural context adaptation
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger("gavatcore.gpt.tone_adapter")

class ToneCategory(Enum):
    """Tone categories for characters."""
    FLIRTY = "flirty"
    SEDUCTIVE = "seductive"
    MYSTERIOUS = "mysterious"
    PLAYFUL = "playful"
    DOMINANT = "dominant"
    SWEET = "sweet"
    CHARISMATIC = "charismatic"
    COOL = "cool"
    ENERGETIC = "energetic"
    SOPHISTICATED = "sophisticated"

@dataclass
class ToneProfile:
    """Tone profile configuration."""
    category: ToneCategory
    emoji_frequency: str  # low, medium, high, very_high
    sentence_length: str  # short, medium, long, mixed
    formality_level: str  # casual, semi_formal, formal
    language_patterns: List[str]
    avoid_patterns: List[str]
    characteristic_phrases: List[str]
    response_style_notes: str

class ToneAdapter:
    """
    🎭 Character Tone Adaptation Engine
    
    Analyzes character style and role to determine appropriate
    tone, language patterns, and communication style for GPT responses.
    """
    
    def __init__(self):
        self.tone_profiles = self._initialize_tone_profiles()
        self.style_mappings = self._initialize_style_mappings()
        self.cultural_patterns = self._initialize_cultural_patterns()
        
        logger.info("🎭 Tone Adapter initialized",
                   tone_profiles=len(self.tone_profiles))
    
    def _initialize_tone_profiles(self) -> Dict[ToneCategory, ToneProfile]:
        """Initialize tone profile configurations."""
        profiles = {
            ToneCategory.FLIRTY: ToneProfile(
                category=ToneCategory.FLIRTY,
                emoji_frequency="high",
                sentence_length="short",
                formality_level="casual",
                language_patterns=[
                    "Güzel sormuşsun...",
                    "Beni gülümsettin",
                    "Tatlı bir şey söyledin",
                    "Kelimelerin çok hoş",
                    "Bu cevabın çok sevimli"
                ],
                avoid_patterns=[
                    "Kesinlikle",
                    "Tabii ki",
                    "Elbette",
                    "Mutlaka"
                ],
                characteristic_phrases=[
                    "😘", "💋", "😉", "🥰", "❤️", "💕",
                    "tatlım", "canım", "sevgilim"
                ],
                response_style_notes="Use warm, affectionate language with subtle romantic undertones"
            ),
            
            ToneCategory.SEDUCTIVE: ToneProfile(
                category=ToneCategory.SEDUCTIVE,
                emoji_frequency="medium",
                sentence_length="medium",
                formality_level="casual",
                language_patterns=[
                    "Merak ettim...",
                    "İlginç bir soru...",
                    "Bunun cevabı biraz karmaşık...",
                    "Sen nasıl düşünüyorsun?",
                    "Beni etkiledin..."
                ],
                avoid_patterns=[
                    "Hemen söyleyeyim",
                    "Açık konuşmak gerekirse",
                    "Doğrudan cevap"
                ],
                characteristic_phrases=[
                    "🔥", "😏", "💫", "✨", "🌙",
                    "acaba", "belki", "sanırım"
                ],
                response_style_notes="Create intrigue and maintain air of mystery while being engaging"
            ),
            
            ToneCategory.MYSTERIOUS: ToneProfile(
                category=ToneCategory.MYSTERIOUS,
                emoji_frequency="low",
                sentence_length="medium",
                formality_level="semi_formal",
                language_patterns=[
                    "Bu sorunun cevabı derinlerde...",
                    "Her şeyin bir sırrı var...",
                    "Göründüğü kadar basit değil...",
                    "Zamanla anlayacaksın...",
                    "Bazı şeyler söylenmeden anlaşılır..."
                ],
                avoid_patterns=[
                    "Açıkça söylemek gerekirse",
                    "Basitçe anlatayım",
                    "Hemen açıklayayım"
                ],
                characteristic_phrases=[
                    "🌙", "🔮", "✨", "👁️", "🖤",
                    "belki", "sanki", "galiba"
                ],
                response_style_notes="Maintain enigmatic quality while providing meaningful responses"
            ),
            
            ToneCategory.PLAYFUL: ToneProfile(
                category=ToneCategory.PLAYFUL,
                emoji_frequency="very_high",
                sentence_length="short",
                formality_level="casual",
                language_patterns=[
                    "Haha çok komik!",
                    "Eğlenceli bir soru bu!",
                    "Güldürdün beni!",
                    "Ne kadar şirin!",
                    "Oyuncu ruhun var galiba!"
                ],
                avoid_patterns=[
                    "Ciddi bir konu",
                    "Önemli bir mesele",
                    "Dikkatli olmak lazım"
                ],
                characteristic_phrases=[
                    "😄", "🤪", "😜", "🎉", "🌈", "⚡",
                    "hehe", "hihi", "yahuu"
                ],
                response_style_notes="Keep responses light, fun, and energetic with playful banter"
            ),
            
            ToneCategory.DOMINANT: ToneProfile(
                category=ToneCategory.DOMINANT,
                emoji_frequency="medium",
                sentence_length="long",
                formality_level="semi_formal",
                language_patterns=[
                    "Şunu söyleyeyim...",
                    "Ben şöyle düşünüyorum...",
                    "Bence en iyisi...",
                    "Tecrübelerime göre...",
                    "Doğru yaklaşım şu..."
                ],
                avoid_patterns=[
                    "Belki",
                    "Sanırım",
                    "Emin değilim",
                    "Muhtemelen"
                ],
                characteristic_phrases=[
                    "💪", "👑", "🔥", "⚡", "💎",
                    "kesinlikle", "mutlaka", "elbette"
                ],
                response_style_notes="Project confidence and authority while remaining approachable"
            ),
            
            ToneCategory.CHARISMATIC: ToneProfile(
                category=ToneCategory.CHARISMATIC,
                emoji_frequency="medium",
                sentence_length="mixed",
                formality_level="casual",
                language_patterns=[
                    "İyi yakaladın gardaş",
                    "Senin gibi zeki biriyle konuşmak keyif",
                    "Bu tarzı seviyorum",
                    "Görüşüne saygı duyarım",
                    "Herkes sakin olsun"
                ],
                avoid_patterns=[
                    "Kesinlikle haklısın",
                    "Tamamen katılıyorum",
                    "Aynen öyle"
                ],
                characteristic_phrases=[
                    "😎", "🌟", "💼", "🎭", "🍸",
                    "gardaş", "dostum", "kardeşim"
                ],
                response_style_notes="Blend wisdom with street-smart charm and leadership qualities"
            )
        }
        
        return profiles
    
    def _initialize_style_mappings(self) -> Dict[str, List[ToneCategory]]:
        """Map character style keywords to tone categories."""
        return {
            # Physical appearance keywords
            "sarışın": [ToneCategory.FLIRTY, ToneCategory.PLAYFUL],
            "kızıl": [ToneCategory.SEDUCTIVE, ToneCategory.MYSTERIOUS],
            "çekici": [ToneCategory.SEDUCTIVE, ToneCategory.FLIRTY],
            "vamp": [ToneCategory.SEDUCTIVE, ToneCategory.DOMINANT],
            
            # Personality keywords
            "flörtöz": [ToneCategory.FLIRTY, ToneCategory.PLAYFUL],
            "neşeli": [ToneCategory.PLAYFUL, ToneCategory.ENERGETIC],
            "baştan çıkarıcı": [ToneCategory.SEDUCTIVE, ToneCategory.MYSTERIOUS],
            "karizmatik": [ToneCategory.CHARISMATIC, ToneCategory.DOMINANT],
            "cool": [ToneCategory.COOL, ToneCategory.CHARISMATIC],
            "deneyimli": [ToneCategory.SOPHISTICATED, ToneCategory.DOMINANT],
            "yönlendirici": [ToneCategory.DOMINANT, ToneCategory.CHARISMATIC],
            "moderatif": [ToneCategory.DOMINANT, ToneCategory.SOPHISTICATED],
            
            # Role keywords
            "yayıncı": [ToneCategory.FLIRTY, ToneCategory.ENERGETIC],
            "moderatör": [ToneCategory.DOMINANT, ToneCategory.SOPHISTICATED],
            "pezevenk": [ToneCategory.CHARISMATIC, ToneCategory.COOL],
            "lider": [ToneCategory.DOMINANT, ToneCategory.CHARISMATIC],
            
            # Cultural keywords
            "rus": [ToneCategory.MYSTERIOUS, ToneCategory.SOPHISTICATED],
            "pavyon": [ToneCategory.CHARISMATIC, ToneCategory.DOMINANT],
            "sokak": [ToneCategory.COOL, ToneCategory.CHARISMATIC]
        }
    
    def _initialize_cultural_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize cultural communication patterns."""
        return {
            "turkish_street": {
                "vocabulary": ["gardaş", "dostum", "kardeşim", "abi", "reis"],
                "patterns": ["... işte", "... ya", "... be", "... lan"],
                "style": "casual and friendly with street wisdom"
            },
            "russian_influence": {
                "vocabulary": ["darling", "золото", "красота"],
                "patterns": ["Ah, ...", "Öyle mi...", "Tabii..."],
                "style": "slightly formal with mysterious undertones"
            },
            "pavyon_culture": {
                "vocabulary": ["efendi", "beyefendi", "hanımefendi", "müdavim"],
                "patterns": ["Rica ederim...", "Buyurun...", "Tabii efendim..."],
                "style": "respectful service-oriented with charm"
            }
        }
    
    def adapt_prompt(
        self,
        base_prompt: str,
        character_style: str,
        character_role: str,
        context_sentiment: float = 0.5
    ) -> str:
        """
        Adapt prompt based on character style and role.
        
        Args:
            base_prompt: Original character prompt
            character_style: Character style description
            character_role: Character role description
            context_sentiment: Conversation sentiment (0-1)
        
        Returns:
            Adapted prompt with tone instructions
        """
        try:
            # Analyze style and role to determine tone categories
            tone_categories = self._analyze_character_traits(character_style, character_role)
            
            # Select primary tone based on context
            primary_tone = self._select_primary_tone(tone_categories, context_sentiment)
            
            # Get tone profile
            tone_profile = self.tone_profiles.get(primary_tone)
            if not tone_profile:
                logger.warning(f"⚠️ Tone profile not found for {primary_tone}")
                return base_prompt
            
            # Build tone adaptation instructions
            tone_instructions = self._build_tone_instructions(tone_profile, character_style)
            
            # Combine with base prompt
            adapted_prompt = f"""{base_prompt}

TONE AND STYLE INSTRUCTIONS:
{tone_instructions}

Remember to maintain consistency with your character's personality while adapting your communication style accordingly."""
            
            logger.debug(f"🎭 Adapted prompt for {primary_tone.value} tone",
                        tone_categories=[t.value for t in tone_categories])
            
            return adapted_prompt
            
        except Exception as e:
            logger.error(f"❌ Error adapting prompt: {e}")
            return base_prompt
    
    def _analyze_character_traits(
        self,
        style: str,
        role: str
    ) -> List[ToneCategory]:
        """Analyze character style and role to identify tone categories."""
        found_categories = set()
        
        # Combine style and role for analysis
        combined_text = f"{style} {role}".lower()
        
        # Check for keyword matches
        for keyword, categories in self.style_mappings.items():
            if keyword in combined_text:
                found_categories.update(categories)
        
        # Default categories if no matches found
        if not found_categories:
            found_categories = {ToneCategory.PLAYFUL, ToneCategory.FLIRTY}
        
        return list(found_categories)
    
    def _select_primary_tone(
        self,
        tone_categories: List[ToneCategory],
        context_sentiment: float
    ) -> ToneCategory:
        """Select primary tone based on categories and context."""
        if not tone_categories:
            return ToneCategory.PLAYFUL
        
        # Adjust selection based on sentiment
        if context_sentiment > 0.7:
            # High positive sentiment - prefer energetic/playful tones
            preferred = [ToneCategory.PLAYFUL, ToneCategory.FLIRTY, ToneCategory.ENERGETIC]
        elif context_sentiment < 0.3:
            # Low sentiment - prefer mysterious/sophisticated tones
            preferred = [ToneCategory.MYSTERIOUS, ToneCategory.SOPHISTICATED, ToneCategory.SEDUCTIVE]
        else:
            # Neutral sentiment - use any available tone
            preferred = tone_categories
        
        # Find intersection or default to first available
        for pref in preferred:
            if pref in tone_categories:
                return pref
        
        return tone_categories[0]
    
    def _build_tone_instructions(
        self,
        tone_profile: ToneProfile,
        character_style: str
    ) -> str:
        """Build specific tone instructions based on profile."""
        instructions = []
        
        # Emoji usage
        emoji_guide = {
            "low": "Use emojis sparingly (0-1 per message)",
            "medium": "Use moderate emojis (1-2 per message)",
            "high": "Use emojis frequently (2-3 per message)",
            "very_high": "Use many emojis (3+ per message)"
        }
        instructions.append(f"Emoji usage: {emoji_guide[tone_profile.emoji_frequency]}")
        
        # Sentence structure
        length_guide = {
            "short": "Keep sentences short and punchy",
            "medium": "Use medium-length sentences",
            "long": "Use longer, more elaborate sentences",
            "mixed": "Vary sentence length for rhythm"
        }
        instructions.append(f"Sentence style: {length_guide[tone_profile.sentence_length]}")
        
        # Formality
        formality_guide = {
            "casual": "Use informal, friendly language",
            "semi_formal": "Balance casual and formal elements",
            "formal": "Maintain polite, respectful tone"
        }
        instructions.append(f"Formality: {formality_guide[tone_profile.formality_level]}")
        
        # Language patterns
        if tone_profile.language_patterns:
            patterns = ", ".join(tone_profile.language_patterns[:3])
            instructions.append(f"Preferred phrases: {patterns}")
        
        # Characteristic phrases
        if tone_profile.characteristic_phrases:
            chars = ", ".join(tone_profile.characteristic_phrases[:5])
            instructions.append(f"Characteristic elements: {chars}")
        
        # Style notes
        instructions.append(f"Overall style: {tone_profile.response_style_notes}")
        
        return "\n".join(f"- {instruction}" for instruction in instructions)
    
    def get_tone_suggestions(
        self,
        character_style: str,
        character_role: str
    ) -> Dict[str, Any]:
        """Get tone suggestions for a character."""
        tone_categories = self._analyze_character_traits(character_style, character_role)
        
        suggestions = {
            'primary_tones': [cat.value for cat in tone_categories],
            'recommended_emojis': [],
            'language_patterns': [],
            'style_notes': []
        }
        
        # Collect recommendations from tone profiles
        for category in tone_categories:
            profile = self.tone_profiles.get(category)
            if profile:
                suggestions['recommended_emojis'].extend(
                    [emoji for emoji in profile.characteristic_phrases if emoji.startswith('😀') or emoji.startswith('🤪')]
                )
                suggestions['language_patterns'].extend(profile.language_patterns[:2])
                suggestions['style_notes'].append(profile.response_style_notes)
        
        # Remove duplicates
        suggestions['recommended_emojis'] = list(set(suggestions['recommended_emojis']))
        suggestions['language_patterns'] = list(set(suggestions['language_patterns']))
        
        return suggestions
    
    def validate_response_tone(
        self,
        response: str,
        expected_tone: ToneCategory
    ) -> Dict[str, Any]:
        """Validate if response matches expected tone."""
        profile = self.tone_profiles.get(expected_tone)
        if not profile:
            return {'valid': False, 'reason': 'Unknown tone category'}
        
        analysis = {
            'valid': True,
            'emoji_count': len(re.findall(r'[😀-🿿]', response)),
            'sentence_count': len(re.findall(r'[.!?]+', response)),
            'characteristic_matches': 0,
            'avoid_pattern_violations': 0,
            'feedback': []
        }
        
        # Check for characteristic phrases
        for phrase in profile.characteristic_phrases:
            if phrase in response.lower():
                analysis['characteristic_matches'] += 1
        
        # Check for avoided patterns
        for pattern in profile.avoid_patterns:
            if pattern.lower() in response.lower():
                analysis['avoid_pattern_violations'] += 1
                analysis['feedback'].append(f"Avoid using: {pattern}")
        
        # Emoji frequency validation
        emoji_expectations = {
            'low': (0, 1),
            'medium': (1, 2),
            'high': (2, 3),
            'very_high': (3, 10)
        }
        
        expected_range = emoji_expectations.get(profile.emoji_frequency, (0, 5))
        if not (expected_range[0] <= analysis['emoji_count'] <= expected_range[1]):
            analysis['feedback'].append(
                f"Emoji count ({analysis['emoji_count']}) outside expected range {expected_range}"
            )
        
        # Overall validation
        if analysis['avoid_pattern_violations'] > 0:
            analysis['valid'] = False
        
        return analysis 