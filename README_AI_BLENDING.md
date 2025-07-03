# 🧠 AI Blending System

OpenAI GPT-4o tabanlı intelligent mesaj geliştirme sistemi. Production-ready, cost-controlled ve güvenli.

## 🌟 Özellikler

### 🔧 **Core Functionality**
- **OpenAI GPT-4o Integration**: Latest model desteği
- **Multiple Enhancement Types**: 6 farklı enhancement stili
- **Cost Control**: Saatlik maliyet limitleri ve token kontrolü
- **Rate Limiting**: Request/minute limitleri
- **Retry Logic**: Exponential backoff ile retry mekanizması
- **Safe Response Parsing**: Güvenli response işleme

### 🎭 **Enhancement Types**
- **PERSUASIVE**: Yüksek dönüşüm sağlayan manipülasyon yazısı
- **FRIENDLY**: Samimi ve arkadaş canlısı ton
- **PROFESSIONAL**: Resmi ve profesyonel dil
- **CASUAL**: Rahat ve gündelik konuşma
- **FLIRTY**: Çekici ve iltifat dolu stil
- **SALES**: Satış odaklı ve eylem çağrısı içeren

### 💰 **Cost Management**
- **Token Limiting**: Max token kontrolü
- **Hourly Cost Limits**: Saatlik harcama limitleri
- **Model Pricing**: Gerçek zamanlı maliyet hesaplama
- **Usage Statistics**: Detaylı kullanım istatistikleri

### 🛡️ **Security & Reliability**
- **API Key Security**: Environment variable management
- **Error Handling**: Comprehensive hata yönetimi
- **Timeout Control**: Request timeout yönetimi
- **Fallback Mechanisms**: API failure durumunda fallback

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```bash
# Dependencies kur
pip install openai httpx[http2] redis

# Veya requirements.txt ile
pip install -r gavatcore_engine/requirements.txt
```

### 2. API Key Setup

```bash
# OpenAI API key'i environment variable olarak ayarla
export OPENAI_API_KEY=your_openai_api_key_here

# Opsiyonel konfigürasyon
export AI_MODEL=gpt-4o
export AI_MAX_TOKENS=150
export AI_TEMPERATURE=0.7
export AI_COST_LIMIT=10.0
```

### 3. Basit Kullanım

```python
from gavatcore_engine.ai_blending import AIBlendingSystem, EnhancementType

# AI sistemi başlat
ai_system = AIBlendingSystem()
await ai_system.initialize()

# Mesaj geliştir
enhanced_text = await ai_system.generate_response(
    text="Merhaba, nasılsın?",
    bot_name="yayincilara",
    target_entity="@vip_group"
)

print(f"Enhanced: {enhanced_text}")
```

## 📖 Detaylı Kullanım

### Configuration

```python
from gavatcore_engine.ai_blending import AIConfig, AIProvider

# Custom configuration
config = AIConfig(
    provider=AIProvider.OPENAI,
    api_key="your_api_key",
    model="gpt-4o",
    
    # Cost control
    max_tokens=150,
    temperature=0.7,
    cost_limit_per_hour=10.0,
    
    # Rate limiting
    requests_per_minute=60,
    timeout=30,
    max_retries=3
)
```

### Enhancement Types

```python
# Farklı enhancement türleri
enhancement_types = [
    EnhancementType.PERSUASIVE,    # Manipülasyon yazısı
    EnhancementType.FRIENDLY,      # Samimi ton
    EnhancementType.PROFESSIONAL,  # Profesyonel dil
    EnhancementType.CASUAL,        # Gündelik konuşma
    EnhancementType.FLIRTY,        # Çekici stil
    EnhancementType.SALES          # Satış odaklı
]

# Belirli enhancement type ile kullanım
enhanced = await ai_system.generate_response(
    text="Bu ürünü denemelisin",
    bot_name="sales_bot",
    target_entity="@customers",
    enhancement_type=EnhancementType.SALES
)
```

