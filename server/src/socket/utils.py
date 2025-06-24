from typing import Optional
from fastapi import WebSocket, Query, status
from ..redis.config import Redis

from fastapi import WebSocketException

async def get_token(websocket: WebSocket, token: Optional[str] = Query(None)):
    if token is None or token == "":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    
    redis_client = await Redis().create_connection()  # ← must use instance, not class
    isexists = await redis_client.exists(token)
    
    if isexists == 1:
        return token
    else:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")


