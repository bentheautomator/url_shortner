// SHRTNR Browser Extension - Background Service Worker

const API_URL = 'http://localhost:8000';

// Create context menu on install
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'shrtnr-link',
    title: 'SHRTNR This Link',
    contexts: ['link']
  });

  chrome.contextMenus.create({
    id: 'shrtnr-page',
    title: 'SHRTNR This Page',
    contexts: ['page']
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  let urlToShorten;

  if (info.menuItemId === 'shrtnr-link') {
    urlToShorten = info.linkUrl;
  } else if (info.menuItemId === 'shrtnr-page') {
    urlToShorten = info.pageUrl;
  }

  if (urlToShorten) {
    await shortenUrl(urlToShorten);
  }
});

// Shorten URL function
async function shortenUrl(url) {
  try {
    // Get API key from storage
    const { apiKey } = await chrome.storage.sync.get(['apiKey']);

    const headers = {
      'Content-Type': 'application/json'
    };

    if (apiKey) {
      headers['X-API-Key'] = apiKey;
    }

    const response = await fetch(`${API_URL}/api/shorten`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ url })
    });

    const data = await response.json();

    if (!response.ok) {
      showNotification('Error', data.detail || 'Failed to shorten URL');
      return;
    }

    // Copy to clipboard
    await copyToClipboard(data.short_url);

    // Show success notification
    showNotification('URL Shortened!', `${data.short_url}\nCopied to clipboard!`);

  } catch (error) {
    showNotification('Error', 'Failed to connect to SHRTNR. Is the server running?');
  }
}

// Copy to clipboard (works in service worker context)
async function copyToClipboard(text) {
  // Use offscreen document for clipboard access
  try {
    await chrome.offscreen.createDocument({
      url: 'offscreen.html',
      reasons: ['CLIPBOARD'],
      justification: 'Write text to clipboard'
    });
  } catch (e) {
    // Document might already exist
  }

  chrome.runtime.sendMessage({
    type: 'copy-to-clipboard',
    text: text
  });
}

// Show notification
function showNotification(title, message) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon128.png',
    title: title,
    message: message
  });
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'shorten') {
    shortenUrl(request.url).then(() => {
      sendResponse({ success: true });
    }).catch((error) => {
      sendResponse({ success: false, error: error.message });
    });
    return true; // Keep channel open for async response
  }
});
