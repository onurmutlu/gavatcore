#!/usr/bin/env python3
"""
BabaGAVAT Coin API Endpoints - Sokak Zekası ile Güçlendirilmiş Coin API
FlirtMarket / GavatCore için Onur Metodu API entegrasyonu
BabaGAVAT'ın sokak tecrübesi ile coin ekonomisi API'si
"""

from fastapi import FastAPI, HTTPException, Depends, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog

from core.coin_service import babagavat_coin_service, CoinTransactionType, UserType

logger = structlog.get_logger("babagavat.coin_api")

# FastAPI app
app = FastAPI(
    title="BabaGAVAT Coin API",
    description="Sokak Zekası ile Güçlendirilmiş Coin Sistemi - Onur Metodu",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# ==================== PYDANTIC MODELS ====================

class CoinBalanceResponse(BaseModel):
    """Coin bakiye response modeli"""
    user_id: int
    balance: int
    babagavat_status: str = Field(description="BabaGAVAT'ın kullanıcı değerlendirmesi")

class UserStatsResponse(BaseModel):
    """Kullanıcı istatistikleri response modeli"""
    balance: int
    total_earned: int
    total_spent: int
    user_type: str
    babagavat_tier: str = Field(description="bronze, silver, gold, platinum")
    daily_stats: Dict[str, Any]
    babagavat_status: str

class AddCoinsRequest(BaseModel):
    """Coin ekleme request modeli"""
    user_id: int = Field(description="Hedef kullanıcı ID")
    amount: int = Field(gt=0, description="Eklenecek coin miktarı")
    reason: str = Field(description="Coin ekleme nedeni")
    admin_id: Optional[int] = Field(description="Admin kullanıcı ID")

class SpendCoinsRequest(BaseModel):
    """Coin harcama request modeli"""
    user_id: int = Field(description="Kullanıcı ID")
    amount: int = Field(gt=0, description="Harcanacak coin miktarı")
    item_type: str = Field(description="Harcama tipi: message_to_performer, vip_content_view, etc.")
    target_user_id: Optional[int] = Field(description="Hedef kullanıcı ID (şovcu vs.)")
    metadata: Optional[Dict[str, Any]] = Field(description="Ek bilgiler")

class ReferralBonusRequest(BaseModel):
    """Referans bonusu request modeli"""
    referrer_id: int = Field(description="Davet eden kullanıcı ID")
    referred_id: int = Field(description="Davet edilen kullanıcı ID")

class MessageToPerformerRequest(BaseModel):
    """Şovcuya mesaj request modeli"""
    user_id: int = Field(description="Mesaj gönderen kullanıcı ID")
    performer_id: int = Field(description="Şovcu kullanıcı ID")
    message_content: str = Field(description="Mesaj içeriği")

class DailyTaskRequest(BaseModel):
    """Günlük görev request modeli"""
    user_id: int = Field(description="Kullanıcı ID")
    task_type: str = Field(description="Görev tipi: daily_login, group_join, content_share, etc.")

class TransactionHistoryResponse(BaseModel):
    """İşlem geçmişi response modeli"""
    transactions: List[Dict[str, Any]]
    total_count: int
    babagavat_verified: bool = True

class LeaderboardResponse(BaseModel):
    """Leaderboard response modeli"""
    leaderboard: List[Dict[str, Any]]
    babagavat_analysis: str = "sokak_zekasi_siralaması"

# ==================== AUTH DEPENDENCY ====================

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Token doğrulama"""
    try:
        # FIX: Correct way to access token from HTTPAuthorizationCredentials
        token = credentials.credentials if credentials else None
        
        if not token or len(token) < 10:
            raise HTTPException(
                status_code=401,
                detail="Geçersiz token"
            )
        
        # Simple token validation for demo
        if token.startswith("babagavat_"):
            return {"user_id": int(token.split("_")[1]), "valid": True}
        
        raise HTTPException(
            status_code=401,
            detail="Token doğrulanamadı"
        )
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Token doğrulama hatası"
        )

# ==================== COIN BALANCE ENDPOINTS ====================

@app.get("/coins/balance/{user_id}", response_model=CoinBalanceResponse)
async def get_coin_balance(
    user_id: int,
    token: str = Depends(verify_token)
):
    """
    Kullanıcının coin bakiyesini getir - BabaGAVAT kontrolü
    """
    try:
        balance = await babagavat_coin_service.get_balance(user_id)
        stats = await babagavat_coin_service.get_user_stats(user_id)
        
        return CoinBalanceResponse(
            user_id=user_id,
            balance=balance,
            babagavat_status=stats.get("babagavat_status", "bilinmeyen")
        )
        
    except Exception as e:
        logger.error(f"❌ BabaGAVAT bakiye API hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BabaGAVAT: Bakiye getirme hatası - {str(e)}"
        )

@app.get("/coins/stats/{user_id}", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: int,
    token: str = Depends(verify_token)
):
    """
    Kullanıcının detaylı coin istatistikleri - BabaGAVAT analizi
    """
    try:
        stats = await babagavat_coin_service.get_user_stats(user_id)
        
        return UserStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"❌ BabaGAVAT stats API hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BabaGAVAT: İstatistik getirme hatası - {str(e)}"
        )

# ==================== COIN MANAGEMENT ENDPOINTS ====================

@app.post("/coins/add")
async def add_coins(
    request: AddCoinsRequest,
    token: str = Depends(verify_token)
):
    """
    Admin coin ekleme - BabaGAVAT onayı ile
    """
    try:
        if not request.admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="BabaGAVAT: Admin ID gerekli - Sokak kuralları!"
            )
        
        success = await babagavat_coin_service.babagavat_admin_add_coins(
            admin_id=request.admin_id,
            target_user_id=request.user_id,
            amount=request.amount,
            reason=request.reason
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="BabaGAVAT: Coin ekleme başarısız - Günlük limit aşıldı!"
            )
        
        return {
            "success": True,
            "message": f"BabaGAVAT: {request.amount} coin başarıyla eklendi!",
            "user_id": request.user_id,
            "amount": request.amount,
            "babagavat_approved": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ BabaGAVAT coin ekleme API hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BabaGAVAT: Coin ekleme hatası - {str(e)}"
        )

@app.post("/coins/spend")
async def spend_coins(
    request: SpendCoinsRequest,
    token: str = Depends(verify_token)
):
    """
    Coin harcama - BabaGAVAT kontrolü ile
    """
    try:
        # İşlem tipini belirle
        transaction_type_map = {
            "message_to_performer": CoinTransactionType.SPEND_MESSAGE,
            "vip_content_view": CoinTransactionType.SPEND_VIP_CONTENT,
            "vip_group_monthly": CoinTransactionType.SPEND_VIP_GROUP,
            "special_show_request": CoinTransactionType.SPEND_SPECIAL_SHOW
        }
        
        transaction_type = transaction_type_map.get(request.item_type)
        if not transaction_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"BabaGAVAT: Geçersiz harcama tipi - {request.item_type}"
            )
        
        success = await babagavat_coin_service.spend_coins(
            user_id=request.user_id,
            amount=request.amount,
            transaction_type=transaction_type,
            description=f"BabaGAVAT {request.item_type} harcaması",
            related_user_id=request.target_user_id,
            metadata=request.metadata
        )
        
        if not success:
            # Bakiye kontrolü
            balance = await babagavat_coin_service.get_balance(request.user_id)
            if balance < request.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"BabaGAVAT: Yetersiz bakiye! Mevcut: {balance}, Gerekli: {request.amount}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="BabaGAVAT: Günlük harcama limiti aşıldı!"
                )
        
        return {
            "success": True,
            "message": f"BabaGAVAT: {request.amount} coin başarıyla harcandı!",
            "user_id": request.user_id,
            "amount": request.amount,
            "item_type": request.item_type,
            "babagavat_approved": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ BabaGAVAT coin harcama API hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BabaGAVAT: Coin harcama hatası - {str(e)}"
        )

# ==================== EARNING ENDPOINTS ====================

@app.post("/coins/referral-bonus")
async def referral_bonus(
    request: ReferralBonusRequest,
    token: str = Depends(verify_token)
):
    """
    Referans bonusu ver - BabaGAVAT sokak ödülü
    """
    try:
        success = await babagavat_coin_service.babagavat_referral_bonus(
            referrer_id=request.referrer_id,
            referred_id=request.referred_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="BabaGAVAT: Referans bonusu verilemedi - Günlük limit aşıldı!"
            )
        
        return {
            "success": True,
            "message": "BabaGAVAT: Referans bonusu başarıyla verildi!",
            "referrer_id": request.referrer_id,
            "referred_id": request.referred_id,
            "bonus_amount": babagavat_coin_service.earning_rates["referral_bonus"],
            "babagavat_approved": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ BabaGAVAT referans bonusu API hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BabaGAVAT: Referans bonusu hatası - {str(e)}"
        )

@app.post("/coins/message-to-performer")
async def message_to_performer(
    request: MessageToPerformerRequest,
    token: str = Depends(verify_token)
):
    """
    Şovcuya mesaj gönder - BabaGAVAT coin sistemi
    """
    try:
        success = await babagavat_coin_service.babagavat_message_to_performer(
            user_id=request.user_id,
            performer_id=request.performer_id,
            message_content=request.message_content
        )
        
        if not success:
            balance = await babagavat_coin_service.get_balance(request.user_id)
            cost = babagavat_coin_service.coin_prices["message_to_performer"]
            
            if balance < cost:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"BabaGAVAT: Yetersiz bakiye! Mevcut: {balance}, Gerekli: {cost}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="BabaGAVAT: Günlük mesaj limiti aşıldı!"
                )
        
        return {
            "success": True,
            "message": "BabaGAVAT: Şovcuya mesaj başarıyla gönderildi!",
            "user_id": request.user_id,
            "performer_id": request.performer_id,
            "cost": babagavat_coin_service.coin_prices["message_to_performer"],
            "babagavat_approved": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ BabaGAVAT şovcuya mesaj API hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BabaGAVAT: Şovcuya mesaj hatası - {str(e)}"
        )

@app.post("/coins/daily-task")
async def daily_task_reward(
    request: DailyTaskRequest,
    token: str = Depends(verify_token)
):
    """
    Günlük görev ödülü ver - BabaGAVAT sokak sistemi
    """
    try:
        success = await babagavat_coin_service.babagavat_daily_task_reward(
            user_id=request.user_id,
            task_type=request.task_type
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="BabaGAVAT: Günlük görev ödülü verilemedi - Limit aşıldı!"
            )
        
        return {
            "success": True,
            "message": f"BabaGAVAT: {request.task_type} görevi tamamlandı!",
            "user_id": request.user_id,
            "task_type": request.task_type,
            "reward_amount": babagavat_coin_service.earning_rates["daily_task"],
            "babagavat_approved": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ BabaGAVAT günlük görev API hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BabaGAVAT: Günlük görev hatası - {str(e)}"
        )

# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/coins/transactions/{user_id}", response_model=TransactionHistoryResponse)
async def get_transaction_history(
    user_id: int,
    limit: int = 50,
    token: str = Depends(verify_token)
):
    """
    Kullanıcının işlem geçmişi - BabaGAVAT kayıtları
    """
    try:
        transactions = await babagavat_coin_service.get_babagavat_transaction_history(
            user_id=user_id,
            limit=limit
        )
        
        return TransactionHistoryResponse(
            transactions=transactions,
            total_count=len(transactions),
            babagavat_verified=True
        )
        
    except Exception as e:
        logger.error(f"❌ BabaGAVAT işlem geçmişi API hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BabaGAVAT: İşlem geçmişi hatası - {str(e)}"
        )

@app.get("/coins/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = 10,
    token: str = Depends(verify_token)
):
    """
    Coin leaderboard - BabaGAVAT sokak sıralaması
    """
    try:
        leaderboard = await babagavat_coin_service.get_babagavat_leaderboard(limit=limit)
        
        return LeaderboardResponse(
            leaderboard=leaderboard,
            babagavat_analysis="sokak_zekasi_siralaması"
        )
        
    except Exception as e:
        logger.error(f"❌ BabaGAVAT leaderboard API hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BabaGAVAT: Leaderboard hatası - {str(e)}"
        )

# ==================== SYSTEM INFO ENDPOINTS ====================

@app.get("/coins/prices")
async def get_coin_prices(token: str = Depends(verify_token)):
    """
    Coin fiyat listesi - BabaGAVAT sokak değerleri
    """
    try:
        return {
            "coin_prices": babagavat_coin_service.coin_prices,
            "earning_rates": babagavat_coin_service.earning_rates,
            "daily_limits": babagavat_coin_service.daily_limits,
            "babagavat_approved": True,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ BabaGAVAT fiyat listesi API hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BabaGAVAT: Fiyat listesi hatası - {str(e)}"
        )

@app.get("/coins/system-status")
async def get_system_status(token: str = Depends(verify_token)):
    """
    BabaGAVAT Coin sistemi durumu
    """
    try:
        return {
            "system_name": "BabaGAVAT Coin Service",
            "version": "1.0.0",
            "status": "active",
            "sokak_zekasi": "maksimum",
            "onur_metodu": "entegre",
            "babagavat_approval": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ BabaGAVAT sistem durumu API hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BabaGAVAT: Sistem durumu hatası - {str(e)}"
        )

# ==================== STARTUP EVENT ====================

@app.on_event("startup")
async def startup_event():
    """BabaGAVAT Coin API başlatma"""
    try:
        await babagavat_coin_service.initialize()
        logger.info("💪 BabaGAVAT Coin API başlatıldı - Sokak ekonomisi aktif!")
    except Exception as e:
        logger.error(f"❌ BabaGAVAT Coin API başlatma hatası: {e}")
        raise

if __name__ == "__main__":
    import uvicorn
    
    print("""
💪 BabaGAVAT Coin API - Sokak Zekası ile Güçlendirilmiş Coin Sistemi

🎯 Onur Metodu Entegrasyonu:
✅ Coin Balance Management
✅ Transaction Processing  
✅ Referral Bonus System
✅ Daily Task Rewards
✅ Message to Performer
✅ Admin Panel Functions
✅ Analytics & Leaderboard

🚀 API başlatılıyor...
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 