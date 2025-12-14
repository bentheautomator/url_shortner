// Handle clipboard operations from service worker
chrome.runtime.onMessage.addListener((request) => {
  if (request.type === 'copy-to-clipboard') {
    navigator.clipboard.writeText(request.text);
  }
});
