# SHRTNR - Critical Bug Report

**Date:** December 16, 2025
**Priority:** P0 - CRITICAL
**Status:** Open
**Environment:** Production (https://urlshortner-dun.vercel.app)

---

## Bug #1: Dynamic API Routes Return HTML Instead of JSON

### Severity: 🔴 P0 - CRITICAL

### Affected Endpoints
- `GET /api/urls/:code` - URL details & analytics
- `GET /api/urls/:code/qr` - QR code generation
- `DELETE /api/urls/:code` - URL deletion
- `DELETE /api/keys/:id` - API key revocation

### Current Behavior
```bash
$ curl https://urlshortner-dun.vercel.app/api/urls/abc123
<!DOCTYPE html>
<html lang="en" class="dark">
  <head>
    <meta charset="UTF-8" />
    ...
```

**Status:** 200 OK
**Content-Type:** text/html

### Expected Behavior
```json
{
  "id": 1,
  "original_url": "https://example.com",
  "short_code": "abc123",
  "created_at": "2025-12-16T...",
  "click_count": 42,
  "clicks_by_day": {"2025-12-16": 10},
  "top_referers": [{"referer": "Direct", "count": 25}]
}
```

**Status:** 200 OK
**Content-Type:** application/json

### Root Cause
Vercel routing configuration is catching API paths before they reach serverless functions.

**Current `vercel.json`:**
```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/$1" },
    { "source": "/:code([a-zA-Z0-9_-]{3,20})", "destination": "/api/redirect?code=:code" },
    { "source": "/((?!assets|favicon).*)", "destination": "/index.html" }
  ]
}
```

The third rewrite rule `/((?!assets|favicon).*)` matches `/api/urls/abc123` and serves `index.html`.

### Solution

**Option 1: Update catch-all to exclude /api**
```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/$1" },
    { "source": "/:code([a-zA-Z0-9_-]{3,20})", "destination": "/api/redirect?code=:code" },
    { "source": "/((?!api|assets|favicon).*)", "destination": "/index.html" }
  ]
}
```

**Option 2: More explicit routing (RECOMMENDED)**
```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "/api/:path*" },
    { "source": "/:code([a-zA-Z0-9_-]{3,20})", "destination": "/api/redirect?code=:code" },
    { "source": "/:path*", "destination": "/index.html" }
  ]
}
```

### Testing After Fix
```bash
# Test URL details
curl https://urlshortner-dun.vercel.app/api/urls/abc123
# Should return JSON, not HTML

# Test QR code
curl https://urlshortner-dun.vercel.app/api/urls/abc123/qr
# Should return JSON with base64 image

# Test DELETE
curl -X DELETE https://urlshortner-dun.vercel.app/api/urls/abc123
# Should return 200 with success message
```

### Impact
- **URL analytics:** Cannot view click stats, referrers, or click history
- **QR codes:** Cannot generate QR codes for links
- **URL deletion:** Cannot delete shortened URLs
- **API key management:** Cannot revoke API keys
- **Frontend features:** QR button, stats button, delete button all broken

### Files Affected
- `/api/urls/[code].py` - Working code, routing broken
- `/api/urls/[code]/qr.py` - Working code, routing broken
- `/api/keys/[id].py` - Working code, routing broken
- `vercel.json` - Needs fix

---

## Bug #2: DELETE Methods Return 405 Method Not Allowed

### Severity: 🔴 P0 - CRITICAL

### Affected Endpoints
- `DELETE /api/urls/:code`
- `DELETE /api/keys/:id`

### Current Behavior
```bash
$ curl -X DELETE https://urlshortner-dun.vercel.app/api/urls/abc123
(empty response)
```

**Status:** 405 Method Not Allowed

### Expected Behavior
```json
{
  "message": "URL deleted successfully"
}
```

**Status:** 200 OK

### Root Cause
Vercel is not routing DELETE requests to serverless functions. This could be due to:

1. **HTTP method not configured** in Vercel deployment
2. **Missing methods in vercel.json** configuration
3. **Vercel framework detection** not recognizing Python handlers with DELETE

### Solution

**Option 1: Add methods configuration to vercel.json**
```json
{
  "functions": {
    "api/urls/[code].py": {
      "methods": ["GET", "DELETE", "OPTIONS"]
    },
    "api/keys/[id].py": {
      "methods": ["DELETE", "OPTIONS"]
    }
  }
}
```

**Option 2: Use Vercel config API in Python files**
```python
# Add to top of api/urls/[code].py
"""
config:
  methods:
    - GET
    - DELETE
    - OPTIONS
"""
```

**Option 3: Combine with Route Handlers**
Create `api/urls/[code]/route.py`:
```python
from api.urls.[code] import handler

# Vercel will recognize this as supporting all methods
def GET(request):
    h = handler()
    return h.do_GET()

def DELETE(request):
    h = handler()
    return h.do_DELETE()
```

### Testing After Fix
```bash
# Test URL deletion
curl -X DELETE https://urlshortner-dun.vercel.app/api/urls/abc123
# Should return 200 OK with success message

# Verify deletion
curl https://urlshortner-dun.vercel.app/api/urls/abc123
# Should return 404 Not Found

# Test API key revocation
curl -X DELETE https://urlshortner-dun.vercel.app/api/keys/1
# Should return 200 OK with success message
```

### Impact
- Cannot delete shortened URLs
- Cannot revoke API keys
- Frontend delete buttons non-functional
- API cleanup not possible

---

## Bug #3: SQLite Database Not Persistent

### Severity: 🔴 P0 - CRITICAL (Data Loss)

### Current Implementation
```python
# api/_db.py
DATABASE_URL = "sqlite:///./urls.db"
```

### Issue
Vercel serverless functions are **stateless**. Each function invocation may run on a different container, and the filesystem is ephemeral.

**Problems:**
1. **Data loss on redeployment** - All URLs/stats lost
2. **Inconsistent data** - Different functions see different data
3. **No persistence** - Database in `/tmp` cleared regularly
4. **Race conditions** - Concurrent requests hit different DBs

### Evidence
During testing, different API calls returned inconsistent URL counts, suggesting data is not shared across function invocations.

### Solution

**RECOMMENDED: Vercel Postgres**
```bash
# Install Vercel Postgres
vercel link
vercel postgres create
```

Update `api/_db.py`:
```python
import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv(
    'POSTGRES_URL',
    'sqlite:///./urls.db'  # Fallback for local dev
)

engine = create_engine(DATABASE_URL)
```

**Alternative: External PostgreSQL**
```python
# Use Supabase, Neon, Railway, etc.
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://user:pass@host:5432/dbname'
)
```

**Alternative: Vercel KV (Redis)**
Good for simple key-value storage, but requires schema changes.

### Migration Steps
1. Export existing SQLite data (if any)
2. Create Vercel Postgres database
3. Update DATABASE_URL environment variable
4. Deploy updated code
5. Import existing data (if any)

### Testing After Fix
```bash
# Create URL
curl -X POST https://urlshortner-dun.vercel.app/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"https://test.com"}'
# Note the short_code

# Wait 5 minutes (force function recycling)

# Verify URL still exists
curl https://urlshortner-dun.vercel.app/api/urls
# Should still show the URL

# Test across multiple requests
for i in {1..10}; do
  curl https://urlshortner-dun.vercel.app/api/urls | jq '.[] | .short_code'
done
# All responses should show consistent data
```

### Impact
- **Data integrity:** Risk of data loss
- **User experience:** Links may disappear
- **Analytics:** Stats unreliable
- **Production readiness:** NOT production-safe

---

## Bug #4: No Rate Limiting

### Severity: 🟡 P1 - HIGH (Security)

### Issue
Anyone can create unlimited URLs without authentication or rate limiting.

### Exploitation
```bash
# Create 1000 URLs in seconds
for i in {1..1000}; do
  curl -X POST https://urlshortner-dun.vercel.app/api/shorten \
    -H "Content-Type: application/json" \
    -d "{\"url\":\"https://spam.com/$i\"}"
done
```

### Solution

**Option 1: Vercel Edge Config with Rate Limiting**
```python
from vercel_rate_limit import rate_limit

@rate_limit(
    requests=10,
    window=60,  # 10 requests per minute
    identifier='ip'
)
def do_POST(self):
    # existing code
```

**Option 2: Redis-based Rate Limiting**
```python
import redis
from datetime import datetime, timedelta

redis_client = redis.from_url(os.getenv('REDIS_URL'))

def check_rate_limit(ip_address):
    key = f"rate_limit:{ip_address}"
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, 60)  # 60 second window
    return count <= 10  # Max 10 requests per minute
```

**Option 3: Vercel Edge Middleware**
```typescript
// middleware.ts
import { next } from '@vercel/edge';
import { Ratelimit } from '@upstash/ratelimit';

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '1 m'),
});

export default async function middleware(request: Request) {
  const ip = request.headers.get('x-forwarded-for');
  const { success } = await ratelimit.limit(ip);

  if (!success) {
    return new Response('Rate limit exceeded', { status: 429 });
  }

  return next();
}
```

### Recommended Limits
- **URL creation:** 10 per minute per IP
- **API key creation:** 5 per hour per IP
- **URL deletion:** 20 per minute per API key
- **Stats/analytics:** 60 per minute per IP

---

## Bug #5: No URL Validation

### Severity: 🟡 P1 - HIGH (Security)

### Issue
The API accepts any string as a URL without validation.

### Exploitation
```bash
# XSS attempt
curl -X POST https://urlshortner-dun.vercel.app/api/shorten \
  -d '{"url":"javascript:alert(1)"}'

# Malicious redirects
curl -X POST https://urlshortner-dun.vercel.app/api/shorten \
  -d '{"url":"https://phishing-site.com/steal-credentials"}'

# Internal network
curl -X POST https://urlshortner-dun.vercel.app/api/shorten \
  -d '{"url":"http://localhost:22"}'
```

### Solution

**Add URL validation in `api/shorten.py`:**
```python
from urllib.parse import urlparse
import re

BLOCKED_DOMAINS = [
    'localhost', '127.0.0.1', '0.0.0.0',
    '10.', '172.16.', '192.168.',  # Private IPs
]

ALLOWED_SCHEMES = ['http', 'https']

def validate_url(url: str) -> tuple[bool, str]:
    """Validate URL is safe to redirect to."""

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format"

    # Check scheme
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False, f"Scheme must be http or https"

    # Check for blocked domains
    hostname = parsed.hostname or ''
    for blocked in BLOCKED_DOMAINS:
        if hostname.startswith(blocked):
            return False, "Cannot shorten internal/private URLs"

    # Check for suspicious patterns
    if 'javascript:' in url.lower():
        return False, "JavaScript URLs not allowed"

    if 'data:' in url.lower():
        return False, "Data URLs not allowed"

    # Optional: Check against malware/phishing lists
    # if is_malicious(url):
    #     return False, "URL flagged as potentially malicious"

    return True, ""

# In handler.do_POST():
valid, error = validate_url(url)
if not valid:
    self.send_json({"detail": error}, 400)
    return
```

### Additional Security
```python
# URL length limit
MAX_URL_LENGTH = 2048

if len(url) > MAX_URL_LENGTH:
    return {"detail": "URL too long"}, 400

# Check against Google Safe Browsing API
from google.cloud import safebrowsing

def check_safe_browsing(url: str) -> bool:
    client = safebrowsing.SafeBrowsingClient()
    response = client.lookup_uri(url)
    return response.threat_type == 'THREAT_TYPE_UNSPECIFIED'
```

---

## Bug #6: Frontend Test False Positive

### Severity: 🔵 P3 - LOW (Test Issue, Not App Bug)

### Issue
Test reports "Missing: ['Form input']" but form is present and functional.

### Root Cause
Test checks static HTML source before React renders:
```python
html = response.text
'input' in html.lower()  # False - React not executed
```

### Solution
Update test to use Selenium/Playwright for JavaScript execution:
```python
from playwright.sync_api import sync_playwright

def test_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL)

        # Wait for React to render
        page.wait_for_selector('input[type="text"]')

        # Check elements
        assert page.locator('input').count() > 0
        assert page.locator('button:has-text("Shorten")').count() > 0
```

Or update to check for React root:
```python
if '<div id="root"></div>' in html and '<script type="module"' in html:
    results.add_test(category, "React app structure", True)
```

---

## Summary of Fixes Required

### Critical (Deploy ASAP)
1. ✅ **Fix vercel.json routing** - Add `(?!api)` to catch-all
2. ✅ **Enable DELETE methods** - Add methods configuration
3. ✅ **Migrate to PostgreSQL** - Use Vercel Postgres

### High Priority (Before Public Launch)
4. ⚠️ **Add rate limiting** - Prevent abuse
5. ⚠️ **Add URL validation** - Block malicious URLs

### Medium Priority
6. 📝 **Update frontend tests** - Use Playwright/Selenium
7. 📝 **Add authentication** - Secure API key management

---

## Deployment Checklist

Before next deployment:
- [ ] Update vercel.json with routing fix
- [ ] Add methods configuration for DELETE endpoints
- [ ] Create Vercel Postgres database
- [ ] Update DATABASE_URL environment variable
- [ ] Add rate limiting middleware
- [ ] Add URL validation to shorten endpoint
- [ ] Test all endpoints after deployment
- [ ] Monitor logs for errors
- [ ] Verify data persistence across requests

---

## Contact
**QA Team:** qa@shrtnr.io
**Deployment:** Deploy to staging first, then production after validation
**Rollback Plan:** Keep previous deployment active until verification complete

---

**Last Updated:** 2025-12-16T14:40:00Z
