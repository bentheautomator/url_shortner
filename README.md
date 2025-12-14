# SHRTNR - Badass URL Shortener

A sleek, full-featured URL shortener with a dark cyberpunk interface, built for developers who appreciate good design.

## Features

- **URL Shortening** - Generate short, memorable links
- **Custom Codes** - Create your own vanity URLs
- **Click Analytics** - Track clicks, referrers, and daily trends
- **QR Code Generation** - Download QR codes for any link
- **API Key Authentication** - Secure access to your links
- **Trending Page** - See the hottest links in real-time
- **Social Sharing** - One-click share to Twitter/Discord
- **Viral Interstitial** - Branded redirect page drives growth
- **CLI Tool** - Shorten URLs from your terminal
- **Browser Extension** - Right-click to shorten any link

## Tech Stack

- **Backend**: Python FastAPI + SQLite
- **Frontend**: React + Tailwind CSS + Vite
- **CLI**: Node.js with Commander
- **Extension**: Chrome Manifest V3
- **Styling**: Dark cyber theme with glowing effects

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3156

### CLI Tool

```bash
cd cli
npm install
npm link  # Makes 'shrtnr' available globally

# Usage
shrtnr https://example.com/long-url
shrtnr https://example.com -c my-code  # Custom code
shrtnr stats                           # Global stats
shrtnr list                            # List your URLs
```

### Browser Extension

1. Open Chrome → `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension` folder
5. Right-click any link → "SHRTNR This Link"

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/shorten` | Shorten a URL |
| GET | `/{code}` | Redirect (with viral interstitial) |
| GET | `/{code}?direct=true` | Direct redirect |
| GET | `/api/urls` | List all URLs |
| GET | `/api/urls/{code}` | Get URL stats |
| GET | `/api/urls/{code}/qr` | Generate QR code |
| DELETE | `/api/urls/{code}` | Delete a URL |
| GET | `/api/stats` | Global statistics |
| GET | `/api/trending` | Top 10 trending URLs |
| POST | `/api/keys` | Create API key |
| GET | `/api/keys` | List API keys |

## API Usage

### Shorten a URL

```bash
curl -X POST http://localhost:8000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url"}'
```

### Custom Short Code

```bash
curl -X POST http://localhost:8000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "custom_code": "my-link"}'
```

### With API Key

```bash
curl -X POST http://localhost:8000/api/shorten \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"url": "https://example.com"}'
```

### Get Trending

```bash
curl http://localhost:8000/api/trending
```

## Growth Features

### Viral Redirect Interstitial
Every click shows a branded "Powered by SHRTNR" page for 1.5 seconds before redirecting. This turns every shared link into a mini-ad.

To bypass (for API/programmatic use):
```
GET /{code}?direct=true
```

### Social Sharing
After shortening a URL, users can instantly share to Twitter or Discord with pre-filled text that promotes SHRTNR.

### Trending Page
Shows the most-clicked links in the last 7 days, creating social proof and FOMO.

## CLI Tool

```
  ███████╗██╗  ██╗██████╗ ████████╗███╗   ██╗██████╗
  ██╔════╝██║  ██║██╔══██╗╚══██╔══╝████╗  ██║██╔══██╗
  ███████╗███████║██████╔╝   ██║   ██╔██╗ ██║██████╔╝
  ╚════██║██╔══██║██╔══██╗   ██║   ██║╚██╗██║██╔══██╗
  ███████║██║  ██║██║  ██║   ██║   ██║ ╚████║██║  ██║
  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝

Commands:
  shrtnr <url>              Shorten a URL (copies to clipboard)
  shrtnr <url> -c <code>    Use custom short code
  shrtnr stats              Show global stats
  shrtnr stats <code>       Show stats for specific URL
  shrtnr list               List your URLs
  shrtnr config --show      Show current config
  shrtnr config --api-key   Set your API key
```

## Browser Extension

- **Right-click menu**: "SHRTNR This Link" / "SHRTNR This Page"
- **Popup**: Quick shorten with optional custom code
- **Auto-copy**: Short URL automatically copied to clipboard
- **Notifications**: Success/error feedback

## Project Structure

```
url_shortner/
├── backend/           # FastAPI server
│   ├── app/
│   │   ├── main.py    # API routes
│   │   ├── models.py  # SQLAlchemy models
│   │   ├── schemas.py # Pydantic schemas
│   │   └── database.py
│   └── requirements.txt
├── frontend/          # React app
│   ├── src/
│   │   ├── App.jsx    # Main component
│   │   └── index.css  # Cyber styling
│   └── package.json
├── cli/               # Command-line tool
│   ├── bin/shrtnr.js
│   └── package.json
├── extension/         # Chrome extension
│   ├── manifest.json
│   ├── background.js
│   ├── popup.html/js
│   └── icons/
└── README.md
```

## License

MIT

---

**Short links, big impact.**
