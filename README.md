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

- **Backend**: Python Serverless Functions (Vercel)
- **Database**: Neon Postgres
- **Frontend**: React + Tailwind CSS + Vite
- **CLI**: Node.js with Commander
- **Extension**: Chrome Manifest V3
- **Styling**: Dark cyber theme with glowing effects

## Deployment

See [DEPLOY.md](./DEPLOY.md) for deployment instructions to Vercel with Neon Postgres.

## Quick Start (Local Development)

### With Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Run locally (requires DATABASE_URL in .env)
vercel dev
```

### Legacy FastAPI Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Only

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

# Configure (optional - defaults to https://shrtnr.vercel.app)
shrtnr config --api-url https://your-instance.vercel.app
shrtnr config --api-key your-api-key

# Usage
shrtnr https://example.com/long-url
shrtnr https://example.com -c my-code  # Custom code
shrtnr stats                           # Global stats
shrtnr list                            # List your URLs
```

See [cli/README.md](./cli/README.md) for full CLI documentation.

### Browser Extension

1. Open Chrome -> `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension` folder
5. Click Settings to configure your API URL (defaults to Vercel deployment)
6. Right-click any link -> "SHRTNR This Link"

See [extension/README.md](./extension/README.md) for full extension documentation.

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
├── api/               # Vercel serverless functions
│   ├── _db.py         # Shared database module
│   ├── shorten.py     # POST /api/shorten
│   ├── redirect.py    # GET /:code (with interstitial)
│   ├── stats.py       # GET /api/stats
│   ├── trending.py    # GET /api/trending
│   ├── urls/          # URL management endpoints
│   └── keys/          # API key management
├── frontend/          # React app
│   ├── src/
│   │   ├── App.jsx    # Main component
│   │   └── index.css  # Cyber styling
│   └── package.json
├── cli/               # Command-line tool
│   ├── bin/shrtnr.js
│   ├── package.json
│   └── README.md
├── extension/         # Chrome extension
│   ├── manifest.json
│   ├── background.js
│   ├── popup.html/js
│   ├── icons/
│   └── README.md
├── backend/           # Legacy FastAPI server (for local dev)
├── vercel.json        # Vercel configuration
├── requirements.txt   # Python dependencies
├── DEPLOY.md          # Deployment instructions
└── README.md
```

## License

MIT

---

**Short links, big impact.**
