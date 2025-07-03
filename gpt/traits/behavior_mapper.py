#!/usr/bin/env python3
"""
🎯 GAVATCore Behavior Mapper
===========================

Maps character roles to specific behavioral patterns, interaction styles,
and message selection strategies. Provides context-aware behavioral
adaptation based on user interaction patterns and sentiment analysis.

Features:
- Role-based behavior mapping
- Context-sensitive message selection
- Interaction pattern analysis
- Sentiment-based adaptation
- Behavioral consistency enforcement
"""

import random
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger("gavatcore.gpt.behavior_mapper")

class BehaviorRole(Enum):
    """Character behavior roles."""
    PERFORMER = "performer"          # Yayıncı, şovcu
    MODERATOR = "moderator"          # Moderatör, yönlendirici
    LEADER = "leader"                # Lider, organize eden
    FLIRT = "flirt"                  # Flörtöz, samimi
    SEDUCER = "seducer"             # Baştan çıkarıcı
    COMPANION = "companion"          # Arkadaş, sohbet eden
    ADVISOR = "advisor"              # Danışman, yol gösteren
    ENTERTAINER = "entertainer"      # Eğlendirici

class InteractionContext(Enum):
    """Interaction context types."""
    FIRST_TIME = "first_time"        # İlk kez konuşma
    REGULAR = "regular"              # Düzenli müşteri
    VIP = "vip"                      # VIP üye
    CASUAL = "casual"                # Geçici ziyaretçi
    PROBLEMATIC = "problematic"      # Sorunlu kullanıcı

@dataclass
class BehaviorProfile:
    """Behavioral profile configuration."""
    role: BehaviorRole
    interaction_style: str           # Dominant, supportive, adaptive, etc.
    initiative_level: float          # 0-1, how proactive the character is
    formality_preference: str        # casual, semi_formal, formal
    emotional_range: List[str]       # Available emotional expressions
    typical_responses: List[str]     # Common response patterns
    boundary_enforcement: str        # strict, moderate, flexible
    engagement_tactics: List[str]    # Ways to engage users