### Prompt Templates

```python
from gavatcore_engine.ai_blending import PromptTemplate

# Persuasive template (main template)
template = PromptTemplate.get_persuasive_template()
print(template)
# Output:
# """
# Sen yüksek dönüşüm sağlayan AI manipülasyon yazarı ol. 
# Aşağıdaki input mesajı kısa, net ve ikna edici hale getir:
# 
# Input: {user_input}
# 
# Cevap:
# """

# Template formatting
formatted = template.format(user_input="Test mesajı")
```

### Bot Personality Mappings

```python
# Bot personality'lerini yönet
personalities = await ai_system.get_available_personalities()
print(f"Available bots: {personalities}")

# Yeni personality mapping ekle
await ai_system.update_personality_mapping(
    "new_bot", 
    EnhancementType.FLIRTY
)

# Mevcut mapping'leri göster
for bot_name in personalities:
    enhancement = ai_system.personality_mappings.get(bot_name)
    print(f"{bot_name}: {enhancement.value}")
```

### Cost Control ve Monitoring

```python
# Usage statistics
stats = await ai_system.get_usage_statistics()
print(f"Total requests: {stats['total_requests']}")
print(f"Total cost: ${stats['total_cost_usd']:.6f}")
print(f"Success rate: {stats['successful_requests']/stats['total_requests']*100:.1f}%")

# Maliyet hesaplama
from gavatcore_engine.ai_blending import OpenAIClient

client = OpenAIClient(config)
cost = await client._calculate_cost(1000, 500, "gpt-4o")
print(f"Cost for 1000+500 tokens: ${cost:.6f}")
```

## 🎯 Gelişmiş Özellikler

### Conversation Context Management

```python
# Conversation context otomatik yönetiliyor
# Her bot:entity için ayrı context saklanıyor

context_key = "yayincilara:@vip_group"
context = ai_system.conversation_context.get(context_key, [])
print(f"Conversation history: {len(context)} messages")

# Son 5 mesaj context olarak kullanılıyor
# Maksimum 10 mesaj saklanıyor
```

### Error Handling

```python
from gavatcore_engine.ai_blending import AIResponse

response = await client.enhance_text(
    "Test message",
    EnhancementType.PERSUASIVE
)

if response.success:
    print(f"Enhanced: {response.enhanced_text}")
    print(f"Cost: ${response.cost_usd:.6f}")
    print(f"Tokens: {response.tokens_used}")
    print(f"Confidence: {response.confidence_score:.2f}")
else:
    print(f"Error: {response.error}")
    
    # Retry after time
    if response.retry_after:
        await asyncio.sleep(response.retry_after)
```

### Redis Integration

```python
# AI sistemi Redis ile entegre
# Otomatik olarak şunları saklıyor:

# 1. Usage statistics
await redis_state.hget("ai_usage_stats", "current")

# 2. Hourly cost tracking
current_hour = datetime.utcnow().strftime("%Y-%m-%d_%H")
cost = await redis_state.get(f"ai_cost:{current_hour}")

# 3. Conversation context
context = await redis_state.hget("ai_conversation_context", "bot:entity")

# 4. Personality mappings
mappings = await redis_state.hget("ai_personality_mappings", "current")

# 5. Enhancement logs
logs = await redis_state.lrange(f"ai_enhancement_log:{current_hour}", 0, -1)
```

## 🧪 Testing

### Test Scripts

```bash
# Comprehensive test suite
./test_ai_blending.py

# Usage examples
python gavatcore_engine/ai_blending_examples.py

# Manual testing
python -c "
from gavatcore_engine.ai_blending import AIBlendingSystem
import asyncio

async def test():
    ai = AIBlendingSystem()
    await ai.initialize()
    result = await ai.generate_response('Test', 'bot', 'entity')
    print(result)

asyncio.run(test())
"
```

### Mock Testing (No API Key)

