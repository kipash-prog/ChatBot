import os
import json
from dotenv import load_dotenv, find_dotenv
import redis.asyncio as redis

load_dotenv(find_dotenv())  # Explicitly load .env

class Redis:
    def __init__(self):
        self.REDIS_URL = os.getenv("REDIS_URL")
        print(f"Redis URL in Redis class: {self.REDIS_URL}")  # Debug print
        if not self.REDIS_URL:
            raise RuntimeError("Missing REDIS_URL environment variable")

    async def create_connection(self):
        return redis.from_url(self.REDIS_URL, decode_responses=True)

    async def save_json(self, key: str, data: dict, ex: int = 3600):
        conn = await self.create_connection()
        await conn.set(key, json.dumps(data), ex=ex)

    async def get_json(self, key: str):
        conn = await self.create_connection()
        raw = await conn.get(key)
        return json.loads(raw) if raw else None
