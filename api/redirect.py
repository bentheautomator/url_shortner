"""GET /:code - Redirect handler with viral interstitial"""
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from api._db import get_db, URL, Click, BASE_URL, init_db

init_db()

INTERSTITIAL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redirecting... | SHRTNR</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0a0f 0%, #0f1419 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #f8fafc;
        }}
        .container {{ text-align: center; padding: 2rem; }}
        .logo {{
            font-size: 2rem;
            font-weight: bold;
            background: linear-gradient(90deg, #0ea5e9, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }}
        .message {{ color: #94a3b8; margin-bottom: 2rem; }}
        .loader {{
            width: 40px; height: 40px;
            border: 3px solid #1e293b;
            border-top: 3px solid #0ea5e9;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 2rem;
        }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        .cta {{
            background: rgba(14, 165, 233, 0.1);
            border: 1px solid rgba(14, 165, 233, 0.3);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            display: inline-block;
        }}
        .cta a {{ color: #0ea5e9; text-decoration: none; font-weight: 500; }}
        .cta a:hover {{ text-decoration: underline; }}
        .skip {{ margin-top: 1rem; font-size: 0.875rem; color: #64748b; }}
        .skip a {{ color: #94a3b8; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">SHRTNR</div>
        <div class="loader"></div>
        <p class="message">Redirecting you to your destination...</p>
        <div class="cta">
            <a href="{base_url}" target="_blank">Create your own short link in 5 seconds →</a>
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


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse the path to get short code
            parsed = urlparse(self.path)
            path = parsed.path.strip('/')
            query = parse_qs(parsed.query)

            # Get short code from path or query param
            short_code = query.get('code', [path])[0] if not path.startswith('api') else None

            if not short_code:
                self.send_error(404, "Not found")
                return

            db = next(get_db())
            url = db.query(URL).filter(URL.short_code == short_code).first()

            if not url:
                self.send_error(404, "URL not found")
                return

            # Record click
            click = Click(
                url_id=url.id,
                ip_address=self.headers.get('X-Forwarded-For', self.client_address[0] if self.client_address else None),
                user_agent=self.headers.get('User-Agent'),
                referer=self.headers.get('Referer')
            )
            db.add(click)
            db.commit()

            # Check if direct redirect requested
            direct = 'direct' in query and query['direct'][0].lower() == 'true'

            if direct or self.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Direct redirect
                self.send_response(307)
                self.send_header('Location', url.original_url)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
            else:
                # Show interstitial
                html = INTERSTITIAL_HTML.format(
                    destination=url.original_url,
                    base_url=BASE_URL
                )
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"detail": str(e)}).encode())