```python
# API key olmadan test etme
import os

# Disable AI enhancement for testing
os.environ["AI_ENHANCEMENT_ENABLED"] = "false"

ai_system = AIBlendingSystem()
await ai_system.initialize()

# Bu None döndürecek ama hata vermeyecek
result = await ai_system.generate_response("test", "bot", "entity")
assert result is None
```

## 🔧 Production Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY=your_openai_api_key_here

# Optional optimization
export AI_MODEL=gpt-4o              # Model selection
export AI_MAX_TOKENS=150            # Token limit
export AI_TEMPERATURE=0.7           # Creativity level
export AI_COST_LIMIT=10.0           # Hourly cost limit (USD)
export AI_REQUESTS_PER_MINUTE=60    # Rate limiting
export AI_ENHANCEMENT_ENABLED=true  # Enable/disable

# Redis configuration
export REDIS_URL=redis://localhost:6379/0
```

### Cost Optimization

```python
# Maliyet optimizasyonu için öneriler

# 1. Ucuz model kullan
config.model = "gpt-4o-mini"  # 10x cheaper than gpt-4o

# 2. Token limitlerini ayarla
config.max_tokens = 100  # Shorter responses

# 3. Temperature'ı düşür
config.temperature = 0.5  # More deterministic, less creative

# 4. Saatlik limitler
config.cost_limit_per_hour = 5.0  # $5/hour limit

# 5. Rate limiting
config.requests_per_minute = 30  # Slow down requests
```

### Model Pricing (2024)

| Model | Input (per 1K tokens) | Output (per 1K tokens) | Use Case |
|-------|----------------------|------------------------|----------|
| gpt-4o | $0.005 | $0.015 | High quality, production |
| gpt-4o-mini | $0.00015 | $0.0006 | Cost-effective, good quality |
| gpt-3.5-turbo | $0.0015 | $0.002 | Basic enhancement |

### Performance Monitoring

```python
# Performance metrics to monitor
metrics = {
    "requests_per_minute": "API call frequency",
    "avg_response_time": "Response latency", 
    "cost_per_hour": "Operational cost",
    "success_rate": "Request success percentage",
    "token_efficiency": "Tokens per successful enhancement"
}

# Redis'te otomatik tracking
# Prometheus metrics için export edebilir
```

## 🛡️ Security Best Practices

### API Key Management

```python
# ✅ GOOD: Environment variable
api_key = os.getenv("OPENAI_API_KEY")

# ❌ BAD: Hardcoded in code
api_key = "sk-1234567890abcdef..."  # NEVER DO THIS

# ✅ GOOD: Runtime check
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable required")
```

### Input Sanitization

```python
# Input validation and sanitization
def sanitize_input(text: str) -> str:
    if not text or len(text.strip()) == 0:
        raise ValueError("Empty input not allowed")
    
    if len(text) > 2000:  # Limit input length
        text = text[:2000]
    
    # Remove potentially harmful content
    text = text.replace("\x00", "")  # Remove null bytes
    
    return text.strip()

# Usage
sanitized_text = sanitize_input(user_input)
response = await ai_system.generate_response(sanitized_text, bot, entity)
```

### Rate Limiting

```python
# Production rate limiting
config = AIConfig(
    requests_per_minute=30,        # Conservative limit
    cost_limit_per_hour=10.0,      # Cost protection
    timeout=30,                    # Reasonable timeout
    max_retries=3                  # Limited retries
)
```

## 📊 Monitoring ve Analytics

### Key Metrics

```python
# Önemli metrikler
key_metrics = {
    "enhancement_success_rate": "% successful enhancements",
    "avg_processing_time": "Average response time",
    "cost_per_enhancement": "Cost per successful enhancement", 
    "tokens_per_request": "Average tokens used",
    "api_error_rate": "% of requests that failed",
    "hourly_cost_trend": "Cost trend over time"
}

