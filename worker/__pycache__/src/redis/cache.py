import json
from redis.commands.json.path import Path

class Cache:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def get_chat_history(self, token):
        data = await self.redis.get(token)
        return json.loads(data) if data else None

    async def add_message_to_cache(self, token, source, message_data):
        # Add source to message
        message_data["source"] = source

        # Get existing chat history
        history = await self.get_chat_history(token)
        if not history:
            history = {"token": token, "name": "User", "messages": []}

        # Append new message
        history["messages"].append(message_data)

        # Save updated history
        await self.redis.set(token, json.dumps(history), ex=3600)

    
