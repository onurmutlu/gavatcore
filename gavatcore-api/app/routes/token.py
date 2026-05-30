#!/usr/bin/env python3
"""
🪙 Token Economy Routes
Basit leaderboard ve durum endpoint'leri (mock veri)
"""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/system/status")
async def get_system_status():
    total_users = 6
    total_tokens = 8150

    return {
        "success": True,
        "data": {
            "system_uptime": "5h 23m 15s",
            "api_requests": 1547,
            "total_users": total_users,
            "total_tokens": total_tokens,
            "total_transactions": 156,
            "xp_token_engine_status": "Active",
            "database_status": "Connected",
            "active_bots": [
                "gawatbaba_demo",
                "yayincilara_demo",
                "xxxgeisha_demo",
            ],
        },
        "message": "Token system status OK",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/leaderboard")
async def get_leaderboard():
    mock_users = {
        "yayincilaradal": {"balance": 2850, "total_earned": 4200, "total_spent": 1350},
        "gawatbaba_fan": {"balance": 2100, "total_earned": 3500, "total_spent": 1400},
        "vip_member_01": {"balance": 1950, "total_earned": 2800, "total_spent": 850},
        "xxxgeisha_lover": {"balance": 1250, "total_earned": 2400, "total_spent": 1150},
        "premium_user": {"balance": 1185, "total_earned": 1800, "total_spent": 615},
        "balkiz_simp": {"balance": 850, "total_earned": 1200, "total_spent": 350},
        "token_hunter": {"balance": 750, "total_earned": 1150, "total_spent": 400},
        "daily_active": {"balance": 650, "total_earned": 950, "total_spent": 300},
        "new_member": {"balance": 425, "total_earned": 600, "total_spent": 175},
        "beginner": {"balance": 325, "total_earned": 450, "total_spent": 125},
    }

    sorted_users = sorted(mock_users.items(), key=lambda x: x[1]["balance"], reverse=True)
    leaderboard = [
        {
            "rank": rank,
            "user_id": user_id,
            "balance": data["balance"],
            "total_earned": data["total_earned"],
            "total_spent": data["total_spent"],
        }
        for rank, (user_id, data) in enumerate(sorted_users, 1)
    ]

    return {
        "success": True,
        "data": {
            "leaderboard": leaderboard,
            "total_users": len(mock_users),
            "updated_at": datetime.now().isoformat(),
        },
        "message": f"Top {len(leaderboard)} kullanıcı",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/logs/recent")
async def get_recent_logs():
    logs = [
        {
            "user_id": "999999",
            "amount": 50,
            "type": "earn",
            "reason": "dm_reply",
            "timestamp": "2025-07-03T20:30:00",
        },
        {
            "user_id": "123456",
            "amount": -25,
            "type": "spend",
            "reason": "vip_content",
            "timestamp": "2025-07-03T19:15:00",
        },
        {
            "user_id": "654321",
            "amount": 100,
            "type": "earn",
            "reason": "daily_bonus",
            "timestamp": "2025-07-03T18:45:00",
        },
    ]
    return {
        "success": True,
        "data": {"logs": logs, "total_count": len(logs)},
        "message": f"Recent {len(logs)} transactions",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/campaign/stats")
async def get_campaign_stats():
    return {
        "success": True,
        "data": {
            "active": True,
            "current_members": 47,
            "target_members": 100,
            "progress_percent": 47,
            "time_remaining": "13 days",
            "bots_active": ["@yayincilara", "@babagavat", "@xxxgeisha"],
            "rewards_distributed": 1200,
            "last_update": datetime.now().isoformat(),
        },
        "message": "Campaign stats",
        "timestamp": datetime.now().isoformat(),
    }
