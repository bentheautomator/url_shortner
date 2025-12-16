# SHRTNR CLI

Command-line interface for SHRTNR - the badass URL shortener.

## Installation

```bash
# Install globally from npm (once published)
npm install -g shrtnr-cli

# Or install from source
cd cli
npm install
npm link
```

## Configuration

Configure the CLI to point to your SHRTNR instance:

```bash
# Set your API URL (default: https://shrtnr.vercel.app)
shrtnr config --api-url https://your-shrtnr.vercel.app

# Set your API key for authenticated requests
shrtnr config --api-key your-api-key-here

# View current config
shrtnr config --show
```

You can also use environment variables:
```bash
export SHRTNR_API_URL=https://your-shrtnr.vercel.app
```

## Usage

### Shorten a URL

```bash
# Basic usage (copies to clipboard automatically)
shrtnr https://example.com/very-long-url

# With custom short code
shrtnr https://example.com/long-url -c my-link

# Without copying to clipboard
shrtnr https://example.com/long-url --no-copy

# With API key (for one-off use)
shrtnr https://example.com/long-url -k your-api-key
```

### View Statistics

```bash
# Global stats
shrtnr stats

# Stats for a specific link
shrtnr stats abc123
```

### List Your URLs

```bash
# List recent URLs (requires API key)
shrtnr list

# Limit results
shrtnr list -l 20
```

## Examples

```bash
$ shrtnr https://github.com/username/really-long-repository-name

  SHRTNR URL shortened!

  Original:  https://github.com/username/really-long-repository-name
  Short URL: https://shrtnr.vercel.app/x7Kp2m

  Copied to clipboard!

$ shrtnr stats x7Kp2m

  Stats retrieved!

  Short Code: /x7Kp2m
  Clicks:     42
  Created:    12/16/2024

  Top Referrers:
    1. Direct (25)
    2. twitter.com (12)
    3. reddit.com (5)
```

## Options

| Option | Description |
|--------|-------------|
| `-c, --custom <code>` | Use a custom short code |
| `-k, --api-key <key>` | API key for this request |
| `--no-copy` | Don't copy to clipboard |

## Commands

| Command | Description |
|---------|-------------|
| `shrtnr <url>` | Shorten a URL |
| `shrtnr config` | Configure CLI settings |
| `shrtnr stats [code]` | View statistics |
| `shrtnr list` | List your shortened URLs |

## Requirements

- Node.js 18.0.0 or higher
- A running SHRTNR instance

## License

MIT
