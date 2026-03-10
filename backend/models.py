import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime,
    ForeignKey, JSON
)
from sqlalchemy.orm import relationship

from database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Thesis(Base):
    __tablename__ = "theses"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=False)
    summary = Column(String, default="")
    description = Column(Text, nullable=False)
    time_horizon = Column(String, nullable=False)
    tags = Column(JSON, default=list)
    is_archived = Column(Boolean, default=False)
    is_collapsed = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # THI fields
    thi_score = Column(Float, default=50.0)
    thi_direction = Column(String, default="neutral")
    thi_trend = Column(String, default="stable")
    evidence_score = Column(Float, default=50.0)
    evidence_weight = Column(Float, default=0.50)
    momentum_score = Column(Float, default=50.0)
    momentum_weight = Column(Float, default=0.30)
    conviction_data_score = Column(Float, default=50.0)
    conviction_data_weight = Column(Float, default=0.20)

    # User conviction
    user_conviction_score = Column(Integer, default=5)
    user_conviction_note = Column(Text, nullable=True)
    user_conviction_updated_at = Column(DateTime, default=datetime.utcnow)

    effects = relationship("Effect", back_populates="thesis", cascade="all, delete-orphan")
    equity_bets = relationship("EquityBet", back_populates="thesis", cascade="all, delete-orphan",
                               foreign_keys="EquityBet.thesis_id")
    startup_opportunities = relationship("StartupOpportunity", back_populates="thesis",
                                         cascade="all, delete-orphan", foreign_keys="StartupOpportunity.thesis_id")
    feeds = relationship("DataFeed", back_populates="thesis", cascade="all, delete-orphan")
    indicators = relationship("Indicator", back_populates="thesis", cascade="all, delete-orphan")
    thi_history = relationship("THISnapshot", back_populates="thesis", cascade="all, delete-orphan")
    conviction_history = relationship("ConvictionSnapshot", back_populates="thesis",
                                       cascade="all, delete-orphan", foreign_keys="ConvictionSnapshot.thesis_id")


class Effect(Base):
    __tablename__ = "effects"

    id = Column(String, primary_key=True, default=generate_uuid)
    thesis_id = Column(String, ForeignKey("theses.id"), nullable=False)
    parent_effect_id = Column(String, ForeignKey("effects.id"), nullable=True)
    order = Column(Integer, default=2)  # 2 or 3
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    inheritance_weight = Column(Float, default=0.40)
    display_order = Column(Integer, default=0)
    is_collapsed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # THI fields
    thi_score = Column(Float, default=50.0)
    thi_direction = Column(String, default="neutral")
    thi_trend = Column(String, default="stable")

    # User conviction
    user_conviction_score = Column(Integer, default=5)
    user_conviction_note = Column(Text, nullable=True)
    user_conviction_updated_at = Column(DateTime, default=datetime.utcnow)

    thesis = relationship("Thesis", back_populates="effects")
    parent_effect = relationship("Effect", remote_side=[id], backref="child_effects")
    equity_bets = relationship("EquityBet", back_populates="effect", cascade="all, delete-orphan",
                               foreign_keys="EquityBet.effect_id")
    startup_opportunities = relationship("StartupOpportunity", back_populates="effect",
                                         cascade="all, delete-orphan", foreign_keys="StartupOpportunity.effect_id")
    feeds = relationship("DataFeed", backref="effect", cascade="all, delete-orphan",
                          foreign_keys="DataFeed.effect_id")
    indicators = relationship("Indicator", back_populates="effect", cascade="all, delete-orphan")
    conviction_history = relationship("ConvictionSnapshot", back_populates="effect",
                                       cascade="all, delete-orphan", foreign_keys="ConvictionSnapshot.effect_id")


