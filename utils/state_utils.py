# utils/state_utils.py

import asyncio

# Global in-memory state
_STATE_STORE = {}
_LOCK = asyncio.Lock()

async def set_state(user_id, key, value):
    async with _LOCK:
        user_id = str(user_id)
        if user_id not in _STATE_STORE:
            _STATE_STORE[user_id] = {}
        _STATE_STORE[user_id][key] = value

async def get_state(user_id, key, default=None):
    async with _LOCK:
        user_id = str(user_id)
        return _STATE_STORE.get(user_id, {}).get(key, default)

async def clear_state(user_id, key=None):
    async with _LOCK:
        user_id = str(user_id)
        if user_id in _STATE_STORE:
            if key:
                _STATE_STORE[user_id].pop(key, None)
            else:
                _STATE_STORE.pop(user_id, None)

async def dump_state():
    """Debug amaçlı tüm state’i göster."""
    async with _LOCK:
        return _STATE_STORE.copy()
