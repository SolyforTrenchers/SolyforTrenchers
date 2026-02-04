"""
Database Models - SQLAlchemy ORM models for data persistence
Stores token data, alerts, user preferences, and analytics
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Token(Base):
    """Token information and tracking"""
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    mint_address = Column(String(44), unique=True, nullable=False, index=True)
    name = Column(String(100))
    symbol = Column(String(20))
    decimals = Column(Integer)
    total_supply = Column(Float)
    
    # Creator info
    creator_address = Column(String(44), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Market data
    current_price_usd = Column(Float, default=0.0)
    market_cap_usd = Column(Float, default=0.0)
    liquidity_usd = Column(Float, default=0.0)
    volume_24h_usd = Column(Float, default=0.0)
    
    # Risk assessment
    risk_score = Column(Float, default=0.0)
    is_honeypot = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_suspicious = Column(Boolean, default=False)
    
    # Metadata
    description = Column(Text)
    website = Column(String(255))
    twitter = Column(String(255))
    telegram = Column(String(255))
    
    # Relationships
    alerts = relationship("Alert", back_populates="token")
    price_history = relationship("PriceHistory", back_populates="token")
    holder_snapshots = relationship("HolderSnapshot", back_populates="token")
    
    # Timestamps
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Token {self.symbol} ({self.mint_address[:8]}...)>"


class Alert(Base):
    """Trading alerts and notifications"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    
    alert_type = Column(String(50), nullable=False)  # 'launch', 'rug', 'whale', 'price'
    severity = Column(String(20))  # 'low', 'medium', 'high', 'critical'
    title = Column(String(200))
    message = Column(Text)
    
    # Alert metadata
    data = Column(JSON)  # Additional structured data
    
    # Status
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    is_resolved = Column(Boolean, default=False)
    
    # Social media
    tweet_id = Column(String(50))
    retweets = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    token = relationship("Token", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert {self.alert_type} - {self.title}>"


class User(Base):
    """User accounts and preferences"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    twitter_username = Column(String(50), unique=True, index=True)
    twitter_id = Column(String(50), unique=True)
    
    # Preferences
    alert_preferences = Column(JSON)  # Custom alert settings
    watchlist = Column(JSON)  # List of tokens being watched
    risk_tolerance = Column(String(20), default="medium")  # 'low', 'medium', 'high'
    
    # Subscription
    is_premium = Column(Boolean, default=False)
    subscription_expires = Column(DateTime)
    
    # Analytics
    total_alerts_received = Column(Integer, default=0)
    successful_trades = Column(Integer, default=0)
    failed_trades = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user")
    
    def __repr__(self):
        return f"<User @{self.twitter_username}>"


class Portfolio(Base):
    """User portfolio tracking"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    wallet_address = Column(String(44), index=True)
    
    # Holdings
    holdings = Column(JSON)  # List of tokens and amounts
    total_value_usd = Column(Float, default=0.0)
    
    # Performance
    initial_investment_usd = Column(Float, default=0.0)
    profit_loss_usd = Column(Float, default=0.0)
    profit_loss_pct = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    
    def __repr__(self):
        return f"<Portfolio {self.wallet_address[:8]}... - ${self.total_value_usd:,.2f}>"


class PriceHistory(Base):
    """Historical price data for tokens"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    
    price_usd = Column(Float, nullable=False)
    volume_usd = Column(Float, default=0.0)
    liquidity_usd = Column(Float, default=0.0)
    market_cap_usd = Column(Float, default=0.0)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    token = relationship("Token", back_populates="price_history")
    
    def __repr__(self):
        return f"<PriceHistory ${self.price_usd} at {self.timestamp}>"


class HolderSnapshot(Base):
    """Token holder distribution snapshots"""
    __tablename__ = "holder_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    
    total_holders = Column(Integer, default=0)
    top_10_holdings_pct = Column(Float, default=0.0)
    dev_holdings_pct = Column(Float, default=0.0)
    
    # Distribution data
    holder_distribution = Column(JSON)  # Full holder list if needed
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    token = relationship("Token", back_populates="holder_snapshots")
    
    def __repr__(self):
        return f"<HolderSnapshot {self.total_holders} holders>"


class MarketStats(Base):
    """Daily market statistics and metrics"""
    __tablename__ = "market_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)
    
    # Token stats
    new_tokens_launched = Column(Integer, default=0)
    active_tokens = Column(Integer, default=0)
    rugged_tokens = Column(Integer, default=0)
    
    # Trading stats
    total_volume_usd = Column(Float, default=0.0)
    total_liquidity_usd = Column(Float, default=0.0)
    unique_traders = Column(Integer, default=0)
    
    # Performance
    biggest_gainer_symbol = Column(String(20))
    biggest_gainer_pct = Column(Float, default=0.0)
    biggest_loser_symbol = Column(String(20))
    biggest_loser_pct = Column(Float, default=0.0)
    
    # Soly stats
    alerts_sent = Column(Integer, default=0)
    successful_alerts = Column(Integer, default=0)
    false_positives = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<MarketStats {self.date.date()}>"
