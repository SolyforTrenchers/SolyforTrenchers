"""
AI Analyzer - Token and market sentiment analysis using LLMs
Uses OpenAI/Anthropic to analyze tokens, social sentiment, and generate insights
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


class TokenAnalyzer:
    """AI-powered token and market analyzer"""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4-turbo-preview"):
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.model = model
        self.is_ready = True
        
        # Analysis cache to avoid redundant API calls
        self.cache: Dict[str, Dict] = {}
        
        logger.info(f"🤖 AI Analyzer initialized with model: {model}")
    
    async def analyze_token_contract(self, 
                                    contract_data: Dict,
                                    holder_data: Dict,
                                    liquidity_data: Dict) -> Dict:
        """Analyze token contract for red flags and opportunities"""
        
        prompt = f"""
You are a Solana blockchain expert analyzing tokens for potential risks and opportunities.

Token Contract Analysis:
- Total Supply: {contract_data.get('total_supply', 'Unknown')}
- Decimals: {contract_data.get('decimals', 'Unknown')}
- Mint Authority: {'Revoked' if contract_data.get('mint_authority_revoked') else 'Active'}
- Freeze Authority: {'Revoked' if contract_data.get('freeze_authority_revoked') else 'Active'}

Holder Distribution:
- Total Holders: {holder_data.get('total_holders', 0)}
- Top 10 Holdings: {holder_data.get('top_10_pct', 0)}%
- Dev Wallet Holdings: {holder_data.get('dev_holdings_pct', 0)}%

Liquidity:
- Total Liquidity: ${liquidity_data.get('total_usd', 0):,.2f}
- Liquidity Locked: {'Yes' if liquidity_data.get('locked') else 'No'}
- Lock Duration: {liquidity_data.get('lock_duration_days', 0)} days

Analyze this token and provide:
1. Risk Score (0-100, where 100 is highest risk)
2. Key Red Flags (if any)
3. Positive Signals (if any)
4. Overall Recommendation (Buy/Hold/Avoid)
5. Brief reasoning

Format as JSON.
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Solana token analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Fallback if response isn't valid JSON
                analysis = {
                    "risk_score": 50,
                    "red_flags": ["Unable to parse analysis"],
                    "positive_signals": [],
                    "recommendation": "HOLD",
                    "reasoning": analysis_text
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return {
                "risk_score": 100,
                "red_flags": [f"Analysis failed: {str(e)}"],
                "positive_signals": [],
                "recommendation": "AVOID",
                "reasoning": "Could not complete analysis"
            }
    
    async def analyze_social_sentiment(self, 
                                      token_symbol: str,
                                      tweets: List[str]) -> Dict:
        """Analyze social media sentiment around a token"""
        
        tweets_text = "\n".join([f"- {tweet}" for tweet in tweets[:20]])  # Limit to 20 tweets
        
        prompt = f"""
Analyze the social sentiment for token ${token_symbol} based on these recent tweets:

{tweets_text}

Provide:
1. Sentiment Score (-100 to +100, where -100 is very bearish, +100 is very bullish)
2. FOMO Level (Low/Medium/High)
3. Key Themes (list of main topics discussed)
4. Potential Concerns (if any)
5. Overall Market Mood (one sentence)

Format as JSON.
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a crypto social sentiment analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=800
            )
            
            sentiment_text = response.choices[0].message.content
            sentiment = json.loads(sentiment_text)
            
            return sentiment
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "sentiment_score": 0,
                "fomo_level": "Unknown",
                "key_themes": [],
                "concerns": [str(e)],
                "market_mood": "Unable to analyze"
            }
    
    async def generate_trading_tip(self, market_conditions: Dict) -> str:
        """Generate a helpful trading tip based on current market conditions"""
        
        prompt = f"""
Current Market Conditions:
- Overall Trend: {market_conditions.get('trend', 'Unknown')}
- Volatility: {market_conditions.get('volatility', 'Unknown')}
- Top Performers: {market_conditions.get('top_gainers', [])}
- Recent Rugs: {market_conditions.get('recent_rugs', 0)} in last 24h

Generate a concise, actionable trading tip (2-3 sentences) for Solana trenchers.
Focus on risk management and current market dynamics.
Keep it real and helpful - no hype, just facts.
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a pragmatic trading advisor for crypto traders."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            tip = response.choices[0].message.content.strip()
            return tip
            
        except Exception as e:
            logger.error(f"Error generating tip: {e}")
            return "Market conditions are volatile. Always DYOR and never invest more than you can afford to lose."
    
    async def detect_rug_patterns(self, transaction_history: List[Dict]) -> Dict:
        """Detect potential rug pull patterns in transaction history"""
        
        patterns = {
            "is_suspicious": False,
            "risk_level": "LOW",
            "detected_patterns": [],
            "confidence": 0.0
        }
        
        try:
            # Check for common rug patterns:
            # 1. Large dev wallet sells
            # 2. Rapid liquidity removal
            # 3. Suspicious contract interactions
            # 4. Honeypot characteristics
            
            dev_sells = [tx for tx in transaction_history if tx.get('type') == 'dev_sell']
            lp_removes = [tx for tx in transaction_history if tx.get('type') == 'lp_remove']
            
            if len(dev_sells) > 3:
                patterns["detected_patterns"].append("Multiple dev wallet sells detected")
                patterns["risk_level"] = "MEDIUM"
            
            if len(lp_removes) > 0:
                total_removed = sum(tx.get('amount', 0) for tx in lp_removes)
                if total_removed > 50:  # More than 50% LP removed
                    patterns["detected_patterns"].append("Significant liquidity removal")
                    patterns["risk_level"] = "HIGH"
                    patterns["is_suspicious"] = True
            
            # Calculate confidence based on detected patterns
            patterns["confidence"] = min(len(patterns["detected_patterns"]) * 0.3, 1.0)
            
        except Exception as e:
            logger.error(f"Error detecting rug patterns: {e}")
        
        return patterns
    
    async def summarize_market_day(self, daily_data: Dict) -> str:
        """Generate a summary of the day's market activity"""
        
        prompt = f"""
Summarize today's Solana trading activity for trenchers:

Key Stats:
- New Token Launches: {daily_data.get('new_tokens', 0)}
- Total Volume: ${daily_data.get('volume_usd', 0):,.0f}
- Biggest Gainer: {daily_data.get('biggest_gainer', 'N/A')} (+{daily_data.get('biggest_gain_pct', 0)}%)
- Confirmed Rugs: {daily_data.get('rugs', 0)}
- Successful Alerts: {daily_data.get('successful_alerts', 0)}

Write a brief, engaging summary (3-4 sentences) for a Twitter post.
Include key takeaways and lessons learned.
Use emojis appropriately.
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a crypto market analyst writing for Twitter."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Another day in the trenches! {daily_data.get('new_tokens', 0)} new tokens launched. Stay vigilant! 🛡️"
