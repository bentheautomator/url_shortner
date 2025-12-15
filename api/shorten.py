"""POST /api/shorten - Create shortened URL"""
import json
import secrets
import string
from http.server import BaseHTTPRequestHandler
from api._db import get_db, URL, APIKey, BASE_URL, json_response, init_db

init_db()


def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body) if body else {}

            url = data.get('url', '').strip()
            custom_code = data.get('custom_code')

            if not url:
                self.send_json({"detail": "URL is required"}, 400)
                return

            # Add https if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            db = next(get_db())

            # Get API key if provided
            api_key_header = self.headers.get('X-API-Key')
            api_key = None
            if api_key_header:
                api_key = db.query(APIKey).filter(
                    APIKey.key == api_key_header,
                    APIKey.is_active == True
                ).first()

            # Handle custom code
            if custom_code:
                existing = db.query(URL).filter(URL.short_code == custom_code).first()
                if existing:
                    self.send_json({"detail": "Custom code already taken"}, 400)
                    return
                short_code = custom_code
            else:
                while True:
                    short_code = generate_short_code()
                    if not db.query(URL).filter(URL.short_code == short_code).first():
                        break

            # Create URL
            db_url = URL(
                original_url=url,
                short_code=short_code,
                api_key_id=api_key.id if api_key else None
            )
            db.add(db_url)
            db.commit()
            db.refresh(db_url)

            self.send_json({
                "id": db_url.id,
                "original_url": db_url.original_url,
                "short_code": db_url.short_code,
                "created_at": db_url.created_at.isoformat(),
                "click_count": 0,
                "short_url": f"{BASE_URL}/{db_url.short_code}"
            })

        except Exception as e:
            self.send_json({"detail": str(e)}, 500)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
