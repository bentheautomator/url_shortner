"""GET/DELETE /api/urls/:code - URL stats and deletion"""
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime, timedelta
from collections import defaultdict
from api._db import get_db, URL, Click, APIKey, BASE_URL, init_db

init_db()


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        self.end_headers()

    def get_code(self):
        """Extract short code from path like /api/urls/abc123"""
        parsed = urlparse(self.path)
        parts = parsed.path.strip('/').split('/')
        # Path is like: api/urls/CODE or api/urls/CODE/qr
        if len(parts) >= 3:
            return parts[2]
        return None

    def do_GET(self):
        try:
            short_code = self.get_code()
            if not short_code:
                self.send_json({"detail": "Short code required"}, 400)
                return

            db = next(get_db())
            url = db.query(URL).filter(URL.short_code == short_code).first()

            if not url:
                self.send_json({"detail": "URL not found"}, 404)
                return

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

            self.send_json({
                "id": url.id,
                "original_url": url.original_url,
                "short_code": url.short_code,
                "created_at": url.created_at.isoformat(),
                "click_count": url.click_count,
                "clicks": [],
                "clicks_by_day": dict(clicks_by_day),
                "top_referers": top_referers
            })

        except Exception as e:
            self.send_json({"detail": str(e)}, 500)

    def do_DELETE(self):
        try:
            short_code = self.get_code()
            if not short_code:
                self.send_json({"detail": "Short code required"}, 400)
                return

            db = next(get_db())
            url = db.query(URL).filter(URL.short_code == short_code).first()

            if not url:
                self.send_json({"detail": "URL not found"}, 404)
                return

            # Check API key authorization
            api_key_header = self.headers.get('X-API-Key')
            if api_key_header:
                api_key = db.query(APIKey).filter(
                    APIKey.key == api_key_header,
                    APIKey.is_active == True
                ).first()
                if api_key and url.api_key_id != api_key.id:
                    self.send_json({"detail": "Not authorized"}, 403)
                    return

            db.delete(url)
            db.commit()
            self.send_json({"message": "URL deleted successfully"})

        except Exception as e:
            self.send_json({"detail": str(e)}, 500)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
