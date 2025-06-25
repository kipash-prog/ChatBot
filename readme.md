# 📚 Full‑stack AI Chatbot (Python × Redis × GPT)

A minimal real‑time chatbot powered by **Python** (FastAPI), **Redis Streams/Cache**, and any **GPT‑style model** (e.g. HuggingFace inference endpoint).
The repo contains **two async services**:

| Service    | Path      | Role                                                                                      |
| ---------- | --------- | ----------------------------------------------------------------------------------------- |
| **API**    | `server/` | HTTP+WebSocket gateway, issues session tokens, relays user ↔ model messages through Redis |
| **Worker** | `worker/` | Consumes user messages from a Redis Stream, calls the GPT endpoint, pushes responses back |

---

## ⚡️ Quick Start

```bash
# clone & cd
$ git clone https://github.com/kipash-prog/ChatBot/
$ cd fullstack-ai-chatbot

# Python env (3.10+ recommended)
$ python -m venv env && source env/bin/activate

# install shared deps for both services
(env)$ pip install -r requirements.txt
```

### 1 · Redis

```bash
# local Redis (Docker)
$ docker run -p 6379:6379 redis:7-alpine
```

*or* use Redis Cloud and copy the URL *.env* vars below.\_

### 2 · Environment Variables

Create **`.env`** at the project root:

```env
# APP
APP_ENV=development

# REDIS
REDIS_URL=redis://default:<password>@localhost:6379

# MODEL (HuggingFace Inference API example)
HUGGINGFACE_TOKEN=hf_********************************
MODEL_URL=https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta
```

### 3 · Run the API (FastAPI + WebSocket)

```bash
(env)$ cd server
(env)$ uvicorn server.main:api --host 0.0.0.0 --port 3500 --reload
```

### 4 · Run the Worker

```bash
(env)$ cd worker
(env)$ python main.py
```

The worker keeps streaming:

```
🚀 Stream consumer started — waiting for new messages
```

---

## 🛠️  Architecture

```mermaid
graph TD
    subgraph Client
      A[Browser / Postman] -- GET /token --> API
      A -- WS /chat?token=... --> API
    end

    subgraph API (FastAPI)
      API -- XADD message_channel --> Redis
      Redis -- XREAD response_channel --> API
      API -- WebSocket --> A
    end

    subgraph Worker
      Redis --> Worker[Stream Consumer]
      Worker -- call GPT --> GPT[(LLM Endpoint)]
      Worker -- XADD response_channel --> Redis
    end

    Redis[(Redis Streams & Keys)]
```

* **Token Route** `POST /token?name=<user>` – returns `{token,name,messages:[]}` (stored as JSON with TTL = 1 h)
* **WebSocket** `/chat?token=` – validates token, forwards user text to Redis stream `message_channel`, waits on `response_channel`.
* Add authentication & refresh tokens `GET /token=ENTER TOKEN`, – returns `{token,name,messages:[]}` 
* **Worker** pulls the stream, calls GPT, publishes response, updates chat history.

---

## 🐍 Code Snippets

### Send a message to the stream

```python
producer = Producer(redis)
await producer.add_to_stream({token: text}, "message_channel")
```

### Consume & respond (worker)

```python
response = await consumer.consume_stream("message_channel", count=1)
for _, msgs in response:
    for msg_id, data in msgs:
        token, user_text = next(iter(data.items()))
        llm_answer = GPT().query(user_text)
        await producer.add_to_stream({token: llm_answer}, "response_channel")
        await consumer.delete_message("message_channel", msg_id)
```

---

## 🏃‍♂️  Example cURL

```bash
# Get token
token=$(curl -s "http://localhost:3500/token?name=guest" | jq -r .token)
# Connect via websocat (brew install websocat)
websocat "ws://localhost:3500/chat?token=$token"
```

---

## 📝  TODO / Ideas

* Swap GPT endpoint with local model (e.g. Text‑Generation‑Inference or Ollama)
* Front‑end React client (or simple HTML/JS)
* Docker‑compose for one‑command spin‑up

---

## 📄 License

MIT © 2025  kidus shimelis
