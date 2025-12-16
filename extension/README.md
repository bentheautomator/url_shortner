# SHRTNR Browser Extension

Chrome extension for SHRTNR - shorten URLs with a single click.

## Features

- Shorten the current page URL with one click
- Right-click context menu to shorten any link
- Custom short codes support
- Automatic clipboard copy
- Configurable API URL and key

## Installation

### From Source (Developer Mode)

1. Clone or download this repository
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top right)
4. Click "Load unpacked"
5. Select the `extension` folder

### From Chrome Web Store

Coming soon!

## Usage

### Popup

1. Click the SHRTNR icon in your browser toolbar
2. The current page URL is automatically filled in
3. (Optional) Enable "Custom short code" for a custom alias
4. Click "Shorten URL"
5. The short URL is automatically copied to your clipboard

### Right-Click Menu

- **SHRTNR This Link** - Right-click any link to shorten it
- **SHRTNR This Page** - Right-click anywhere on a page to shorten the current URL

Both options automatically copy the shortened URL to your clipboard and show a notification.

## Configuration

Click "Settings" at the bottom of the popup to configure:

- **API URL**: Your SHRTNR instance URL (default: `https://shrtnr.vercel.app`)
- **API Key**: Your API key for authenticated requests

### Setting Up

1. Click the SHRTNR extension icon
2. Click "Settings" at the bottom
3. Type `url` to change the API URL
4. Type `key` to set your API key
5. Type `clear` to reset all settings

## Permissions

The extension requires these permissions:

- `contextMenus` - For right-click menu integration
- `clipboardWrite` - To copy shortened URLs
- `storage` - To save your API URL and key
- `notifications` - To show success/error messages
- `offscreen` - For clipboard access in service worker

## Development

The extension uses Chrome Manifest V3 with:

- `background.js` - Service worker for context menu and API calls
- `popup.html/js` - Popup UI for manual URL shortening
- `offscreen.html/js` - Helper for clipboard operations

### Testing Locally

1. Set the API URL to your local SHRTNR instance:
   - Click Settings > type `url` > enter `http://localhost:8000`
2. Make sure your local SHRTNR server is running

## License

MIT
