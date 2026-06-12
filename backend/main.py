import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, schemes, whatsapp

app = FastAPI(
    title="YojanaBot API",
    description="AI-powered government scheme navigator for rural India",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router,     prefix="/api/chat",     tags=["Chat"])
app.include_router(schemes.router,  prefix="/api/schemes",  tags=["Schemes"])
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["WhatsApp"])

@app.get("/")
async def root():
    return {"message": "YojanaBot API is running"}

@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}