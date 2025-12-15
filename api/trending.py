"""GET /api/trending - Trending URLs"""
import json
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from api._db import get_db, URL, Click, BASE_URL, init_db

init_db()


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()

    def do_GET(self):
        try:
            db = next(get_db())

            seven_days_ago = datetime.utcnow() - timedelta(days=7)

            trending_query = (
                db.query(URL, func.count(Click.id).label('recent_clicks'))
                .join(Click, Click.url_id == URL.id)
                .filter(Click.clicked_at >= seven_days_ago)
                .group_by(URL.id)
                .order_by(desc('recent_clicks'))
                .limit(10)
            )

            results = []
            for url, recent_clicks in trending_query:
                results.append({
                    "id": url.id,
                    "original_url": url.original_url[:50] + "..." if len(url.original_url) > 50 else url.original_url,
                    "short_code": url.short_code,
                    "created_at": url.created_at.isoformat(),
                    "click_count": url.click_count,
                    "short_url": f"{BASE_URL}/{url.short_code}"
                })

            self.send_json(results)

        except Exception as e:
            self.send_json({"detail": str(e)}, 500)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
