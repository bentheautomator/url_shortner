# Deploying SHRTNR to Vercel

## Prerequisites

1. **Vercel Account** - [vercel.com](https://vercel.com)
2. **Neon Account** - [neon.tech](https://neon.tech) (free tier works)
3. **GitHub** - Repo connected to Vercel

## Step 1: Create Neon Database

1. Go to [neon.tech](https://neon.tech) and create a free account
2. Create a new project (any name, e.g., "shrtnr")
3. Copy the connection string:
   ```
   postgresql://username:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```

## Step 2: Deploy to Vercel

### Option A: One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/bentheautomator/url_shortner)

### Option B: Manual Deploy

1. Push your code to GitHub
2. Go to [vercel.com/new](https://vercel.com/new)
3. Import your repository
4. Vercel will auto-detect the configuration

## Step 3: Configure Environment Variables

In Vercel Dashboard → Your Project → Settings → Environment Variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql://...` | Your Neon connection string |
| `SHRTNR_BASE_URL` | `https://your-app.vercel.app` | Your Vercel domain |

**Important:** After adding env vars, redeploy for changes to take effect.

## Step 4: Initialize Database

The database tables are created automatically on first request. Just visit your deployed app!

## Custom Domain

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain (e.g., `shrtnr.io`)
3. Update DNS records as instructed
4. Update `SHRTNR_BASE_URL` env var to your custom domain

## Environment Variables Reference

```bash
# Required
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Optional (defaults shown)
SHRTNR_BASE_URL=https://your-app.vercel.app
```

## Project Structure for Vercel

```
url_shortner/
├── api/                    # Python serverless functions
│   ├── _db.py              # Shared database module
│   ├── shorten.py          # POST /api/shorten
│   ├── stats.py            # GET /api/stats
│   ├── trending.py         # GET /api/trending
│   ├── redirect.py         # GET /:code (via rewrite)
│   ├── urls/
│   │   ├── index.py        # GET /api/urls
│   │   └── [code].py       # GET/DELETE /api/urls/:code
│   │   └── [code]/
│   │       └── qr.py       # GET /api/urls/:code/qr
│   └── keys/
│       ├── index.py        # GET/POST /api/keys
│       └── [id].py         # DELETE /api/keys/:id
├── frontend/               # React app (built to dist/)
├── vercel.json             # Vercel configuration
└── requirements.txt        # Python dependencies
```

## Troubleshooting

### "Database not configured" error
- Check `DATABASE_URL` is set in Vercel env vars
- Make sure it starts with `postgresql://` (not `postgres://`)
- Redeploy after adding env vars

### Short links not redirecting
- Check `SHRTNR_BASE_URL` matches your actual domain
- Verify the rewrite rules in `vercel.json`

### CORS errors
- All API endpoints include CORS headers
- If issues persist, check browser console for specific errors

### Cold starts
- First request may be slow (serverless cold start)
- Subsequent requests are fast
- Consider Vercel Pro for better performance

## Local Development

For local dev, you can still use the original FastAPI backend:

```bash
# Backend (original)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

Or test Vercel functions locally:

```bash
npm i -g vercel
vercel dev
```

## Costs

- **Vercel Free Tier**: 100GB bandwidth, serverless functions included
- **Neon Free Tier**: 0.5 GB storage, 190 compute hours/month

For most use cases, you can run SHRTNR completely free!