# Grafana dashboard için metrics export
# Redis'ten metrics collect ederek dashboard oluştur
```

### Alerting

```python
# Alarm koşulları
alerts = {
    "high_cost": "Hourly cost > $10",
    "high_error_rate": "Error rate > 10%",
    "api_down": "No successful requests in 10 minutes",
    "quota_exceeded": "Rate limit exceeded",
    "slow_response": "Avg response time > 10 seconds"
}
```

## 🔄 Integration Examples

### Message Pool Integration

```python
# Message pool ile entegrasyon
from gavatcore_engine.message_pool import Message, MessageType

# AI-enhanced mesaj oluştur
message = Message(
    target_entity="@channel",
    content="Raw message",
    message_type=MessageType.TEXT,
    ai_enhanced=True,  # Enable AI enhancement
    session_name="yayincilara"
)

# Message pool automatically calls AI enhancement
message_id = await message_pool.add_message(message)
```

### Scheduler Integration

```python
# Scheduler ile entegrasyon
from gavatcore_engine.scheduler_engine import ScheduledTask, TaskType

# AI-enhanced scheduled task
task = ScheduledTask(
    task_type=TaskType.SCHEDULED_MESSAGE,
    target_entity="@vip_group",
    message_content="Raw scheduled message",
    cron_expression="0 9 * * *",  # Daily at 9 AM
    session_name="xxxgeisha",
    ai_enhanced=True  # Will be enhanced before sending
)

await scheduler_engine.add_task(task)
```

### FastAPI Integration

```python
# FastAPI endpoint'lerde kullanım
from fastapi import FastAPI

app = FastAPI()

@app.post("/enhance-message")
async def enhance_message(
    text: str,
    bot_name: str,
    enhancement_type: str = "persuasive"
):
    enhanced = await ai_system.generate_response(
        text=text,
        bot_name=bot_name,
        target_entity="api_request",
        enhancement_type=EnhancementType(enhancement_type)
    )
    
    return {
        "original": text,
        "enhanced": enhanced,
        "bot_name": bot_name,
        "enhancement_type": enhancement_type
    }
```

## ❓ Troubleshooting

### Common Issues

**API Key Error:**
```bash
# Check API key
echo $OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Cost Limit Exceeded:**
```python
# Check current costs
current_hour = datetime.utcnow().strftime("%Y-%m-%d_%H")
cost = await redis_state.get(f"ai_cost:{current_hour}")
print(f"Current hour cost: ${float(cost):.6f}")

# Reset cost counter (if needed)
await redis_state.delete(f"ai_cost:{current_hour}")
```

**Rate Limit Errors:**
```python
# Check rate limiting
usage_stats = await ai_system.get_usage_statistics()
print(f"Recent requests: {usage_stats.get('hourly_requests', 0)}")

# Adjust rate limits
config.requests_per_minute = 30  # Lower limit
```

**Redis Connection:**
```bash
# Check Redis
redis-cli ping

# Check AI data in Redis
redis-cli
> KEYS ai_*
> HGETALL ai_usage_stats
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test API connection
from gavatcore_engine.ai_blending import OpenAIClient

client = OpenAIClient(config)
response = await client.enhance_text("test", EnhancementType.PERSUASIVE)
print(f"Response: {response}")
```

## 📝 Changelog

### v1.0.0 (Current)
- ✅ OpenAI GPT-4o integration
- ✅ 6 enhancement types (persuasive, friendly, etc.)
- ✅ Production-ready cost control
- ✅ Comprehensive error handling
- ✅ Redis state management
- ✅ Conversation context tracking
- ✅ Rate limiting and timeout control
- ✅ Usage statistics and monitoring
- ✅ Bot personality mappings
- ✅ Retry logic with exponential backoff

### Planned Features
- 🔄 Azure OpenAI support
- 🔄 Anthropic Claude integration
- 🔄 Custom model fine-tuning
- 🔄 A/B testing framework
- 🔄 Advanced analytics dashboard

---

**💡 Production Ready**: Bu modül production ortamında kullanıma hazır. Gerçek API key ile test edilebilir ve maliyet kontrollü şekilde çalıştırılabilir. 