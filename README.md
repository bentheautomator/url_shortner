# SHRTNR - Badass URL Shortener

A sleek, full-featured URL shortener with a dark cyberpunk interface.

## Features

- **URL Shortening** - Generate short, memorable links
- **Custom Codes** - Create your own vanity URLs
- **Click Analytics** - Track clicks, referrers, and more
- **QR Code Generation** - Download QR codes for any link
- **API Key Authentication** - Secure access to your links
- **Responsive Design** - Looks great on any device

## Tech Stack

- **Backend**: Python FastAPI + SQLite
- **Frontend**: React + Tailwind CSS + Vite
- **Styling**: Dark theme with glowing cyber aesthetics

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/shorten` | Shorten a URL |
| GET | `/{code}` | Redirect to original URL |
| GET | `/api/urls` | List all URLs |
| GET | `/api/urls/{code}` | Get URL stats |
| GET | `/api/urls/{code}/qr` | Generate QR code |
| DELETE | `/api/urls/{code}` | Delete a URL |
| GET | `/api/stats` | Global statistics |
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

## License

MIT
