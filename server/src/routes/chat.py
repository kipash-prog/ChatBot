import uuid
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from server.src.schema.chat import Chat
from server.src.redis.config import Redis
from server.src.socket.connection import ConnectionManager
from server.src.socket.utils import get_token
from ..redis.stream import StreamConsumer
from ..redis.producer import Producer

chat = APIRouter()
redis = Redis()
manager = ConnectionManager()


@chat.post("/token")
async def create_token(name: str):
    new_token = str(uuid.uuid4())

    chat_session = {
        "token": new_token,
        "name": name,
        "messages": []
    }

    redis_client = await redis.create_connection()
    await redis_client.setex(new_token, 3600, json.dumps(chat_session))
    return chat_session


@chat.get("/refresh_token")
async def refresh_token(token: str):
    redis_client = await redis.create_connection()
    raw = await redis_client.get(token)
    if raw is None:
        raise HTTPException(404, "Session expired")
    return json.loads(raw)


@chat.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, token: str = Depends(get_token)):
    await websocket.accept()
    await manager.connect(websocket)

    redis_client = await redis.create_connection()
    producer = Producer(redis_client)
    consumer = StreamConsumer(redis_client)

    try:
        while True:
            # Receive message from frontend
            data = await websocket.receive_text()
            print(f"Received from frontend: {data}")  # Debug log
            
            # Publish to Redis stream
            stream_data = {token: data}
            await producer.add_to_stream(stream_data, "message_channel")
            
            # Wait for and process response
            while True:
                response = await consumer.consume_stream(
                    stream_channel="response_channel", 
                    count=1, 
                    block=5000
                )
                
                if not response:
                    await asyncio.sleep(0.1)
                    continue

                for stream, messages in response:
                    for message in messages:
                        message_id = message[0]
                        message_data = message[1]
                        
                        # Decode the message
                        decoded_data = {
                            k.decode('utf-8') if isinstance(k, bytes) else k:
                            v.decode('utf-8') if isinstance(v, bytes) else v
                            for k, v in message_data.items()
                        }
                        
                        # Check if this message is for our token
                        response_token = next(iter(decoded_data))
                        if token != response_token:
                            continue
                            
                        response_message = decoded_data[response_token]
                        print(f"Response from Redis: {response_message}")  # Debug log
                        
                        try:
                            # Parse the response JSON
                            response_json = json.loads(response_message)
                            
                            # Extract the generated text
                            if isinstance(response_json, list):
                                generated_text = response_json[0].get("generated_text", "No response generated")
                            elif isinstance(response_json, dict):
                                generated_text = response_json.get("generated_text", "No response generated")
                            else:
                                generated_text = str(response_json)
                                
                            # Clean up the response
                            if 'Human:' in generated_text and 'Bot:' in generated_text:
                                generated_text = generated_text.split('Bot:')[-1].strip()
                            
                            # Send the clean response to frontend
                            await websocket.send_text(generated_text)
                            print(f"Sent to frontend: {generated_text}")  # Debug log
                            
                        except json.JSONDecodeError:
                            # If not JSON, send raw message
                            await websocket.send_text(response_message)
                            print(f"Sent raw to frontend: {response_message}")  # Debug log
                            
                        # Delete the processed message
                        await consumer.delete_message("response_channel", message_id)
                        break
                break

    except WebSocketDisconnect:
        print(f"Client #{token} disconnected")
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011)