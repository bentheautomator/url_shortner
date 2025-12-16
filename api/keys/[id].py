"""DELETE /api/keys/:id - Revoke API key"""
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from api._db import get_db, APIKey, init_db

init_db()


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-HTTP-Method-Override')
        self.end_headers()

    def do_POST(self):
        """Handle POST with method override for DELETE (Vercel workaround)"""
        method_override = self.headers.get('X-HTTP-Method-Override', '').upper()
        if method_override == 'DELETE':
            return self.do_DELETE()
        self.send_json({"detail": "Use DELETE or X-HTTP-Method-Override: DELETE"}, 405)

    def do_DELETE(self):
        try:
            # Extract key ID from path like /api/keys/123
            parsed = urlparse(self.path)
            parts = parsed.path.strip('/').split('/')
            key_id = int(parts[2]) if len(parts) >= 3 else None

            if not key_id:
                self.send_json({"detail": "Key ID required"}, 400)
                return

            db = next(get_db())
            api_key = db.query(APIKey).filter(APIKey.id == key_id).first()

            if not api_key:
                self.send_json({"detail": "API key not found"}, 404)
                return

            api_key.is_active = False
            db.commit()

            self.send_json({"message": "API key revoked"})

        except Exception as e:
            self.send_json({"detail": str(e)}, 500)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
