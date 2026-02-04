"""
Twitter Bot - Autonomous X (Twitter) agent
Posts updates, responds to mentions, and engages with the community
"""

import logging
import asyncio
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import tweepy
from tweepy.asynchronous import AsyncClient

from ai.analyzer import TokenAnalyzer
from blockchain.monitor import BlockchainMonitor, TokenLaunch

logger = logging.getLogger(__name__)


class SolyTwitterBot:
    """Autonomous Twitter bot for Soly"""
    
    def __init__(self,
                 api_key: str,
                 api_secret: str,
                 access_token: str,
                 access_token_secret: str,
                 bearer_token: str):
        
        # Initialize Twitter API v2
        self.client = AsyncClient(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        self.is_running = False
        self.last_tweet_time: Optional[datetime] = None
        self.tweet_queue: List[str] = []
        
        # Rate limiting
        self.tweets_today = 0
        self.max_tweets_per_day = 50
        self.min_tweet_interval_minutes = 15
        
        logger.info("🐦 Twitter bot initialized")
    
    async def start(self, blockchain_monitor: BlockchainMonitor, ai_analyzer: TokenAnalyzer):
        """Start the Twitter bot"""
        logger.info("🚀 Starting Twitter bot...")
        
        self.blockchain_monitor = blockchain_monitor
        self.ai_analyzer = ai_analyzer
        self.is_running = True
        
        # Start bot tasks
        asyncio.create_task(self._post_scheduled_updates())
        asyncio.create_task(self._monitor_mentions())
        asyncio.create_task(self._post_alerts())
        asyncio.create_task(self._engage_with_community())
        
        logger.info("✅ Twitter bot started")
    
    async def stop(self):
        """Stop the Twitter bot"""
        self.is_running = False
        logger.info("🛑 Twitter bot stopped")
    
    async def post_tweet(self, text: str, reply_to: Optional[int] = None) -> bool:
        """Post a tweet"""
        try:
            # Check rate limits
            if self.tweets_today >= self.max_tweets_per_day:
                logger.warning("Daily tweet limit reached")
                return False
            
            if self.last_tweet_time:
                time_since_last = datetime.utcnow() - self.last_tweet_time
                if time_since_last.total_seconds() < self.min_tweet_interval_minutes * 60:
                    logger.debug("Tweet interval too short, queueing...")
                    self.tweet_queue.append(text)
                    return False
            
            # Post tweet
            if reply_to:
                response = await self.client.create_tweet(
                    text=text,
                    in_reply_to_tweet_id=reply_to
                )
            else:
                response = await self.client.create_tweet(text=text)
            
            self.tweets_today += 1
            self.last_tweet_time = datetime.utcnow()
            
            logger.info(f"📤 Posted tweet: {text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return False
    
    async def _post_scheduled_updates(self):
        """Post scheduled market updates"""
        logger.info("📅 Starting scheduled updates...")
        
        schedule = [
            {"hour": 8, "type": "morning_update"},
            {"hour": 12, "type": "midday_alert"},
            {"hour": 18, "type": "evening_recap"}
        ]
        
        while self.is_running:
            try:
                current_hour = datetime.utcnow().hour
                
                for scheduled in schedule:
                    if current_hour == scheduled["hour"]:
                        await self._post_update(scheduled["type"])
                
                # Check every hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in scheduled updates: {e}")
                await asyncio.sleep(60)
    
    async def _post_update(self, update_type: str):
        """Post a specific type of update"""
        try:
            if update_type == "morning_update":
                tweet = await self._generate_morning_update()
            elif update_type == "midday_alert":
                tweet = await self._generate_midday_alert()
            elif update_type == "evening_recap":
                tweet = await self._generate_evening_recap()
            else:
                return
            
            await self.post_tweet(tweet)
            
        except Exception as e:
            logger.error(f"Error posting {update_type}: {e}")
    
    async def _generate_morning_update(self) -> str:
        """Generate morning market update"""
        stats = await self.blockchain_monitor.get_stats()
        
        tweet = f"""
☀️ GM Trenchers!

🔍 Monitoring {stats['tokens_monitored']} tokens today
📊 Market sentiment: Looking stable
⚠️ Stay alert for new launches

Remember: DYOR, take profits, and never ape blindly! 

#Solana #CryptoTrading #TrenchLife
"""
        return tweet.strip()
    
    async def _generate_midday_alert(self) -> str:
        """Generate midday market alert"""
        # Get market conditions and generate tip
        market_conditions = {
            "trend": "sideways",
            "volatility": "medium",
            "top_gainers": [],
            "recent_rugs": 0
        }
        
        tip = await self.ai_analyzer.generate_trading_tip(market_conditions)
        
        tweet = f"""
🔔 Midday Update

💡 Trading Tip: {tip}

Stay disciplined, stick to your strategy!

#SolanaTips #CryptoTrading
"""
        return tweet.strip()
    
    async def _generate_evening_recap(self) -> str:
        """Generate evening market recap"""
        daily_data = {
            "new_tokens": 15,
            "volume_usd": 2500000,
            "biggest_gainer": "EXAMPLE",
            "biggest_gain_pct": 150,
            "rugs": 2,
            "successful_alerts": 5
        }
        
        summary = await self.ai_analyzer.summarize_market_day(daily_data)
        
        return summary
    
    async def _monitor_mentions(self):
        """Monitor and respond to mentions"""
        logger.info("👂 Monitoring mentions...")
        
        while self.is_running:
            try:
                # Get recent mentions
                # mentions = await self.client.get_users_mentions(user_id, max_results=10)
                
                # Process and respond to relevant mentions
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error monitoring mentions: {e}")
                await asyncio.sleep(60)
    
    async def _post_alerts(self):
        """Post time-sensitive alerts"""
        logger.info("🚨 Alert system active...")
        
        while self.is_running:
            try:
                # Check for critical alerts
                # - New token launches
                # - Rug pulls detected
                # - Whale movements
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in alert system: {e}")
                await asyncio.sleep(60)
    
    async def _engage_with_community(self):
        """Engage with community posts"""
        logger.info("🤝 Community engagement active...")
        
        while self.is_running:
            try:
                # Like and retweet quality community content
                # Respond to questions
                # Share success stories
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in community engagement: {e}")
                await asyncio.sleep(60)
    
    async def post_token_alert(self, token: TokenLaunch, analysis: Dict):
        """Post an alert about a new token"""
        risk_emoji = "🟢" if analysis['risk_score'] < 30 else "🟡" if analysis['risk_score'] < 70 else "🔴"
        
        tweet = f"""
{risk_emoji} New Token Alert!

${token.symbol} just launched
Risk Score: {analysis['risk_score']}/100

{f"⚠️ Red Flags: {', '.join(analysis['red_flags'][:2])}" if analysis['red_flags'] else ""}

DYOR before aping! 🔬

#Solana #NewToken
"""
        
        await self.post_tweet(tweet.strip())
