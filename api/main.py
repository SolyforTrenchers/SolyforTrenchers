"""
Soly API - Main FastAPI application
Provides REST endpoints for token analysis, alerts, and community features
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import List, Optional

from api.routes import tokens, alerts, analytics, community
from api.dependencies import get_db, get_current_user
from blockchain.monitor import BlockchainMonitor
from ai.analyzer import TokenAnalyzer
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
blockchain_monitor: Optional[BlockchainMonitor] = None
token_analyzer: Optional[TokenAnalyzer] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources"""
    global blockchain_monitor, token_analyzer
    
    logger.info("🚀 Starting Soly API...")
    
    # Initialize blockchain monitor
    blockchain_monitor = BlockchainMonitor(
        rpc_url=settings.SOLANA_RPC_URL,
        websocket_url=settings.SOLANA_WS_URL
    )
    await blockchain_monitor.start()
    
    # Initialize AI analyzer
    token_analyzer = TokenAnalyzer(
        openai_api_key=settings.OPENAI_API_KEY,
        model=settings.AI_MODEL
    )
    
    logger.info("✅ Soly API started successfully")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down Soly API...")
    await blockchain_monitor.stop()
    logger.info("👋 Soly API stopped")


# Create FastAPI app
app = FastAPI(
    title="Soly API",
    description="Autonomous agent API for Solana trenchers",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tokens.router, prefix="/api/v1/tokens", tags=["tokens"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(community.router, prefix="/api/v1/community", tags=["community"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Soly API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "blockchain_monitor": blockchain_monitor.is_running if blockchain_monitor else False,
        "ai_analyzer": token_analyzer.is_ready if token_analyzer else False
    }


@app.get("/api/v1/stats")
async def get_stats():
    """Get current system statistics"""
    if not blockchain_monitor:
        raise HTTPException(status_code=503, detail="Blockchain monitor not ready")
    
    stats = await blockchain_monitor.get_stats()
    return {
        "tokens_monitored": stats.get("tokens_monitored", 0),
        "alerts_sent_today": stats.get("alerts_sent_today", 0),
        "successful_calls": stats.get("successful_calls", 0),
        "active_users": stats.get("active_users", 0),
        "uptime_seconds": stats.get("uptime_seconds", 0)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
