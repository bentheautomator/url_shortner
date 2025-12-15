"""GET /api/urls/:code/qr - Generate QR code"""
import json
import qrcode
import io
import base64
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from api._db import get_db, URL, BASE_URL, init_db

init_db()


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()

    def do_GET(self):
        try:
            # Extract short code from path like /api/urls/abc123/qr
            parsed = urlparse(self.path)
            parts = parsed.path.strip('/').split('/')
            short_code = parts[2] if len(parts) >= 4 else None

            if not short_code:
                self.send_json({"detail": "Short code required"}, 400)
                return

            db = next(get_db())
            url = db.query(URL).filter(URL.short_code == short_code).first()

            if not url:
                self.send_json({"detail": "URL not found"}, 404)
                return

            short_url = f"{BASE_URL}/{url.short_code}"

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(short_url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            qr_base64 = base64.b64encode(buffer.getvalue()).decode()

            self.send_json({"qr_code": f"data:image/png;base64,{qr_base64}"})

        except Exception as e:
            self.send_json({"detail": str(e)}, 500)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
