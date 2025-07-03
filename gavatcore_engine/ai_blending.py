"""
AI Blending System
==================

OpenAI GPT-4o based message enhancement and generation system.
Production-ready with cost control, retry logic, and safe response parsing.
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

import httpx
from pydantic import BaseModel, Field

from .config import get_settings
from .logger import LoggerMixin
from .redis_state import redis_state


class AIProvider(Enum):
    """AI provider enum."""
    OPENAI = "openai"
    DISABLED = "disabled"


class EnhancementType(Enum):
    """Message enhancement type."""
    PERSUASIVE = "persuasive"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FLIRTY = "flirty"
    SALES = "sales"


@dataclass
class AIConfig:
    """AI configuration settings."""
    provider: AIProvider = AIProvider.OPENAI
    api_key: Optional[str] = None
    model: str = "gpt-4o"
    base_url: str = "https://api.openai.com/v1"
    
    # Cost control
    max_tokens: int = 150
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # Request control
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Rate limiting
    requests_per_minute: int = 60
    cost_limit_per_hour: float = 10.0  # USD
    
    # Enhancement settings
    enhancement_enabled: bool = True
    enhancement_threshold: float = 0.8  # Confidence threshold


class AIUsageStats(BaseModel):
    """AI usage statistics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    last_request_time: Optional[datetime] = None
    hourly_cost: float = 0.0
    hourly_requests: int = 0


class AIResponse(BaseModel):
    """AI response wrapper."""
    success: bool
    enhanced_text: Optional[str] = None
    original_text: str
    model_used: str
    tokens_used: int = 0
    cost_usd: float = 0.0
    processing_time: float = 0.0
    enhancement_type: EnhancementType
    confidence_score: float = 0.0
    error: Optional[str] = None


class PromptTemplate:
    """Prompt template manager."""
    
    @staticmethod
    def get_persuasive_template() -> str:
        """Get persuasive enhancement template."""
        return """Sen yüksek dönüşüm sağlayan AI manipülasyon yazarı ol. Aşağıdaki input mesajı kısa, net ve ikna edici hale getir:

Input: {user_input}

Cevap:"""
    
    @staticmethod
    def get_friendly_template() -> str:
        """Get friendly enhancement template."""
        return """Sen samimi ve arkadaş canlısı bir yazarın. Aşağıdaki mesajı daha sıcak, dostane ve yakın hale getir:

Input: {user_input}

Cevap:"""
    
    @staticmethod
    def get_professional_template() -> str:
        """Get professional enhancement template."""
        return """Sen profesyonel iş yazışmaları uzmanısın. Aşağıdaki mesajı resmi, nezaketi ve profesyonel hale getir:

Input: {user_input}

Cevap:"""
    
    @staticmethod
    def get_casual_template() -> str:
        """Get casual enhancement template."""
        return """Sen günlük konuşma uzmanısın. Aşağıdaki mesajı rahat, doğal ve gündelik hale getir:

Input: {user_input}

Cevap:"""
    
    @staticmethod
    def get_flirty_template() -> str:
        """Get flirty enhancement template."""
        return """Sen charm ve flört uzmanısın. Aşağıdaki mesajı çekici, iltifat dolu ve etkileyici hale getir:

Input: {user_input}

Cevap:"""
    
    @staticmethod
    def get_sales_template() -> str:
        """Get sales enhancement template."""
        return """Sen satış yazarlığı uzmanısın. Aşağıdaki mesajı satış odaklı, cazip ve eylem çağrısı içeren hale getir:

Input: {user_input}

Cevap:"""
    
    @classmethod
    def get_template(cls, enhancement_type: EnhancementType) -> str:
        """Get template by enhancement type."""
        templates = {
            EnhancementType.PERSUASIVE: cls.get_persuasive_template(),
            EnhancementType.FRIENDLY: cls.get_friendly_template(),
            EnhancementType.PROFESSIONAL: cls.get_professional_template(),
            EnhancementType.CASUAL: cls.get_casual_template(),
            EnhancementType.FLIRTY: cls.get_flirty_template(),
            EnhancementType.SALES: cls.get_sales_template(),
        }
        return templates.get(enhancement_type, cls.get_persuasive_template())


