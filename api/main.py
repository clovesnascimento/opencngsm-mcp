"""
OpenCngsm v3.0 - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OpenCngsm v3.0",
    description="AI Assistant with Voice Capabilities",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register routes
try:
    from api.routes.voice import router as voice_router
    app.include_router(voice_router)
    logger.info("✅ Voice routes registered")
except Exception as e:
    logger.warning(f"⚠️ Failed to register voice routes: {e}")

# Health check
@app.get("/")
async def root():
    return {
        "name": "OpenCngsm v3.0",
        "version": "3.0.0",
        "status": "running",
        "features": [
            "Voice Input (Voxtral STT)",
            "Voice Output (Kokoro TTS)",
            "Telegram Integration",
            "Web Interface"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
