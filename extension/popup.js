// SHRTNR Browser Extension - Popup Script

const API_URL = 'http://localhost:8000';

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

    const response = await fetch(`${API_URL}/api/shorten`, {
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

// Settings link (placeholder)
document.getElementById('settings-link').addEventListener('click', (e) => {
  e.preventDefault();
  // For now, just show an alert
  const apiKey = prompt('Enter your API key (leave empty to clear):');
  if (apiKey !== null) {
    if (apiKey.trim()) {
      chrome.storage.sync.set({ apiKey: apiKey.trim() });
      alert('API key saved!');
    } else {
      chrome.storage.sync.remove('apiKey');
      alert('API key cleared!');
    }
  }
});