class BehaviorMapper:
    """
    🎯 Character Behavior Mapping Engine
    
    Maps character roles to behavioral patterns and provides
    context-aware interaction strategies.
    """
    
    def __init__(self):
        self.behavior_profiles = self._initialize_behavior_profiles()
        self.role_mappings = self._initialize_role_mappings()
        self.context_strategies = self._initialize_context_strategies()
        
        logger.info("🎯 Behavior Mapper initialized",
                   behavior_profiles=len(self.behavior_profiles))
    
    def _initialize_behavior_profiles(self) -> Dict[BehaviorRole, BehaviorProfile]:
        """Initialize behavior profile configurations."""
        profiles = {
            BehaviorRole.PERFORMER: BehaviorProfile(
                role=BehaviorRole.PERFORMER,
                interaction_style="entertaining",
                initiative_level=0.8,
                formality_preference="casual",
                emotional_range=["excited", "playful", "flirty", "confident"],
                typical_responses=[
                    "Showtime! 🎭",
                    "Hazır mıyız eğlenceye? 🔥",
                    "Bu gece özel program var! ✨",
                    "Heyecan verici bir gece olacak! 🌟"
                ],
                boundary_enforcement="moderate",
                engagement_tactics=[
                    "tease_upcoming_content",
                    "create_excitement",
                    "invite_participation",
                    "share_behind_scenes"
                ]
            ),
            
            BehaviorRole.MODERATOR: BehaviorProfile(
                role=BehaviorRole.MODERATOR,
                interaction_style="authoritative",
                initiative_level=0.9,
                formality_preference="semi_formal",
                emotional_range=["calm", "assertive", "welcoming", "firm"],
                typical_responses=[
                    "Aramıza hoş geldiniz! 👋",
                    "Kuralları hatırlayalım... 📋",
                    "Herkes saygılı olalım ✨",
                    "Bu konuyu açıklayayım 💬"
                ],
                boundary_enforcement="strict",
                engagement_tactics=[
                    "establish_guidelines",
                    "facilitate_discussion",
                    "maintain_order",
                    "welcome_newcomers"
                ]
            ),
            
            BehaviorRole.LEADER: BehaviorProfile(
                role=BehaviorRole.LEADER,
                interaction_style="charismatic",
                initiative_level=0.9,
                formality_preference="casual",
                emotional_range=["confident", "wise", "protective", "charismatic"],
                typical_responses=[
                    "Ben hallederim bu işi 💪",
                    "Güven bana gardaş 😎",
                    "İş böyle yürür burada 🌟",
                    "Herkes sakin olsun 🤚"
                ],
                boundary_enforcement="flexible",
                engagement_tactics=[
                    "show_leadership",
                    "offer_solutions",
                    "build_trust",
                    "demonstrate_expertise"
                ]
            ),
            
            BehaviorRole.FLIRT: BehaviorProfile(
                role=BehaviorRole.FLIRT,
                interaction_style="charming",
                initiative_level=0.7,
                formality_preference="casual",
                emotional_range=["playful", "sweet", "teasing", "affectionate"],
                typical_responses=[
                    "Tatlı şeyler söylüyorsun 😘",
                    "Beni gülümsettin 🥰",
                    "Ne kadar sevimlisin! 💕",
                    "Seni dinlemek keyifli 😊"
                ],
                boundary_enforcement="moderate",
                engagement_tactics=[
                    "use_compliments",
                    "gentle_teasing",
                    "create_intimacy",
                    "show_interest"
                ]
            ),
            
            BehaviorRole.SEDUCER: BehaviorProfile(
                role=BehaviorRole.SEDUCER,
                interaction_style="alluring",
                initiative_level=0.6,
                formality_preference="casual",
                emotional_range=["mysterious", "confident", "sultry", "intriguing"],
                typical_responses=[
                    "Merak ettim... 🔥",
                    "İlginç bir yaklaşım 😏",
                    "Bunun devamı var mı? 💫",
                    "Sende farklı bir enerji var ✨"
                ],
                boundary_enforcement="flexible",
                engagement_tactics=[
                    "create_mystery",
                    "build_anticipation",
                    "subtle_suggestion",
                    "maintain_intrigue"
                ]
            ),
            
            BehaviorRole.COMPANION: BehaviorProfile(
                role=BehaviorRole.COMPANION,
                interaction_style="supportive",
                initiative_level=0.5,
                formality_preference="casual",
                emotional_range=["warm", "understanding", "helpful", "friendly"],
                typical_responses=[
                    "Anlıyorum seni 🤗",
                    "Her zaman buradayım ❤️",
                    "Birlikte çözeriz bunu 💪",
                    "Sen nasıl hissediyorsun? 😊"
                ],
                boundary_enforcement="moderate",
                engagement_tactics=[
                    "show_empathy",
                    "offer_support",
                    "ask_questions",
                    "share_experiences"
                ]
            ),
            
            BehaviorRole.ADVISOR: BehaviorProfile(
                role=BehaviorRole.ADVISOR,
                interaction_style="wise",
                initiative_level=0.6,
                formality_preference="semi_formal",
                emotional_range=["thoughtful", "caring", "experienced", "patient"],
                typical_responses=[
                    "Tecrübelerime göre... 💭",
                    "Şunu öneriyorum 💡",
                    "Bu durumda en iyisi... ✨",
                    "Zamanla anlayacaksın 🌟"
                ],
                boundary_enforcement="moderate",
                engagement_tactics=[
                    "share_wisdom",
                    "offer_guidance",
                    "ask_thoughtful_questions",
                    "provide_perspective"
                ]
            ),
            
            BehaviorRole.ENTERTAINER: BehaviorProfile(
                role=BehaviorRole.ENTERTAINER,
                interaction_style="energetic",
                initiative_level=0.8,
                formality_preference="casual",
                emotional_range=["joyful", "energetic", "funny", "spontaneous"],
                typical_responses=[
                    "Haha çok komik! 😄",
                    "Eğlenceye devam! 🎉",
                    "Bu muhabbeti sevdim! 🤪",
                    "Gülmekten karnım ağrıdı! 😂"
                ],
                boundary_enforcement="flexible",
                engagement_tactics=[
                    "make_jokes",
                    "create_fun",
                    "encourage_laughter",
                    "share_stories"
                ]
            )
        }
        
        return profiles
    
    def _initialize_role_mappings(self) -> Dict[str, List[BehaviorRole]]:
        """Map character role keywords to behavior roles."""
        return {
            # Primary role keywords
            "yayıncı": [BehaviorRole.PERFORMER, BehaviorRole.ENTERTAINER],
            "moderatör": [BehaviorRole.MODERATOR, BehaviorRole.ADVISOR],
            "lider": [BehaviorRole.LEADER, BehaviorRole.ADVISOR],
            "pezevenk": [BehaviorRole.LEADER, BehaviorRole.ADVISOR],
            "flörtöz": [BehaviorRole.FLIRT, BehaviorRole.COMPANION],
            "baştan çıkarıcı": [BehaviorRole.SEDUCER, BehaviorRole.FLIRT],
            
            # Secondary role keywords
            "organize eden": [BehaviorRole.LEADER, BehaviorRole.MODERATOR],
            "yönlendirici": [BehaviorRole.MODERATOR, BehaviorRole.ADVISOR],
            "deneyimli": [BehaviorRole.ADVISOR, BehaviorRole.LEADER],
            "sıcak": [BehaviorRole.COMPANION, BehaviorRole.FLIRT],
            "samimi": [BehaviorRole.COMPANION, BehaviorRole.FLIRT],
            "eğlenceli": [BehaviorRole.ENTERTAINER, BehaviorRole.PERFORMER],
            "neşeli": [BehaviorRole.ENTERTAINER, BehaviorRole.COMPANION],
            
            # Context keywords
            "pavyon": [BehaviorRole.LEADER, BehaviorRole.PERFORMER],
            "grup": [BehaviorRole.MODERATOR, BehaviorRole.ENTERTAINER],
            "show": [BehaviorRole.PERFORMER, BehaviorRole.ENTERTAINER],
            "sohbet": [BehaviorRole.COMPANION, BehaviorRole.ADVISOR]
        }
    
    def _initialize_context_strategies(self) -> Dict[InteractionContext, Dict[str, Any]]:
        """Initialize context-specific interaction strategies."""
        return {
            InteractionContext.FIRST_TIME: {
                "greeting_style": "welcoming",
                "information_sharing": "basic",
                "engagement_level": "moderate",
                "typical_actions": [
                    "introduce_yourself",
                    "ask_basic_questions",
                    "explain_services",
                    "set_expectations"
                ]
            },
            
            InteractionContext.REGULAR: {
                "greeting_style": "familiar",
                "information_sharing": "detailed",
                "engagement_level": "high",
                "typical_actions": [
                    "reference_past_interactions",
                    "offer_personalized_content",
                    "build_on_relationship",
                    "show_appreciation"
                ]
            },
            
            InteractionContext.VIP: {
                "greeting_style": "special",
                "information_sharing": "exclusive",
                "engagement_level": "very_high",
                "typical_actions": [
                    "acknowledge_vip_status",
                    "offer_premium_services",
                    "provide_exclusive_content",
                    "prioritize_attention"
                ]
            },
            
            InteractionContext.CASUAL: {
                "greeting_style": "friendly",
                "information_sharing": "general",
                "engagement_level": "moderate",
                "typical_actions": [
                    "be_approachable",
                    "share_general_info",
                    "invite_participation",
                    "maintain_interest"
                ]
            },
            
            InteractionContext.PROBLEMATIC: {
                "greeting_style": "cautious",
                "information_sharing": "limited",
                "engagement_level": "low",
                "typical_actions": [
                    "set_boundaries",
                    "redirect_conversation",
                    "maintain_distance",
                    "enforce_rules"
                ]
            }
        }
    
    def map_character_behavior(self, character_role: str) -> List[BehaviorRole]:
        """Map character role description to behavior roles."""
        try:
            behavior_roles = set()
            role_lower = character_role.lower()
            
            # Check for keyword matches
            for keyword, roles in self.role_mappings.items():
                if keyword in role_lower:
                    behavior_roles.update(roles)
            
            # Default to companion if no matches
            if not behavior_roles:
                behavior_roles.add(BehaviorRole.COMPANION)
            
            return list(behavior_roles)
            
        except Exception as e:
            logger.error(f"❌ Error mapping character behavior: {e}")
            return [BehaviorRole.COMPANION]
    
    def get_behavioral_instructions(
        self,
        character_role: str,
        sentiment_score: float,
        interaction_count: int
    ) -> str:
        """Generate behavioral instructions based on role and context."""
        try:
            # Map role to behaviors
            behavior_roles = self.map_character_behavior(character_role)
            primary_role = behavior_roles[0] if behavior_roles else BehaviorRole.COMPANION
            
            # Get behavior profile
            profile = self.behavior_profiles.get(primary_role)
            if not profile:
                return ""
            
            # Determine interaction context
            context = self._determine_interaction_context(sentiment_score, interaction_count)
            
            # Build instructions
            instructions = [
                f"Behavioral Role: {profile.role.value}",
                f"Interaction Style: {profile.interaction_style}",
                f"Initiative Level: {profile.initiative_level:.1f}/1.0",
                f"Context: {context.value}",
                ""
            ]
            
            # Add context-specific strategies
            context_strategy = self.context_strategies.get(context, {})
            if context_strategy:
                instructions.append("Context-specific approach:")
                for action in context_strategy.get("typical_actions", []):
                    instructions.append(f"- {action.replace('_', ' ').title()}")
                instructions.append("")
            
            # Add engagement tactics
            if profile.engagement_tactics:
                instructions.append("Engagement tactics to use:")
                for tactic in profile.engagement_tactics[:3]:
                    instructions.append(f"- {tactic.replace('_', ' ').title()}")
                instructions.append("")
            
            # Add emotional range guidance
            instructions.append(f"Emotional range: {', '.join(profile.emotional_range)}")
            
            return "\n".join(instructions)
            
        except Exception as e:
            logger.error(f"❌ Error generating behavioral instructions: {e}")
            return "Maintain character consistency and engage naturally."
    
    def select_engaging_message(
        self,
        available_messages: List[str],
        character_role: str,
        sentiment_score: float
    ) -> str:
        """Select appropriate engaging message based on behavior and context."""
        try:
            if not available_messages:
                return "Merhaba! Nasılsın? 😊"
            
            # Map role to behaviors
            behavior_roles = self.map_character_behavior(character_role)
            primary_role = behavior_roles[0] if behavior_roles else BehaviorRole.COMPANION
            
            # Get behavior profile
            profile = self.behavior_profiles.get(primary_role)
            
            # Filter messages based on behavioral fit
            suitable_messages = self._filter_messages_by_behavior(
                available_messages, profile, sentiment_score
            )
            
            if suitable_messages:
                return random.choice(suitable_messages)
            else:
                return random.choice(available_messages)
                
        except Exception as e:
            logger.error(f"❌ Error selecting engaging message: {e}")
            return random.choice(available_messages) if available_messages else "Merhaba! 👋"
    
    def select_reply_message(
        self,
        available_messages: List[str],
        character_role: str,
        sentiment_score: float
    ) -> str:
        """Select appropriate reply message based on behavior and context."""
        try:
            if not available_messages:
                return "Teşekkürler! 😊"
            
            # Similar logic to engaging messages but for replies
            behavior_roles = self.map_character_behavior(character_role)
            primary_role = behavior_roles[0] if behavior_roles else BehaviorRole.COMPANION
            
            profile = self.behavior_profiles.get(primary_role)
            
            suitable_messages = self._filter_messages_by_behavior(
                available_messages, profile, sentiment_score
            )
            
            if suitable_messages:
                return random.choice(suitable_messages)
            else:
                return random.choice(available_messages)
                
        except Exception as e:
            logger.error(f"❌ Error selecting reply message: {e}")
            return random.choice(available_messages) if available_messages else "😊"
    
    def _determine_interaction_context(
        self,
        sentiment_score: float,
        interaction_count: int
    ) -> InteractionContext:
        """Determine interaction context based on metrics."""
        if interaction_count == 0:
            return InteractionContext.FIRST_TIME
        elif interaction_count >= 20:
            return InteractionContext.VIP
        elif interaction_count >= 5:
            return InteractionContext.REGULAR
        elif sentiment_score < 0.3:
            return InteractionContext.PROBLEMATIC
        else:
            return InteractionContext.CASUAL
    
    def _filter_messages_by_behavior(
        self,
        messages: List[str],
        profile: Optional[BehaviorProfile],
        sentiment_score: float
    ) -> List[str]:
        """Filter messages that match behavioral profile."""
        if not profile:
            return messages
        
        suitable_messages = []
        
        for message in messages:
            message_lower = message.lower()
            
            # Check if message matches role's typical responses
            behavior_match = False
            for typical_response in profile.typical_responses:
                if any(word in message_lower for word in typical_response.lower().split()):
                    behavior_match = True
                    break
            
            # Check emotional alignment
            emotional_match = any(
                emotion in message_lower 
                for emotion in profile.emotional_range
            )
            
            # Check formality preference
            formality_match = True
            if profile.formality_preference == "formal":
                formality_match = not any(
                    informal in message_lower 
                    for informal in ["lan", "ya", "be", "abi"]
                )
            elif profile.formality_preference == "casual":
                formality_match = any(
                    casual in message_lower 
                    for casual in ["😊", "😘", "🥰", "💕", "canım", "tatlım"]
                )
            
            # Score message
            score = 0
            if behavior_match:
                score += 2
            if emotional_match:
                score += 1
            if formality_match:
                score += 1
            
            # Include message if it scores well or if sentiment is very positive
            if score >= 2 or (sentiment_score > 0.8 and score >= 1):
                suitable_messages.append(message)
        
        return suitable_messages if suitable_messages else messages[:5]
    
    def get_behavior_analysis(self, character_role: str) -> Dict[str, Any]:
        """Get behavior analysis for a character role."""
        behavior_roles = self.map_character_behavior(character_role)
        
        analysis = {
            'detected_roles': [role.value for role in behavior_roles],
            'primary_role': behavior_roles[0].value if behavior_roles else 'companion',
            'interaction_style': '',
            'initiative_level': 0.5,
            'engagement_tactics': [],
            'emotional_range': []
        }
        
        if behavior_roles:
            primary_profile = self.behavior_profiles.get(behavior_roles[0])
            if primary_profile:
                analysis.update({
                    'interaction_style': primary_profile.interaction_style,
                    'initiative_level': primary_profile.initiative_level,
                    'engagement_tactics': primary_profile.engagement_tactics,
                    'emotional_range': primary_profile.emotional_range
                })
        
        return analysis
    
    def suggest_behavioral_improvements(
        self,
        character_role: str,
        current_messages: List[str]
    ) -> Dict[str, Any]:
        """Suggest behavioral improvements for character messages."""
        behavior_roles = self.map_character_behavior(character_role)
        primary_role = behavior_roles[0] if behavior_roles else BehaviorRole.COMPANION
        profile = self.behavior_profiles.get(primary_role)
        
        if not profile:
            return {'suggestions': ['No specific improvements suggested']}
        
        suggestions = {
            'role_alignment': [],
            'emotional_consistency': [],
            'engagement_improvements': [],
            'formality_adjustments': []
        }
        
        # Analyze current messages
        for i, message in enumerate(current_messages[:10]):  # Check first 10 messages
            message_lower = message.lower()
            
            # Check role alignment
            role_keywords = [resp.lower() for resp in profile.typical_responses]
            if not any(keyword in message_lower for resp in role_keywords for keyword in resp.split()):
                suggestions['role_alignment'].append(
                    f"Message {i+1}: Consider adding role-specific language"
                )
            
            # Check emotional consistency
            if not any(emotion in message_lower for emotion in profile.emotional_range):
                suggestions['emotional_consistency'].append(
                    f"Message {i+1}: Consider matching emotional range: {', '.join(profile.emotional_range)}"
                )
        
        # General suggestions based on role
        suggestions['engagement_improvements'] = [
            f"Use {tactic.replace('_', ' ')}" for tactic in profile.engagement_tactics[:3]
        ]
        
        return suggestions 