"""GET/POST /api/keys - API key management"""
import json
from http.server import BaseHTTPRequestHandler
from api._db import get_db, APIKey, init_db

init_db()


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        try:
            db = next(get_db())
            keys = db.query(APIKey).filter(APIKey.is_active == True).all()

            results = [{
                "id": key.id,
                "key": key.key,
                "name": key.name,
                "created_at": key.created_at.isoformat(),
                "is_active": key.is_active
            } for key in keys]

            self.send_json(results)

        except Exception as e:
            self.send_json({"detail": str(e)}, 500)

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body) if body else {}

            name = data.get('name', '').strip()
            if not name:
                self.send_json({"detail": "Name is required"}, 400)
                return

            db = next(get_db())
            api_key = APIKey(name=name)
            db.add(api_key)
            db.commit()
            db.refresh(api_key)

            self.send_json({
                "id": api_key.id,
                "key": api_key.key,
                "name": api_key.name,
                "created_at": api_key.created_at.isoformat(),
                "is_active": api_key.is_active
            })

        except Exception as e:
            self.send_json({"detail": str(e)}, 500)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
