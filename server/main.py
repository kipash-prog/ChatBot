import os
from dotenv import load_dotenv

# Load .env before any other imports
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import uvicorn
from server.src.routes.chat import chat
api = FastAPI()
api.include_router(chat, prefix="")
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ["http://127.0.0.1:5500"] or ["http://localhost:3000"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.get("/test")
async def root():
    return {"msg": "API is Online"}

if __name__ == "__main__":
    if os.environ.get("APP_ENV") == "development":
        uvicorn.run("main:api", host="0.0.0.0", port=3500, workers=4, reload=True)