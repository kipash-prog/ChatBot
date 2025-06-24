# 🤖 Fullstack AI Chatbot (FastAPI + Redis + WebSocket)

This is a real-time AI chatbot built using:

- 🐍 **FastAPI** (Python backend)
- 🧠 **WebSockets** for live communication
- ⚡ **Redis Streams** for message passing
- 📦 **Redis Cache** for session storage
- 🧠 **GPT/LLM** (e.g. Hugging Face) for AI responses
- 🌐 **Plain HTML/JavaScript frontend**

---

---

## ⚙️ Requirements

- Python 3.9+
- Redis Server (local or Redis Cloud)
- Hugging Face or OpenAI API key (optional)
- Node.js (optional for React-based frontend)

---

## 🔧 Setup

### Backend

```bash
cd server
python -m venv env
env\Scripts\activate          # or `source env/bin/activate` on macOS/Linux

pip install -r requirements.txt


cd worker
python main.py     # listens to Redis stream and replies using GPT

cd server
uvicorn main:api --reload --port 3500

---


| Endpoint            | Method    | Description                |
| ------------------- | --------- | -------------------------- |
| `/token?name=guest` | POST      | Creates a new chat session |
| `/refresh_token`    | GET       | Refreshes session          |
| `/chat?token=...`   | WebSocket | Two-way communication      |

---

🌍 Environment Variables
Create a .env file like this:

env
Copy
Edit
REDIS_URL=redis://default:YOUR_PASSWORD@YOUR_HOST:PORT
HF_TOKEN=your_huggingface_api_token

---

🔐 Security Advice
✅ Never commit .env files or secrets

✅ Use wss:// and https:// in production

✅ Set CORS if using frontend on a different port

---

🧠 Powered By
FastAPI

Redis Streams

Hugging Face or OpenAI

---


🪪 License
MIT — for personal use








