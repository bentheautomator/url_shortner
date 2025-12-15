"""GET /api/stats - Global statistics"""
import json
from http.server import BaseHTTPRequestHandler
from datetime import datetime
from sqlalchemy import func
from api._db import get_db, URL, Click, init_db

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

            total_urls = db.query(func.count(URL.id)).scalar()
            total_clicks = db.query(func.count(Click.id)).scalar()

            today = datetime.utcnow().date()
            urls_today = db.query(func.count(URL.id)).filter(
                func.date(URL.created_at) == today
            ).scalar()
            clicks_today = db.query(func.count(Click.id)).filter(
                func.date(Click.clicked_at) == today
            ).scalar()

            self.send_json({
                "total_urls": total_urls or 0,
                "total_clicks": total_clicks or 0,
                "urls_today": urls_today or 0,
                "clicks_today": clicks_today or 0
            })

        except Exception as e:
            self.send_json({"detail": str(e)}, 500)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
