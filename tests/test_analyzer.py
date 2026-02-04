"""
Tests for AI Analyzer Module
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from ai.analyzer import TokenAnalyzer


@pytest.fixture
def analyzer():
    """Create a test analyzer instance"""
    return TokenAnalyzer(
        openai_api_key="test_key",
        model="gpt-4-turbo-preview"
    )


@pytest.fixture
def sample_contract_data():
    """Sample contract data for testing"""
    return {
        "total_supply": 1000000000,
        "decimals": 9,
        "mint_authority_revoked": True,
        "freeze_authority_revoked": True
    }


@pytest.fixture
def sample_holder_data():
    """Sample holder data for testing"""
    return {
        "total_holders": 500,
        "top_10_pct": 45.0,
        "dev_holdings_pct": 5.0
    }


@pytest.fixture
def sample_liquidity_data():
    """Sample liquidity data for testing"""
    return {
        "total_usd": 50000.0,
        "locked": True,
        "lock_duration_days": 30
    }


class TestTokenAnalyzer:
    """Test cases for TokenAnalyzer"""
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer.is_ready is True
        assert analyzer.model == "gpt-4-turbo-preview"
        assert analyzer.openai_client is not None
    
    @pytest.mark.asyncio
    async def test_analyze_token_contract_success(
        self, 
        analyzer,
        sample_contract_data,
        sample_holder_data,
        sample_liquidity_data
    ):
        """Test successful token contract analysis"""
        with patch.object(analyzer.openai_client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            # Mock AI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '''{
                "risk_score": 25,
                "red_flags": [],
                "positive_signals": ["Authorities revoked", "Good holder distribution"],
                "recommendation": "BUY",
                "reasoning": "Looks safe"
            }'''
            mock_create.return_value = mock_response
            
            result = await analyzer.analyze_token_contract(
                sample_contract_data,
                sample_holder_data,
                sample_liquidity_data
            )
            
            assert result["risk_score"] == 25
            assert result["recommendation"] == "BUY"
            assert len(result["positive_signals"]) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_token_contract_error_handling(self, analyzer):
        """Test error handling in token analysis"""
        with patch.object(analyzer.openai_client.chat.completions, 'create', side_effect=Exception("API Error")):
            result = await analyzer.analyze_token_contract({}, {}, {})
            
            assert result["risk_score"] == 100
            assert result["recommendation"] == "AVOID"
            assert len(result["red_flags"]) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_social_sentiment(self, analyzer):
        """Test social sentiment analysis"""
        sample_tweets = [
            "This token is going to the moon! 🚀",
            "Great project, solid team",
            "I'm bullish on this one"
        ]
        
        with patch.object(analyzer.openai_client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '''{
                "sentiment_score": 75,
                "fomo_level": "High",
                "key_themes": ["bullish", "moon", "strong team"],
                "concerns": [],
                "market_mood": "Very positive"
            }'''
            mock_create.return_value = mock_response
            
            result = await analyzer.analyze_social_sentiment("TEST", sample_tweets)
            
            assert result["sentiment_score"] == 75
            assert result["fomo_level"] == "High"
            assert len(result["key_themes"]) > 0
    
    @pytest.mark.asyncio
    async def test_generate_trading_tip(self, analyzer):
        """Test trading tip generation"""
        market_conditions = {
            "trend": "bullish",
            "volatility": "high",
            "top_gainers": ["TOKEN1", "TOKEN2"],
            "recent_rugs": 3
        }
        
        with patch.object(analyzer.openai_client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "High volatility means bigger swings. Use tight stop losses and take profits on the way up!"
            mock_create.return_value = mock_response
            
            tip = await analyzer.generate_trading_tip(market_conditions)
            
            assert len(tip) > 0
            assert isinstance(tip, str)
    
    @pytest.mark.asyncio
    async def test_detect_rug_patterns(self, analyzer):
        """Test rug pull pattern detection"""
        transaction_history = [
            {"type": "dev_sell", "amount": 1000},
            {"type": "dev_sell", "amount": 2000},
            {"type": "lp_remove", "amount": 60}
        ]
        
        result = await analyzer.detect_rug_patterns(transaction_history)
        
        assert result["risk_level"] == "HIGH"
        assert result["is_suspicious"] is True
        assert len(result["detected_patterns"]) > 0
    
    @pytest.mark.asyncio
    async def test_detect_rug_patterns_safe_token(self, analyzer):
        """Test rug detection on safe token"""
        transaction_history = [
            {"type": "buy", "amount": 100},
            {"type": "sell", "amount": 50}
        ]
        
        result = await analyzer.detect_rug_patterns(transaction_history)
        
        assert result["risk_level"] == "LOW"
        assert result["is_suspicious"] is False
    
    @pytest.mark.asyncio
    async def test_summarize_market_day(self, analyzer):
        """Test market day summary generation"""
        daily_data = {
            "new_tokens": 25,
            "volume_usd": 5000000,
            "biggest_gainer": "ROCKET",
            "biggest_gain_pct": 250,
            "rugs": 3,
            "successful_alerts": 10
        }
        
        with patch.object(analyzer.openai_client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "📊 Wild day in the trenches! 25 new tokens, $5M volume. ROCKET pumped 250%! 🚀 But watch out - 3 rugs detected. Always DYOR! 🛡️"
            mock_create.return_value = mock_response
            
            summary = await analyzer.summarize_market_day(daily_data)
            
            assert len(summary) > 0
            assert "ROCKET" in summary or "tokens" in summary.lower()


@pytest.mark.asyncio
async def test_analyzer_rate_limiting(analyzer):
    """Test that analyzer respects rate limits"""
    # This would test rate limiting logic if implemented
    pass


@pytest.mark.asyncio
async def test_analyzer_caching(analyzer):
    """Test analysis result caching"""
    # Test that repeated analyses use cache
    pass
