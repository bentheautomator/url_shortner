from fastapi import FastAPI, Depends, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict
import secrets
import string
import qrcode
import io
import base64

from .database import engine, get_db, Base
from .models import URL, Click, APIKey
from .schemas import (
    URLCreate, URLResponse, URLStatsResponse,
    APIKeyCreate, APIKeyResponse, QRCodeResponse
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="A badass URL shortener with analytics, custom codes, and QR generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_URL = "http://localhost:8000"


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def get_api_key(
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[APIKey]:
    if x_api_key is None:
        return None
    api_key = db.query(APIKey).filter(
        APIKey.key == x_api_key,
        APIKey.is_active == True
    ).first()
    return api_key


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# URL Shortening
@app.post("/api/shorten", response_model=URLResponse)
async def shorten_url(
    url_data: URLCreate,
    request: Request,
    db: Session = Depends(get_db),
    api_key: Optional[APIKey] = Depends(get_api_key)
):
    # Check if custom code is taken
    if url_data.custom_code:
        existing = db.query(URL).filter(URL.short_code == url_data.custom_code).first()
        if existing:
            raise HTTPException(status_code=400, detail="Custom code already taken")
        short_code = url_data.custom_code
    else:
        # Generate unique short code
        while True:
            short_code = generate_short_code()
            existing = db.query(URL).filter(URL.short_code == short_code).first()
            if not existing:
                break

    # Create URL entry
    db_url = URL(
        original_url=url_data.url,
        short_code=short_code,
        api_key_id=api_key.id if api_key else None
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    response = URLResponse(
        id=db_url.id,
        original_url=db_url.original_url,
        short_code=db_url.short_code,
        created_at=db_url.created_at,
        click_count=0,
        short_url=f"{BASE_URL}/{db_url.short_code}"
    )
    return response


# Redirect
@app.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    # Skip API routes
    if short_code in ["api", "health", "docs", "openapi.json", "redoc"]:
        raise HTTPException(status_code=404, detail="Not found")

    url = db.query(URL).filter(URL.short_code == short_code).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Record click
    click = Click(
        url_id=url.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer")
    )
    db.add(click)
    db.commit()

    return RedirectResponse(url=url.original_url, status_code=307)


# Get URL stats
@app.get("/api/urls/{short_code}", response_model=URLStatsResponse)
async def get_url_stats(
    short_code: str,
    db: Session = Depends(get_db)
):
    url = db.query(URL).filter(URL.short_code == short_code).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Get clicks by day (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    clicks = db.query(Click).filter(
        Click.url_id == url.id,
        Click.clicked_at >= thirty_days_ago
    ).all()

    clicks_by_day = defaultdict(int)
    for click in clicks:
        day = click.clicked_at.strftime("%Y-%m-%d")
        clicks_by_day[day] += 1

    # Get top referers
    referer_counts = defaultdict(int)
    for click in url.clicks:
        ref = click.referer or "Direct"
        referer_counts[ref] += 1

    top_referers = [
        {"referer": ref, "count": count}
        for ref, count in sorted(referer_counts.items(), key=lambda x: -x[1])[:5]
    ]

    return URLStatsResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        created_at=url.created_at,
        click_count=url.click_count,
        clicks=[],  # Simplified for now
        clicks_by_day=dict(clicks_by_day),
        top_referers=top_referers
    )


# List all URLs (for API key holder)
@app.get("/api/urls", response_model=list[URLResponse])
async def list_urls(
    db: Session = Depends(get_db),
    api_key: Optional[APIKey] = Depends(get_api_key),
    limit: int = 50,
    offset: int = 0
):
    query = db.query(URL)
    if api_key:
        query = query.filter(URL.api_key_id == api_key.id)

    urls = query.order_by(URL.created_at.desc()).offset(offset).limit(limit).all()

    return [
        URLResponse(
            id=url.id,
            original_url=url.original_url,
            short_code=url.short_code,
            created_at=url.created_at,
            click_count=url.click_count,
            short_url=f"{BASE_URL}/{url.short_code}"
        )
        for url in urls
    ]


# Delete URL
@app.delete("/api/urls/{short_code}")
async def delete_url(
    short_code: str,
    db: Session = Depends(get_db),
    api_key: Optional[APIKey] = Depends(get_api_key)
):
    url = db.query(URL).filter(URL.short_code == short_code).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Only allow deletion if owned by API key or no API key required
    if api_key and url.api_key_id != api_key.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this URL")

    db.delete(url)
    db.commit()
    return {"message": "URL deleted successfully"}


# Generate QR Code
@app.get("/api/urls/{short_code}/qr", response_model=QRCodeResponse)
async def generate_qr_code(
    short_code: str,
    db: Session = Depends(get_db)
):
    url = db.query(URL).filter(URL.short_code == short_code).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    short_url = f"{BASE_URL}/{url.short_code}"

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(short_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return QRCodeResponse(qr_code=f"data:image/png;base64,{qr_base64}")


# API Key Management
@app.post("/api/keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    db: Session = Depends(get_db)
):
    api_key = APIKey(name=key_data.name)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key


@app.get("/api/keys", response_model=list[APIKeyResponse])
async def list_api_keys(db: Session = Depends(get_db)):
    return db.query(APIKey).filter(APIKey.is_active == True).all()


@app.delete("/api/keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db)
):
    api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key.is_active = False
    db.commit()
    return {"message": "API key revoked"}


# Global stats
@app.get("/api/stats")
async def get_global_stats(db: Session = Depends(get_db)):
    total_urls = db.query(func.count(URL.id)).scalar()
    total_clicks = db.query(func.count(Click.id)).scalar()

    # URLs created today
    today = datetime.utcnow().date()
    urls_today = db.query(func.count(URL.id)).filter(
        func.date(URL.created_at) == today
    ).scalar()

    # Clicks today
    clicks_today = db.query(func.count(Click.id)).filter(
        func.date(Click.clicked_at) == today
    ).scalar()

    return {
        "total_urls": total_urls,
        "total_clicks": total_clicks,
        "urls_today": urls_today,
        "clicks_today": clicks_today
    }
