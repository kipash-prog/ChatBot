import json

class Cache:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    async def get_chat_history(self, token: str):
        raw = await self.redis_client.get(token)
        try:
            return json.loads(raw)
        except Exception:
            # raw might be "Kidus" or None
            return {"token": token, "name": raw or "Unknown", "messages": []}
    async def add_message_to_cache(self, token: str, source: str, message_data: dict):
        history = await self.get_chat_history(token)
        message_data["source"] = source
        history["messages"].append(message_data)
        await self.redis_client.set(token, json.dumps(history))
