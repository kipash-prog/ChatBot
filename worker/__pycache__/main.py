import asyncio
import json
from uuid import uuid4
from datetime import datetime

from src.redis.config import Redis
from src.redis.cache import Cache
from src.redis.stream import StreamConsumer
from src.redis.producer import Producer
from src.model.gptj import GPT
from src.schema.chat import Message


redis = Redis()


async def main():
    redis_client = await redis.create_connection()  # ✅ Single connection for all Redis ops
    cache = Cache(redis_client)
    consumer = StreamConsumer(redis_client)
    producer = Producer(redis_client)

    print("🚀 Stream consumer started — waiting for new messages")

    while True:
        response = await consumer.consume_stream(
            stream_channel="message_channel",
            count=1,
            block=0
        )

        if not response:
            continue

        for _stream, messages in response:
            for msg_id, fields in messages:
                # Extract token and message
                token, user_msg = next(iter(fields.items()))

                if isinstance(token, bytes):
                    token = token.decode("utf-8")

                if isinstance(user_msg, bytes):
                    user_msg = user_msg.decode("utf-8")

                print(f"📩 New message from [{token[:6]}…]: {user_msg}")

                # Add human message to cache
                human_entry = Message(
                    id=str(uuid4()),
                    msg=user_msg,
                    timestamp=datetime.now().isoformat(),
                    source="human"
                )
                await cache.add_message_to_cache(
                    token=token,
                    source="human",
                    message_data=human_entry.model_dump()
                )

                # Fetch recent history
                data = await cache.get_chat_history(token=token)
                history = data.get("messages", [])[-4:]
                prompt = " ".join(msg["msg"] for msg in history)

                # Send to model (run in thread to avoid blocking event loop)
                response_text = await asyncio.to_thread(GPT().query, input=prompt)

                bot_entry = Message(
                    id=str(uuid4()),
                    msg=response_text,
                    timestamp=datetime.now().isoformat(),
                    source="bot"
                )

                # Send response to Redis stream (response_channel)
                await producer.add_to_stream(
                    {token: json.dumps(bot_entry.model_dump())},
                    "response_channel"
                )

                # Add bot message to chat history
                await cache.add_message_to_cache(
                    token=token,
                    source="bot",
                    message_data=bot_entry.model_dump()
                )

                # Delete the message from the stream
                await consumer.delete_message("message_channel", msg_id)


if __name__ == "__main__":
    asyncio.run(main())
