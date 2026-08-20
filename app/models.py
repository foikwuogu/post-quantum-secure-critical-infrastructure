from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Asset(Base):
    __tablename__ = "assets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_name: Mapped[str] = mapped_column(String(120), unique=True)
    sector: Mapped[str] = mapped_column(String(60))
    zone: Mapped[str] = mapped_column(String(30))
    current_algorithm: Mapped[str] = mapped_column(String(80))
    key_exchange: Mapped[str] = mapped_column(String(80))
    signature_algorithm: Mapped[str] = mapped_column(String(80))
    data_classification: Mapped[str] = mapped_column(String(40))
    secrecy_years: Mapped[int] = mapped_column(Integer)
    migration_months: Mapped[int] = mapped_column(Integer)
    criticality: Mapped[int] = mapped_column(Integer)
    readiness_score: Mapped[float] = mapped_column(Float, default=0)
    quantum_risk_score: Mapped[float] = mapped_column(Float, default=0)

class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    mode: Mapped[str] = mapped_column(String(20))
    operation: Mapped[str] = mapped_column(String(60))
    iterations: Mapped[int] = mapped_column(Integer)
    mean_ms: Mapped[float] = mapped_column(Float)
    min_ms: Mapped[float] = mapped_column(Float)
    max_ms: Mapped[float] = mapped_column(Float)
    output_bytes: Mapped[int] = mapped_column(Integer)
