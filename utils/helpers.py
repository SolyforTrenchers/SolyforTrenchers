"""
Utility Functions - Helper functions used throughout the application
"""

import hashlib
import base58
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import re


def is_valid_solana_address(address: str) -> bool:
    """Validate a Solana wallet/token address"""
    try:
        decoded = base58.b58decode(address)
        return len(decoded) == 32
    except Exception:
        return False


def shorten_address(address: str, chars: int = 4) -> str:
    """Shorten a Solana address for display"""
    if len(address) <= chars * 2:
        return address
    return f"{address[:chars]}...{address[-chars:]}"


def calculate_risk_score(factors: Dict) -> float:
    """
    Calculate risk score (0-100) based on various factors
    Higher score = higher risk
    """
    score = 0.0
    
    # Mint authority not renounced: +30
    if not factors.get('mint_authority_revoked', False):
        score += 30.0
    
    # Freeze authority not renounced: +20
    if not factors.get('freeze_authority_revoked', False):
        score += 20.0
    
    # Low holder count: +15
    holder_count = factors.get('holder_count', 0)
    if holder_count < 50:
        score += 15.0
    elif holder_count < 100:
        score += 10.0
    
    # High concentration in top 10: +20
    top_10_pct = factors.get('top_10_holdings_pct', 0)
    if top_10_pct > 80:
        score += 20.0
    elif top_10_pct > 60:
        score += 15.0
    elif top_10_pct > 40:
        score += 10.0
    
    # High dev holdings: +15
    dev_holdings_pct = factors.get('dev_holdings_pct', 0)
    if dev_holdings_pct > 20:
        score += 15.0
    elif dev_holdings_pct > 10:
        score += 10.0
    
    # No liquidity lock: +20
    if not factors.get('liquidity_locked', False):
        score += 20.0
    
    # Low liquidity: +10
    liquidity_usd = factors.get('liquidity_usd', 0)
    if liquidity_usd < 5000:
        score += 10.0
    
    # Cap at 100
    return min(score, 100.0)


def format_large_number(num: float, decimals: int = 2) -> str:
    """Format large numbers with K, M, B suffixes"""
    if num >= 1_000_000_000:
        return f"${num/1_000_000_000:.{decimals}f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.{decimals}f}M"
    elif num >= 1_000:
        return f"${num/1_000:.{decimals}f}K"
    else:
        return f"${num:.{decimals}f}"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def extract_twitter_handle(text: str) -> Optional[str]:
    """Extract Twitter handle from text"""
    match = re.search(r'@(\w{1,15})', text)
    return match.group(1) if match else None


def extract_solana_address(text: str) -> Optional[str]:
    """Extract Solana address from text"""
    # Solana addresses are base58 encoded, 32-44 characters
    pattern = r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'
    match = re.search(pattern, text)
    
    if match:
        potential_address = match.group(0)
        if is_valid_solana_address(potential_address):
            return potential_address
    
    return None


def time_ago(dt: datetime) -> str:
    """Convert datetime to human-readable 'time ago' format"""
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)}s ago"
    elif seconds < 3600:
        return f"{int(seconds/60)}m ago"
    elif seconds < 86400:
        return f"{int(seconds/3600)}h ago"
    else:
        return f"{int(seconds/86400)}d ago"


def sanitize_text_for_tweet(text: str, max_length: int = 280) -> str:
    """Sanitize and truncate text for Twitter"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    return text


def generate_alert_id(token_address: str, alert_type: str) -> str:
    """Generate a unique alert ID"""
    data = f"{token_address}:{alert_type}:{datetime.utcnow().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def calculate_liquidity_health(liquidity_usd: float, volume_24h_usd: float) -> str:
    """Calculate liquidity health rating"""
    if volume_24h_usd == 0:
        return "Unknown"
    
    ratio = liquidity_usd / volume_24h_usd
    
    if ratio >= 2.0:
        return "Excellent"
    elif ratio >= 1.0:
        return "Good"
    elif ratio >= 0.5:
        return "Fair"
    else:
        return "Poor"


def get_risk_emoji(risk_score: float) -> str:
    """Get emoji based on risk score"""
    if risk_score < 30:
        return "🟢"  # Low risk
    elif risk_score < 70:
        return "🟡"  # Medium risk
    else:
        return "🔴"  # High risk


def get_trend_emoji(percentage_change: float) -> str:
    """Get emoji based on price trend"""
    if percentage_change > 10:
        return "📈🚀"
    elif percentage_change > 0:
        return "📈"
    elif percentage_change > -10:
        return "📉"
    else:
        return "📉💥"


def batch_list(items: List, batch_size: int) -> List[List]:
    """Split a list into batches"""
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def is_weekend() -> bool:
    """Check if current day is weekend"""
    return datetime.utcnow().weekday() >= 5


def get_market_hours_status() -> str:
    """Get current market activity status"""
    hour = datetime.utcnow().hour
    
    # Crypto markets are 24/7, but activity varies
    if 13 <= hour <= 21:  # 1 PM - 9 PM UTC (peak US hours)
        return "peak"
    elif 0 <= hour <= 8:  # Midnight - 8 AM UTC (Asian hours)
        return "asian"
    else:
        return "normal"
