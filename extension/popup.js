// SHRTNR Browser Extension - Popup Script

const DEFAULT_API_URL = 'https://shrtnr.vercel.app';

// Get configured API URL from storage
async function getApiUrl() {
  const { apiUrl } = await chrome.storage.sync.get(['apiUrl']);
  return apiUrl || DEFAULT_API_URL;
}

const urlInput = document.getElementById('url-input');
const customToggle = document.getElementById('custom-toggle');
const customWrapper = document.getElementById('custom-wrapper');
const customInput = document.getElementById('custom-input');
const shortenBtn = document.getElementById('shorten-btn');
const result = document.getElementById('result');
const resultUrl = document.getElementById('result-url');
const resultMessage = document.getElementById('result-message');

// Toggle custom code input
customToggle.addEventListener('change', () => {
  customWrapper.classList.toggle('show', customToggle.checked);
  if (customToggle.checked) {
    customInput.focus();
  }
});

// Get current tab URL on popup open
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  if (tabs[0] && tabs[0].url) {
    urlInput.value = tabs[0].url;
  }
});

// Shorten button click
shortenBtn.addEventListener('click', async () => {
  const url = urlInput.value.trim();

  if (!url) {
    showError('Please enter a URL');
    return;
  }

  shortenBtn.disabled = true;
  shortenBtn.textContent = 'Shortening...';

  try {
    const { apiKey } = await chrome.storage.sync.get(['apiKey']);
    const apiUrl = await getApiUrl();

    const headers = {
      'Content-Type': 'application/json'
    };

    if (apiKey) {
      headers['X-API-Key'] = apiKey;
    }

    const body = { url };
    if (customToggle.checked && customInput.value.trim()) {
      body.custom_code = customInput.value.trim();
    }

    const response = await fetch(`${apiUrl}/api/shorten`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body)
    });

    const data = await response.json();

    if (!response.ok) {
      showError(data.detail || 'Failed to shorten URL');
      return;
    }

    // Copy to clipboard
    await navigator.clipboard.writeText(data.short_url);

    // Show success
    showSuccess(data.short_url);

  } catch (error) {
    showError('Failed to connect to SHRTNR server');
  } finally {
    shortenBtn.disabled = false;
    shortenBtn.textContent = 'Shorten URL';
  }
});

// Enter key to submit
urlInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    shortenBtn.click();
  }
});

customInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    shortenBtn.click();
  }
});

function showSuccess(shortUrl) {
  result.classList.remove('error');
  result.classList.add('show');
  resultUrl.textContent = shortUrl;
  resultMessage.textContent = 'Copied to clipboard!';
}

function showError(message) {
  result.classList.add('error', 'show');
  resultUrl.textContent = message;
  resultMessage.textContent = '';
}

// Settings link
document.getElementById('settings-link').addEventListener('click', async (e) => {
  e.preventDefault();

  const { apiUrl, apiKey } = await chrome.storage.sync.get(['apiUrl', 'apiKey']);
  const currentUrl = apiUrl || DEFAULT_API_URL;

  const choice = prompt(
    `SHRTNR Settings:\n\n` +
    `1. API URL: ${currentUrl}\n` +
    `2. API Key: ${apiKey ? '***' + apiKey.slice(-4) : 'Not set'}\n\n` +
    `Enter "url" to change API URL, "key" to change API key, or "clear" to reset all:`
  );

  if (choice === null) return;

  if (choice.toLowerCase() === 'url') {
    const newUrl = prompt('Enter API URL:', currentUrl);
    if (newUrl !== null && newUrl.trim()) {
      chrome.storage.sync.set({ apiUrl: newUrl.trim() });
      alert('API URL saved!');
    }
  } else if (choice.toLowerCase() === 'key') {
    const newKey = prompt('Enter your API key (leave empty to clear):');
    if (newKey !== null) {
      if (newKey.trim()) {
        chrome.storage.sync.set({ apiKey: newKey.trim() });
        alert('API key saved!');
      } else {
        chrome.storage.sync.remove('apiKey');
        alert('API key cleared!');
      }
    }
  } else if (choice.toLowerCase() === 'clear') {
    chrome.storage.sync.remove(['apiUrl', 'apiKey']);
    alert('Settings reset to defaults!');
  }
});
