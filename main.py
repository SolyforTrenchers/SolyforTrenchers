#!/usr/bin/env python3
"""
Soly - Main Application Entry Point
Starts all services: API, Blockchain Monitor, Twitter Bot
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

from api.main import app
from blockchain.monitor import BlockchainMonitor
from twitter.bot import SolyTwitterBot
from ai.analyzer import TokenAnalyzer
from config import settings, LOGGING_CONFIG
from database.database import init_db

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Global service instances
blockchain_monitor: Optional[BlockchainMonitor] = None
twitter_bot: Optional[SolyTwitterBot] = None
token_analyzer: Optional[TokenAnalyzer] = None


async def initialize_services():
    """Initialize all application services"""
    global blockchain_monitor, twitter_bot, token_analyzer
    
    logger.info("🚀 Initializing Soly services...")
    
    try:
        # Initialize database
        logger.info("📊 Initializing database...")
        await init_db()
        
        # Initialize AI Analyzer
        if settings.ENABLE_AI_ANALYSIS:
            logger.info("🤖 Initializing AI Analyzer...")
            token_analyzer = TokenAnalyzer(
                openai_api_key=settings.OPENAI_API_KEY,
                model=settings.AI_MODEL
            )
        
        # Initialize Blockchain Monitor
        if settings.ENABLE_BLOCKCHAIN_MONITOR:
            logger.info("🔍 Initializing Blockchain Monitor...")
            blockchain_monitor = BlockchainMonitor(
                rpc_url=settings.SOLANA_RPC_URL,
                websocket_url=settings.SOLANA_WS_URL
            )
            await blockchain_monitor.start()
        
        # Initialize Twitter Bot
        if settings.ENABLE_TWITTER_BOT:
            logger.info("🐦 Initializing Twitter Bot...")
            twitter_bot = SolyTwitterBot(
                api_key=settings.TWITTER_API_KEY,
                api_secret=settings.TWITTER_API_SECRET,
                access_token=settings.TWITTER_ACCESS_TOKEN,
                access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
                bearer_token=settings.TWITTER_BEARER_TOKEN
            )
            
            if blockchain_monitor and token_analyzer:
                await twitter_bot.start(blockchain_monitor, token_analyzer)
        
        logger.info("✅ All services initialized successfully!")
        logger.info("=" * 60)
        logger.info(f"🎯 Soly v{settings.APP_VERSION} is now running!")
        logger.info(f"🌐 Environment: {settings.ENVIRONMENT}")
        logger.info(f"📡 API Server: http://{settings.API_HOST}:{settings.API_PORT}")
        logger.info(f"📚 API Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise


async def shutdown_services():
    """Gracefully shutdown all services"""
    logger.info("🛑 Shutting down Soly services...")
    
    try:
        if twitter_bot:
            logger.info("Stopping Twitter bot...")
            await twitter_bot.stop()
        
        if blockchain_monitor:
            logger.info("Stopping blockchain monitor...")
            await blockchain_monitor.stop()
        
        logger.info("✅ All services stopped successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {sig}, initiating shutdown...")
    asyncio.create_task(shutdown_services())
    sys.exit(0)


async def run_health_check():
    """Run periodic health checks"""
    while True:
        try:
            await asyncio.sleep(60)  # Check every minute
            
            # Check service health
            if blockchain_monitor and not blockchain_monitor.is_running:
                logger.warning("⚠️ Blockchain monitor is not running!")
            
            if twitter_bot and not twitter_bot.is_running:
                logger.warning("⚠️ Twitter bot is not running!")
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Health check error: {e}")


async def main():
    """Main application entry point"""
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize services
        await initialize_services()
        
        # Start health check task
        health_check_task = asyncio.create_task(run_health_check())
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            health_check_task.cancel()
            await shutdown_services()
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║     🚀 SOLY - Trenchers' Companion        ║
    ║                                           ║
    ║  Autonomous agent for Solana traders      ║
    ║  Making the trenches a little less brutal ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Soly stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
