"""GET /api/urls - List URLs"""
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from api._db import get_db, URL, APIKey, BASE_URL, init_db

init_db()


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        self.end_headers()

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            limit = int(query.get('limit', [50])[0])
            offset = int(query.get('offset', [0])[0])

            db = next(get_db())

            # Get API key if provided
            api_key_header = self.headers.get('X-API-Key')
            api_key = None
            if api_key_header:
                api_key = db.query(APIKey).filter(
                    APIKey.key == api_key_header,
                    APIKey.is_active == True
                ).first()

            query_obj = db.query(URL)
            if api_key:
                query_obj = query_obj.filter(URL.api_key_id == api_key.id)

            urls = query_obj.order_by(URL.created_at.desc()).offset(offset).limit(limit).all()

            results = [{
                "id": url.id,
                "original_url": url.original_url,
                "short_code": url.short_code,
                "created_at": url.created_at.isoformat(),
                "click_count": url.click_count,
                "short_url": f"{BASE_URL}/{url.short_code}"
            } for url in urls]

            self.send_json(results)

        except Exception as e:
            self.send_json({"detail": str(e)}, 500)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
