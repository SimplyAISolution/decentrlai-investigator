import os
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as aioredis

router = APIRouter(tags=["WebSockets"])

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

@router.websocket("/investigations/{investigation_id}/ws")
async def investigation_ws(websocket: WebSocket, investigation_id: str):
    await websocket.accept()
    client = aioredis.from_url(REDIS_URL)
    pubsub = client.pubsub()
    channel = f"channel:investigation:{investigation_id}"
    await pubsub.subscribe(channel)

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                data = message["data"].decode("utf-8") if isinstance(message["data"], bytes) else message["data"]
                await websocket.send_text(data)
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await client.close()
