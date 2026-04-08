"""Saulo v2 - Simplified medical chat interface.
FastAPI backend with Ollama integration.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from auth.router import router as auth_router
from chat.router import router as chat_router

# Get current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    print("[SAULO] v2 starting up...")
    print("   Admin user: xiute")
    yield
    print("[SAULO] v2 shutting down...")


# Create app
app = FastAPI(
    title="Saulo v2",
    description="Simplified chat interface with Ollama",
    version="2.0.0",
    lifespan=lifespan,
    docs_url=None,  # Disable /docs
    redoc_url=None,  # Disable /redoc
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# === ROOT ROUTE - MUST BE FIRST ===
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the chat interface at root."""
    index_path = os.path.join(BASE_DIR, "static", "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html not found")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()


# === API ROUTES ===
app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}


@app.get("/api/info")
async def api_info():
    """API info endpoint."""
    return {
        "name": "Saulo v2",
        "version": "2.0.0",
        "description": "Simplified chat interface with Ollama"
    }


# === STATIC FILES - MOUNT LAST ===
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