class DataFeed(Base):
    __tablename__ = "data_feeds"

    id = Column(String, primary_key=True, default=generate_uuid)
    thesis_id = Column(String, ForeignKey("theses.id"), nullable=True)
    effect_id = Column(String, ForeignKey("effects.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    source = Column(String, nullable=False)  # FRED, ALPHA_VANTAGE, GTRENDS, EDGAR, etc.
    source_type = Column(String, nullable=False)  # flow, structural, adoption, policy
    api_endpoint = Column(String, nullable=True)
    series_id = Column(String, nullable=True)
    keyword = Column(String, nullable=True)
    ticker = Column(String, nullable=True)
    update_frequency = Column(String, default="daily")
    momentum_transform = Column(String, default="rolling_90d_slope")
    status = Column(String, default="live")  # live, stale, offline, degraded
    last_fetched = Column(DateTime, nullable=True)
    raw_value = Column(Float, nullable=True)
    normalized_score = Column(Float, nullable=True)
    confirming_direction = Column(String, default="higher")  # higher or lower
    normalization_method = Column(String, default="percentile_historical")
    weight = Column(Float, default=1.0)

    thesis = relationship("Thesis", back_populates="feeds")
    cached_values = relationship("FeedCache", back_populates="feed", cascade="all, delete-orphan")


class FeedCache(Base):
    __tablename__ = "feed_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feed_id = Column(String, ForeignKey("data_feeds.id"), nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    raw_value = Column(Float, nullable=True)
    raw_data = Column(JSON, nullable=True)
    normalized_score = Column(Float, nullable=True)

    feed = relationship("DataFeed", back_populates="cached_values")


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(String, primary_key=True, default=generate_uuid)
    thesis_id = Column(String, ForeignKey("theses.id"), nullable=True)
    effect_id = Column(String, ForeignKey("effects.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    current_score = Column(Float, default=50.0)
    previous_score = Column(Float, nullable=True)
    direction = Column(String, default="neutral")
    trend = Column(String, default="stable")
    weight = Column(Float, default=1.0)
    last_updated = Column(DateTime, nullable=True)
    feed_ids = Column(JSON, default=list)

    thesis = relationship("Thesis", back_populates="indicators")
    effect = relationship("Effect", back_populates="indicators")


class EquityBet(Base):
    __tablename__ = "equity_bets"

    id = Column(String, primary_key=True, default=generate_uuid)
    thesis_id = Column(String, ForeignKey("theses.id"), nullable=True)
    effect_id = Column(String, ForeignKey("effects.id"), nullable=True)
    ticker = Column(String, nullable=False)
    company_name = Column(String, default="")
    company_description = Column(Text, default="")
    role = Column(String, nullable=False)  # BENEFICIARY, HEADWIND, CANARY
    rationale = Column(Text, nullable=False)
    time_horizon = Column(String, default="1-3yr")
    is_feedback_indicator = Column(Boolean, default=False)
    feedback_weight = Column(Float, default=0.0)
    current_price = Column(Float, nullable=True)
    price_change_12m_pct = Column(Float, nullable=True)
    price_history = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    thesis = relationship("Thesis", back_populates="equity_bets", foreign_keys=[thesis_id])
    effect = relationship("Effect", back_populates="equity_bets", foreign_keys=[effect_id])


class StartupOpportunity(Base):
    __tablename__ = "startup_opportunities"

    id = Column(String, primary_key=True, default=generate_uuid)
    thesis_id = Column(String, ForeignKey("theses.id"), nullable=True)
    effect_id = Column(String, ForeignKey("effects.id"), nullable=True)
    name = Column(String, nullable=False)
    one_liner = Column(Text, nullable=False)
    problem = Column(Text, default="")
    wedge = Column(Text, default="")
    timing = Column(String, default="RIGHT_TIMING")  # TOO_EARLY, RIGHT_TIMING, CROWDING
    timing_rationale = Column(Text, default="")
    time_horizon = Column(String, default="1-3yr")
    created_at = Column(DateTime, default=datetime.utcnow)

    thesis = relationship("Thesis", back_populates="startup_opportunities", foreign_keys=[thesis_id])
    effect = relationship("Effect", back_populates="startup_opportunities", foreign_keys=[effect_id])


class THISnapshot(Base):
    __tablename__ = "thi_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thesis_id = Column(String, ForeignKey("theses.id"), nullable=False)
    score = Column(Float, nullable=False)
    evidence_score = Column(Float, nullable=True)
    momentum_score = Column(Float, nullable=True)
    conviction_score = Column(Float, nullable=True)
    computed_at = Column(DateTime, default=datetime.utcnow)

    thesis = relationship("Thesis", back_populates="thi_history")


class ConvictionSnapshot(Base):
    __tablename__ = "conviction_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thesis_id = Column(String, ForeignKey("theses.id"), nullable=True)
    effect_id = Column(String, ForeignKey("effects.id"), nullable=True)
    score = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    thesis = relationship("Thesis", back_populates="conviction_history", foreign_keys=[thesis_id])
    effect = relationship("Effect", back_populates="conviction_history", foreign_keys=[effect_id])


class MacroHeader(Base):
    __tablename__ = "macro_header"

    id = Column(Integer, primary_key=True, autoincrement=True)
    regime = Column(String, default="NEUTRAL")
    ffr = Column(Float, nullable=True)
    ten_year_two_year_spread = Column(Float, nullable=True)
    vix = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)


class PortfolioPosition(Base):
    __tablename__ = "portfolio_positions"

    id = Column(String, primary_key=True, default=generate_uuid)
    thesis_id = Column(String, ForeignKey("theses.id"), nullable=False)
    ticker = Column(String, nullable=False)
    shares = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    entry_date = Column(DateTime, default=datetime.utcnow)
    is_short = Column(Boolean, default=False)
    current_price = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)
    pnl_pct = Column(Float, nullable=True)
    last_updated = Column(DateTime, nullable=True)
    is_closed = Column(Boolean, default=False)
    closed_at = Column(DateTime, nullable=True)
    close_price = Column(Float, nullable=True)

    thesis = relationship("Thesis", backref="portfolio_positions")


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thesis_id = Column(String, ForeignKey("theses.id"), nullable=False)
    total_value = Column(Float, nullable=False)
    total_pnl = Column(Float, nullable=False)
    total_pnl_pct = Column(Float, nullable=False)
    thi_score = Column(Float, nullable=True)
    computed_at = Column(DateTime, default=datetime.utcnow)

    thesis = relationship("Thesis", backref="portfolio_snapshots")


class EquityFitScore(Base):
    __tablename__ = "equity_fit_scores"

    id = Column(String, primary_key=True, default=generate_uuid)
    equity_bet_id = Column(String, ForeignKey("equity_bets.id"), nullable=False, unique=True)
    thesis_id = Column(String, ForeignKey("theses.id"), nullable=True)
    effect_id = Column(String, ForeignKey("effects.id"), nullable=True)

    revenue_alignment_score = Column(Float, default=50.0)
    thesis_beta_score = Column(Float, default=50.0)
    momentum_alignment_score = Column(Float, default=50.0)
    valuation_buffer_score = Column(Float, default=50.0)
    signal_purity_score = Column(Float, default=50.0)
    efs_score = Column(Float, default=50.0)

    revenue_alignment_pct = Column(Float, nullable=True)
    forward_pe = Column(Float, nullable=True)
    sector_median_pe = Column(Float, nullable=True)
    segment_count = Column(Integer, nullable=True)
    thesis_beta_raw = Column(Float, nullable=True)
    momentum_direction = Column(String, nullable=True)
    stock_return_90d = Column(Float, nullable=True)
    thi_delta_90d = Column(Float, nullable=True)

    last_updated = Column(DateTime, default=datetime.utcnow)
    data_sources_used = Column(JSON, default=list)

    equity_bet = relationship("EquityBet", backref="fit_score")


class StartupTimingScore(Base):
    __tablename__ = "startup_timing_scores"

    id = Column(String, primary_key=True, default=generate_uuid)
    startup_opp_id = Column(String, ForeignKey("startup_opportunities.id"), nullable=False, unique=True)

    thi_alignment_score = Column(Float, default=50.0)
    thi_velocity_score = Column(Float, default=50.0)
    competition_density_score = Column(Float, default=50.0)
    sts_score = Column(Float, default=50.0)

    competitor_count = Column(Integer, nullable=True)
    funded_startups_in_category = Column(Integer, nullable=True)
    total_funding_in_category = Column(Float, nullable=True)
    timing_label = Column(String, default="RIGHT_TIMING")

    last_updated = Column(DateTime, default=datetime.utcnow)

    startup_opportunity = relationship("StartupOpportunity", backref="timing_score")
