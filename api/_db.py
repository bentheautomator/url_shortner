"""
Shared database module for Vercel serverless functions.
Uses Neon Postgres via DATABASE_URL environment variable.
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import secrets

# Get database URL from environment (Neon Postgres)
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Handle Neon's postgres:// vs postgresql:// URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL) if DATABASE_URL else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None
Base = declarative_base()

# Base URL for generated short links
BASE_URL = os.environ.get("SHRTNR_BASE_URL", "https://your-app.vercel.app")


class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: secrets.token_urlsafe(32))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    urls = relationship("URL", back_populates="api_key")


class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True)
    api_key = relationship("APIKey", back_populates="urls")
    clicks = relationship("Click", back_populates="url", cascade="all, delete-orphan")

    @property
    def click_count(self):
        return len(self.clicks)


class Click(Base):
    __tablename__ = "clicks"
    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    clicked_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    referer = Column(String, nullable=True)
    country = Column(String, nullable=True)
    url = relationship("URL", back_populates="clicks")


def get_db():
    """Get database session."""
    if not SessionLocal:
        raise Exception("Database not configured. Set DATABASE_URL environment variable.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    if engine:
        Base.metadata.create_all(bind=engine)


def json_response(data, status=200):
    """Create JSON response for Vercel."""
    import json
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-API-Key"
        },
        "body": json.dumps(data, default=str)
    }


def html_response(html, status=200):
    """Create HTML response for Vercel."""
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "text/html",
            "Access-Control-Allow-Origin": "*"
        },
        "body": html
    }


def redirect_response(url, status=307):
    """Create redirect response for Vercel."""
    return {
        "statusCode": status,
        "headers": {
            "Location": url,
            "Access-Control-Allow-Origin": "*"
        }
    }