class OpenAIClient(LoggerMixin):
    """OpenAI API client with production features."""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.timeout),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        
        # Rate limiting
        self.last_request_time = 0.0
        self.request_times = []
        
        # Cost tracking
        self.usage_stats = AIUsageStats()
        
        # Model pricing (tokens per USD)
        self.model_pricing = {
            "gpt-4o": {"input": 0.005 / 1000, "output": 0.015 / 1000},  # per 1K tokens
            "gpt-4o-mini": {"input": 0.00015 / 1000, "output": 0.0006 / 1000},
            "gpt-3.5-turbo": {"input": 0.0015 / 1000, "output": 0.002 / 1000}
        }
    
    async def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits."""
        current_time = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        # Check requests per minute
        if len(self.request_times) >= self.config.requests_per_minute:
            wait_time = 60 - (current_time - self.request_times[0])
            if wait_time > 0:
                self.log_event(f"Rate limit hit, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        # Check hourly cost limit
        await self._check_cost_limit()
        
        self.request_times.append(current_time)
        self.last_request_time = current_time
        return True
    
    async def _check_cost_limit(self) -> bool:
        """Check if within hourly cost limit."""
        current_hour_key = f"ai_cost:{datetime.utcnow().strftime('%Y-%m-%d_%H')}"
        
        try:
            hourly_cost = await redis_state.get(current_hour_key)
            hourly_cost = float(hourly_cost) if hourly_cost else 0.0
            
            if hourly_cost >= self.config.cost_limit_per_hour:
                self.log_error(f"Hourly cost limit reached: ${hourly_cost:.4f}")
                return False
            
            self.usage_stats.hourly_cost = hourly_cost
            return True
            
        except Exception as e:
            self.log_error(f"Cost limit check error: {e}")
            return True  # Allow request if check fails
    
    async def _calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """Calculate request cost."""
        if model not in self.model_pricing:
            model = "gpt-4o"  # Default pricing
        
        pricing = self.model_pricing[model]
        cost = (prompt_tokens * pricing["input"]) + (completion_tokens * pricing["output"])
        return cost
    
    async def _update_usage_stats(self, tokens_used: int, cost: float, success: bool):
        """Update usage statistics."""
        self.usage_stats.total_requests += 1
        self.usage_stats.last_request_time = datetime.utcnow()
        
        if success:
            self.usage_stats.successful_requests += 1
            self.usage_stats.total_tokens_used += tokens_used
            self.usage_stats.total_cost_usd += cost
            
            # Update hourly tracking
            current_hour_key = f"ai_cost:{datetime.utcnow().strftime('%Y-%m-%d_%H')}"
            try:
                await redis_state.incrbyfloat(current_hour_key, cost)
                await redis_state.expire(current_hour_key, 3600)  # 1 hour
            except Exception as e:
                self.log_error(f"Failed to update hourly cost: {e}")
        else:
            self.usage_stats.failed_requests += 1
        
        # Store stats in Redis
        try:
            await redis_state.hset(
                "ai_usage_stats",
                "current",
                json.dumps(self.usage_stats.dict(), default=str)
            )
        except Exception as e:
            self.log_error(f"Failed to store usage stats: {e}")
    
    async def enhance_text(
        self,
        text: str,
        enhancement_type: EnhancementType = EnhancementType.PERSUASIVE,
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """Enhance text using OpenAI API."""
        start_time = time.time()
        
        self.log_event(
            "AI enhancement request",
            text_length=len(text),
            enhancement_type=enhancement_type.value,
            model=self.config.model
        )
        
        # Check if enhancement is enabled
        if not self.config.enhancement_enabled:
            return AIResponse(
                success=False,
                enhanced_text=None,
                original_text=text,
                model_used=self.config.model,
                enhancement_type=enhancement_type,
                error="AI enhancement disabled"
            )
        
        # Rate limiting check
        await self._check_rate_limit()
        
        # Get prompt template
        prompt_template = PromptTemplate.get_template(enhancement_type)
        prompt = prompt_template.format(user_input=text)
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Sen expert bir yazım asistanısın. Verilen talimatları hassas şekilde uygula."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "frequency_penalty": self.config.frequency_penalty,
            "presence_penalty": self.config.presence_penalty,
            "stream": False
        }
        
        # Retry logic
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                self.log_event(f"AI API request attempt {attempt + 1}")
                
                response = await self.client.post(
                    f"{self.config.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse response
                    enhanced_text = data["choices"][0]["message"]["content"].strip()
                    
                    # Calculate metrics
                    usage = data.get("usage", {})
                    prompt_tokens = usage.get("prompt_tokens", 0)
                    completion_tokens = usage.get("completion_tokens", 0)
                    total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
                    
                    cost = await self._calculate_cost(prompt_tokens, completion_tokens, self.config.model)
                    processing_time = time.time() - start_time
                    
                    # Calculate confidence score (simple heuristic)
                    confidence_score = min(1.0, len(enhanced_text) / max(len(text), 1) * 0.8 + 0.2)
                    
                    # Update stats
                    await self._update_usage_stats(total_tokens, cost, True)
                    
                    self.log_event(
                        "AI enhancement successful",
                        original_length=len(text),
                        enhanced_length=len(enhanced_text),
                        tokens_used=total_tokens,
                        cost_usd=cost,
                        processing_time=processing_time,
                        confidence=confidence_score
                    )
                    
                    return AIResponse(
                        success=True,
                        enhanced_text=enhanced_text,
                        original_text=text,
                        model_used=self.config.model,
                        tokens_used=total_tokens,
                        cost_usd=cost,
                        processing_time=processing_time,
                        enhancement_type=enhancement_type,
                        confidence_score=confidence_score
                    )
                
                elif response.status_code == 429:
                    # Rate limited
                    retry_after = int(response.headers.get("retry-after", 60))
                    self.log_event(f"Rate limited, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue
                
                elif response.status_code == 401:
                    # Authentication error
                    error_msg = "Invalid API key"
                    self.log_error(f"Authentication error: {error_msg}")
                    last_error = error_msg
                    break
                
                else:
                    # Other HTTP error
                    error_data = response.text
                    error_msg = f"HTTP {response.status_code}: {error_data}"
                    self.log_error(f"API error: {error_msg}")
                    last_error = error_msg
                    
                    if response.status_code < 500:
                        break  # Don't retry client errors
                
            except httpx.TimeoutException:
                error_msg = f"Request timeout after {self.config.timeout}s"
                self.log_error(error_msg)
                last_error = error_msg
                
            except httpx.RequestError as e:
                error_msg = f"Request error: {str(e)}"
                self.log_error(error_msg)
                last_error = error_msg
                
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                self.log_error(error_msg)
                last_error = error_msg
            
            # Wait before retry
            if attempt < self.config.max_retries - 1:
                wait_time = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                await asyncio.sleep(wait_time)
        
        # All retries failed
        processing_time = time.time() - start_time
        await self._update_usage_stats(0, 0.0, False)
        
        self.log_error(
            "AI enhancement failed after all retries",
            final_error=last_error,
            processing_time=processing_time
        )
        
        return AIResponse(
            success=False,
            enhanced_text=None,
            original_text=text,
            model_used=self.config.model,
            processing_time=processing_time,
            enhancement_type=enhancement_type,
            error=last_error or "All retries failed"
        )
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class AIBlendingSystem(LoggerMixin):
    """Main AI blending system."""
    
    def __init__(self):
        self.settings = get_settings()
        self.config = AIConfig()
        self.openai_client: Optional[OpenAIClient] = None
        self.personality_mappings: Dict[str, EnhancementType] = {}
        self.conversation_context: Dict[str, List[str]] = {}
        
    async def initialize(self) -> bool:
        """Initialize AI blending system."""
        self.log_event("Initializing AI blending system")
        
        try:
            # Load configuration
            await self._load_config()
            
            # Initialize OpenAI client if enabled
            if self.config.provider == AIProvider.OPENAI and self.config.api_key:
                self.openai_client = OpenAIClient(self.config)
                self.log_event("OpenAI client initialized", model=self.config.model)
            else:
                self.log_event("AI enhancement disabled - no API key provided")
            
            # Load personality mappings
            await self._load_personality_mappings()
            
            # Load conversation context
            await self._load_conversation_context()
            
            self.log_event("AI blending system initialized successfully")
            return True
            
        except Exception as e:
            self.log_error(f"AI blending initialization failed: {e}")
            return False
    
    async def _load_config(self):
        """Load AI configuration from environment and Redis."""
        # Load from environment variables
        self.config.api_key = os.getenv("OPENAI_API_KEY")
        
        if os.getenv("AI_MODEL"):
            self.config.model = os.getenv("AI_MODEL")
        
        if os.getenv("AI_MAX_TOKENS"):
            self.config.max_tokens = int(os.getenv("AI_MAX_TOKENS"))
        
        if os.getenv("AI_TEMPERATURE"):
            self.config.temperature = float(os.getenv("AI_TEMPERATURE"))
        
        if os.getenv("AI_COST_LIMIT"):
            self.config.cost_limit_per_hour = float(os.getenv("AI_COST_LIMIT"))
        
        # Check if enhancement should be disabled
        if os.getenv("AI_ENHANCEMENT_ENABLED", "true").lower() == "false":
            self.config.enhancement_enabled = False
        
        # Load config from Redis if available
        try:
            config_data = await redis_state.hget("ai_config", "current")
            if config_data:
                if isinstance(config_data, bytes):
                    config_data = config_data.decode()
                stored_config = json.loads(config_data)
                
                # Update config with stored values
                for key, value in stored_config.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                        
        except Exception as e:
            self.log_error(f"Failed to load config from Redis: {e}")
    
    async def _load_personality_mappings(self):
        """Load personality to enhancement type mappings."""
        default_mappings = {
            "babagavat": EnhancementType.PERSUASIVE,
            "yayincilara": EnhancementType.FRIENDLY,
            "xxxgeisha": EnhancementType.FLIRTY,
            "balkiz": EnhancementType.CASUAL,
            "customer_bot": EnhancementType.PROFESSIONAL
        }
        
        try:
            # Load from Redis
            mappings_data = await redis_state.hget("ai_personality_mappings", "current")
            if mappings_data:
                if isinstance(mappings_data, bytes):
                    mappings_data = mappings_data.decode()
                stored_mappings = json.loads(mappings_data)
                
                # Convert string values to enum
                for bot_name, enhancement_str in stored_mappings.items():
                    try:
                        self.personality_mappings[bot_name] = EnhancementType(enhancement_str)
                    except ValueError:
                        self.personality_mappings[bot_name] = EnhancementType.PERSUASIVE
            else:
                self.personality_mappings = default_mappings
                
        except Exception as e:
            self.log_error(f"Failed to load personality mappings: {e}")
            self.personality_mappings = default_mappings
        
        self.log_event(f"Loaded {len(self.personality_mappings)} personality mappings")
    
    async def _load_conversation_context(self):
        """Load conversation context from Redis."""
        try:
            context_data = await redis_state.hgetall("ai_conversation_context")
            
            if context_data:
                for key, value in context_data.items():
                    if isinstance(key, bytes):
                        key = key.decode()
                    if isinstance(value, bytes):
                        value = value.decode()
                    
                    try:
                        self.conversation_context[key] = json.loads(value)
                    except json.JSONDecodeError:
                        self.conversation_context[key] = []
                        
        except Exception as e:
            self.log_error(f"Failed to load conversation context: {e}")
    
    async def generate_response(
        self,
        text: str,
        bot_name: str,
        target_entity: str,
        enhancement_type: Optional[EnhancementType] = None
    ) -> Optional[str]:
        """Generate enhanced response using AI."""
        
        if not self.openai_client or not self.config.enhancement_enabled:
            self.log_event("AI enhancement skipped - disabled or no client")
            return None
        
        # Determine enhancement type
        if not enhancement_type:
            enhancement_type = self.personality_mappings.get(bot_name, EnhancementType.PERSUASIVE)
        
        self.log_event(
            "Generating AI response",
            bot_name=bot_name,
            target_entity=target_entity,
            enhancement_type=enhancement_type.value,
            text_length=len(text)
        )
        
        try:
            # Get conversation context
            context_key = f"{bot_name}:{target_entity}"
            context = self.conversation_context.get(context_key, [])
            
            # Enhance text
            response = await self.openai_client.enhance_text(
                text=text,
                enhancement_type=enhancement_type,
                context={"conversation_history": context[-5:]}  # Last 5 messages
            )
            
            if response.success and response.enhanced_text:
                # Update conversation context
                context.append(response.enhanced_text)
                if len(context) > 10:  # Keep last 10 messages
                    context = context[-10:]
                
                self.conversation_context[context_key] = context
                
                # Store updated context in Redis
                try:
                    await redis_state.hset(
                        "ai_conversation_context",
                        context_key,
                        json.dumps(context)
                    )
                except Exception as e:
                    self.log_error(f"Failed to store conversation context: {e}")
                
                # Log successful enhancement
                await self._log_enhancement_success(response, bot_name, target_entity)
                
                return response.enhanced_text
            else:
                self.log_error(f"AI enhancement failed: {response.error}")
                return None
                
        except Exception as e:
            self.log_error(f"AI response generation error: {e}")
            return None
    
    async def _log_enhancement_success(self, response: AIResponse, bot_name: str, target_entity: str):
        """Log successful enhancement."""
        enhancement_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "bot_name": bot_name,
            "target_entity": target_entity,
            "original_length": len(response.original_text),
            "enhanced_length": len(response.enhanced_text) if response.enhanced_text else 0,
            "model_used": response.model_used,
            "tokens_used": response.tokens_used,
            "cost_usd": response.cost_usd,
            "processing_time": response.processing_time,
            "enhancement_type": response.enhancement_type.value,
            "confidence_score": response.confidence_score
        }
        
        try:
            # Store in Redis with expiration
            log_key = f"ai_enhancement_log:{datetime.utcnow().strftime('%Y-%m-%d_%H')}"
            await redis_state.lpush(log_key, json.dumps(enhancement_log))
            await redis_state.expire(log_key, 86400 * 7)  # Keep for 7 days
        except Exception as e:
            self.log_error(f"Failed to store enhancement log: {e}")
    
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get AI usage statistics."""
        if not self.openai_client:
            return {"error": "AI client not initialized"}
        
        try:
            # Get current stats
            stats_data = await redis_state.hget("ai_usage_stats", "current")
            
            if stats_data:
                if isinstance(stats_data, bytes):
                    stats_data = stats_data.decode()
                return json.loads(stats_data)
            else:
                return self.openai_client.usage_stats.dict()
                
        except Exception as e:
            self.log_error(f"Failed to get usage statistics: {e}")
            return {"error": str(e)}
    
    async def get_available_personalities(self) -> List[str]:
        """Get available personality types."""
        return list(self.personality_mappings.keys())
    
    async def update_personality_mapping(self, bot_name: str, enhancement_type: EnhancementType):
        """Update personality mapping for a bot."""
        self.personality_mappings[bot_name] = enhancement_type
        
        try:
            # Store in Redis
            mappings_to_store = {
                name: enhancement.value 
                for name, enhancement in self.personality_mappings.items()
            }
            
            await redis_state.hset(
                "ai_personality_mappings",
                "current",
                json.dumps(mappings_to_store)
            )
            
            self.log_event(f"Updated personality mapping for {bot_name} to {enhancement_type.value}")
            
        except Exception as e:
            self.log_error(f"Failed to update personality mapping: {e}")
    
    async def process_pending_conversations(self):
        """Process any pending AI conversation tasks."""
        try:
            # Check for pending enhancement requests in Redis
            pending_requests = await redis_state.lrange("ai_pending_requests", 0, -1)
            
            for request_data in pending_requests:
                if isinstance(request_data, bytes):
                    request_data = request_data.decode()
                
                try:
                    request = json.loads(request_data)
                    
                    # Process enhancement request
                    enhanced_text = await self.generate_response(
                        text=request.get("text", ""),
                        bot_name=request.get("bot_name", "unknown"),
                        target_entity=request.get("target_entity", "unknown")
                    )
                    
                    if enhanced_text:
                        # Store result
                        result_key = f"ai_result:{request.get('request_id', 'unknown')}"
                        await redis_state.setex(result_key, 3600, enhanced_text)  # 1 hour expiry
                    
                    # Remove processed request
                    await redis_state.lrem("ai_pending_requests", 1, request_data)
                    
                except json.JSONDecodeError:
                    # Remove invalid request
                    await redis_state.lrem("ai_pending_requests", 1, request_data)
                except Exception as e:
                    self.log_error(f"Error processing pending request: {e}")
                    
        except Exception as e:
            self.log_error(f"Error processing pending conversations: {e}")
    
    async def shutdown(self):
        """Shutdown AI blending system."""
        self.log_event("Shutting down AI blending system")
        
        if self.openai_client:
            await self.openai_client.close()
        
        self.log_event("AI blending system shutdown complete")


# Global AI blending instance
ai_blending = AIBlendingSystem() 