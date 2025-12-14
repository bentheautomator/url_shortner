from fastapi import FastAPI, Depends, HTTPException, Request, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
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


# Viral Interstitial HTML
INTERSTITIAL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redirecting... | SHRTNR</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0a0f 0%, #0f1419 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #f8fafc;
        }
        .container {
            text-align: center;
            padding: 2rem;
        }
        .logo {
            font-size: 2rem;
            font-weight: bold;
            background: linear-gradient(90deg, #0ea5e9, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        .message {
            color: #94a3b8;
            margin-bottom: 2rem;
        }
        .loader {
            width: 40px;
            height: 40px;
            border: 3px solid #1e293b;
            border-top: 3px solid #0ea5e9;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 2rem;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .cta {
            background: rgba(14, 165, 233, 0.1);
            border: 1px solid rgba(14, 165, 233, 0.3);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            display: inline-block;
        }
        .cta a {
            color: #0ea5e9;
            text-decoration: none;
            font-weight: 500;
        }
        .cta a:hover {
            text-decoration: underline;
        }
        .skip {
            margin-top: 1rem;
            font-size: 0.875rem;
            color: #64748b;
        }
        .skip a {
            color: #94a3b8;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">SHRTNR</div>
        <div class="loader"></div>
        <p class="message">Redirecting you to your destination...</p>
        <div class="cta">
            <a href="/" target="_blank">Create your own short link in 5 seconds →</a>
        </div>
        <p class="skip"><a href="{destination}" id="skip">Skip waiting</a></p>
    </div>
    <script>
        setTimeout(function() {{
            window.location.href = "{destination}";
        }}, 1500);
    </script>
</body>
</html>
"""


# Redirect
@app.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db),
    direct: bool = Query(False, description="Skip interstitial")
):
    # Skip API routes
    if short_code in ["api", "health", "docs", "openapi.json", "redoc", "trending"]:
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

    # Direct redirect for API calls or returning visitors
    if direct or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return RedirectResponse(url=url.original_url, status_code=307)

    # Show interstitial for first-time web visitors
    html = INTERSTITIAL_HTML.replace("{destination}", url.original_url)
    return HTMLResponse(content=html)


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


# Trending URLs (most clicked in last 7 days)
@app.get("/api/trending", response_model=list[URLResponse])
async def get_trending_urls(
    db: Session = Depends(get_db),
    limit: int = 10
):
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    # Get URLs with most clicks in last 7 days
    trending_query = (
        db.query(URL, func.count(Click.id).label('recent_clicks'))
        .join(Click, Click.url_id == URL.id)
        .filter(Click.clicked_at >= seven_days_ago)
        .group_by(URL.id)
        .order_by(desc('recent_clicks'))
        .limit(limit)
    )

    results = []
    for url, recent_clicks in trending_query:
        results.append(URLResponse(
            id=url.id,
            original_url=url.original_url[:50] + "..." if len(url.original_url) > 50 else url.original_url,
            short_code=url.short_code,
            created_at=url.created_at,
            click_count=url.click_count,
            short_url=f"{BASE_URL}/{url.short_code}"
        ))

    return results
