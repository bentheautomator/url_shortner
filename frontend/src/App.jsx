import { useState, useEffect } from 'react'
import {
  Link2, Copy, Check, QrCode, BarChart3, Trash2,
  Zap, ExternalLink, ChevronDown, X, Loader2,
  Globe, MousePointerClick, Calendar, TrendingUp,
  Twitter, MessageCircle, Share2, Flame
} from 'lucide-react'

const API_BASE = '/api'

function App() {
  const [url, setUrl] = useState('')
  const [customCode, setCustomCode] = useState('')
  const [showCustom, setShowCustom] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [copied, setCopied] = useState(false)
  const [urls, setUrls] = useState([])
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)
  const [qrCode, setQrCode] = useState(null)
  const [selectedUrl, setSelectedUrl] = useState(null)
  const [urlStats, setUrlStats] = useState(null)
  const [showTrending, setShowTrending] = useState(false)
  const [trending, setTrending] = useState([])

  useEffect(() => {
    fetchUrls()
    fetchStats()
  }, [])

  const fetchUrls = async () => {
    try {
      const res = await fetch(`${API_BASE}/urls`)
      const data = await res.json()
      if (res.ok && Array.isArray(data)) {
        setUrls(data)
      }
    } catch (err) {
      console.error('Failed to fetch URLs:', err)
    }
  }

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/stats`)
      const data = await res.json()
      if (res.ok && data && !data.detail) {
        setStats(data)
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }

  const fetchUrlStats = async (shortCode) => {
    try {
      const res = await fetch(`${API_BASE}/urls/${shortCode}`)
      const data = await res.json()
      setUrlStats(data)
      setSelectedUrl(shortCode)
    } catch (err) {
      console.error('Failed to fetch URL stats:', err)
    }
  }

  const fetchTrending = async () => {
    try {
      const res = await fetch(`${API_BASE}/trending`)
      const data = await res.json()
      if (res.ok && Array.isArray(data)) {
        setTrending(data)
      }
      setShowTrending(true)
    } catch (err) {
      console.error('Failed to fetch trending:', err)
    }
  }

  const shareToTwitter = (shortUrl) => {
    const text = encodeURIComponent(`Just shortened my link with SHRTNR - the dark mode URL shortener that doesn't suck. ${shortUrl}`)
    window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank')
  }

  const shareToDiscord = (shortUrl) => {
    navigator.clipboard.writeText(`Check out my shortened link: ${shortUrl} - made with SHRTNR`)
    alert('Copied to clipboard! Paste in Discord.')
  }

  const shortenUrl = async (e) => {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${API_BASE}/shorten`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: url.trim(),
          custom_code: customCode.trim() || null
        })
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to shorten URL')
      }

      setResult(data)
      setUrl('')
      setCustomCode('')
      setShowCustom(false)
      fetchUrls()
      fetchStats()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = async (text) => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const fetchQrCode = async (shortCode) => {
    try {
      const res = await fetch(`${API_BASE}/urls/${shortCode}/qr`)
      const data = await res.json()
      setQrCode({ code: shortCode, image: data.qr_code })
    } catch (err) {
      console.error('Failed to fetch QR code:', err)
    }
  }

  const deleteUrl = async (shortCode) => {
    if (!confirm('Delete this shortened URL?')) return

    try {
      await fetch(`${API_BASE}/urls/${shortCode}`, { method: 'DELETE' })
      fetchUrls()
      fetchStats()
      if (selectedUrl === shortCode) {
        setSelectedUrl(null)
        setUrlStats(null)
      }
    } catch (err) {
      console.error('Failed to delete URL:', err)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-animated relative">
      <div className="noise-overlay" />

      {/* Header */}
      <header className="relative z-10 py-8 px-6">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Link2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                  SHRTNR
                </span>
              </h1>
              <p className="text-xs text-slate-500 font-mono">URL SHORTENER</p>
            </div>
          </div>

          {stats && (
            <div className="hidden md:flex items-center gap-6 text-sm">
              <button
                onClick={fetchTrending}
                className="flex items-center gap-2 text-slate-400 hover:text-cyan-400 transition-colors"
              >
                <Flame className="w-4 h-4 text-orange-500" />
                <span className="font-medium">Trending</span>
              </button>
              <div className="flex items-center gap-2 text-slate-400">
                <Globe className="w-4 h-4 text-cyan-400" />
                <span className="font-mono">{stats.total_urls}</span>
                <span className="text-slate-600">links</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <MousePointerClick className="w-4 h-4 text-cyan-400" />
                <span className="font-mono">{stats.total_clicks}</span>
                <span className="text-slate-600">clicks</span>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 px-6 pb-20">
        <div className="max-w-6xl mx-auto">

          {/* Hero Section */}
          <section className="text-center py-16 md:py-24">
            <h2 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
              <span className="text-white">Short links,</span>
              <br />
              <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
                big impact
              </span>
            </h2>
            <p className="text-slate-400 text-lg md:text-xl max-w-2xl mx-auto mb-12">
              Transform your long URLs into sleek, trackable links.
              With analytics, custom codes, and QR generation.
            </p>

            {/* URL Input Form */}
            <form onSubmit={shortenUrl} className="max-w-3xl mx-auto">
              <div className="glass rounded-2xl p-2 md:p-3 card-hover">
                <div className="flex flex-col md:flex-row gap-3">
                  <div className="flex-1 relative">
                    <input
                      type="text"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="Paste your long URL here..."
                      className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-5 py-4 text-white placeholder-slate-500 focus:outline-none input-glow font-mono text-sm md:text-base"
                    />
                    <button
                      type="button"
                      onClick={() => setShowCustom(!showCustom)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-cyan-400 transition-colors"
                    >
                      <ChevronDown className={`w-5 h-5 transition-transform ${showCustom ? 'rotate-180' : ''}`} />
                    </button>
                  </div>
                  <button
                    type="submit"
                    disabled={loading || !url.trim()}
                    className="btn-glow bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold px-8 py-4 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 min-w-[160px]"
                  >
                    {loading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <>
                        <Zap className="w-5 h-5" />
                        Shorten
                      </>
                    )}
                  </button>
                </div>

                {/* Custom Code Input */}
                {showCustom && (
                  <div className="mt-3 pt-3 border-t border-slate-700/50">
                    <div className="flex items-center gap-3">
                      <span className="text-slate-500 text-sm font-mono shrink-0">
                        shrtnr.io/
                      </span>
                      <input
                        type="text"
                        value={customCode}
                        onChange={(e) => setCustomCode(e.target.value.replace(/[^a-zA-Z0-9_-]/g, ''))}
                        placeholder="custom-code"
                        maxLength={20}
                        className="flex-1 bg-slate-900/50 border border-slate-700/50 rounded-lg px-4 py-2 text-white placeholder-slate-600 focus:outline-none input-glow font-mono text-sm"
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Error Message */}
              {error && (
                <div className="mt-4 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-xl text-sm flex items-center gap-2">
                  <X className="w-4 h-4 shrink-0" />
                  {error}
                </div>
              )}

              {/* Result */}
              {result && (
                <div className="mt-4 glass rounded-xl p-4 card-hover">
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-slate-500 mb-1">Your shortened URL</p>
                      <a
                        href={result.short_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-cyan-400 hover:text-cyan-300 font-mono text-lg truncate block"
                      >
                        {result.short_url}
                      </a>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => copyToClipboard(result.short_url)}
                        className="p-3 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
                        title="Copy"
                      >
                        {copied ? (
                          <Check className="w-5 h-5 text-green-400" />
                        ) : (
                          <Copy className="w-5 h-5 text-slate-400" />
                        )}
                      </button>
                      <button
                        onClick={() => fetchQrCode(result.short_code)}
                        className="p-3 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
                        title="QR Code"
                      >
                        <QrCode className="w-5 h-5 text-slate-400" />
                      </button>
                      <button
                        onClick={() => shareToTwitter(result.short_url)}
                        className="p-3 bg-slate-800 hover:bg-blue-600 rounded-lg transition-colors"
                        title="Share on Twitter"
                      >
                        <Twitter className="w-5 h-5 text-slate-400 hover:text-white" />
                      </button>
                      <button
                        onClick={() => shareToDiscord(result.short_url)}
                        className="p-3 bg-slate-800 hover:bg-indigo-600 rounded-lg transition-colors"
                        title="Share on Discord"
                      >
                        <MessageCircle className="w-5 h-5 text-slate-400 hover:text-white" />
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </form>
          </section>

          {/* URL List & Stats Grid */}
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Recent URLs */}
            <div className="lg:col-span-2">
              <div className="glass rounded-2xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-cyan-400" />
                    Recent Links
                  </h3>
                  <span className="text-xs text-slate-500 font-mono">
                    {urls.length} total
                  </span>
                </div>

                {urls.length === 0 ? (
                  <div className="text-center py-12 text-slate-500">
                    <Link2 className="w-12 h-12 mx-auto mb-3 opacity-30" />
                    <p>No links yet. Create your first one above!</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {urls.slice(0, 10).map((item) => (
                      <div
                        key={item.id}
                        className="bg-slate-900/50 rounded-xl p-4 border border-slate-800 hover:border-slate-700 transition-colors group"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <a
                                href={item.short_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-cyan-400 hover:text-cyan-300 font-mono text-sm flex items-center gap-1"
                              >
                                /{item.short_code}
                                <ExternalLink className="w-3 h-3" />
                              </a>
                              <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full font-mono">
                                {item.click_count} clicks
                              </span>
                            </div>
                            <p className="text-slate-500 text-xs truncate font-mono">
                              {item.original_url}
                            </p>
                          </div>
                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => copyToClipboard(item.short_url)}
                              className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                              title="Copy"
                            >
                              <Copy className="w-4 h-4 text-slate-500 hover:text-slate-300" />
                            </button>
                            <button
                              onClick={() => fetchQrCode(item.short_code)}
                              className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                              title="QR Code"
                            >
                              <QrCode className="w-4 h-4 text-slate-500 hover:text-slate-300" />
                            </button>
                            <button
                              onClick={() => fetchUrlStats(item.short_code)}
                              className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                              title="Stats"
                            >
                              <BarChart3 className="w-4 h-4 text-slate-500 hover:text-slate-300" />
                            </button>
                            <button
                              onClick={() => deleteUrl(item.short_code)}
                              className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4 text-slate-500 hover:text-red-400" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Stats Panel */}
            <div className="space-y-6">
              {/* Global Stats */}
              {stats && (
                <div className="glass rounded-2xl p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-cyan-400" />
                    Today's Stats
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-900/50 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold text-cyan-400 font-mono">
                        {stats.urls_today}
                      </div>
                      <div className="text-xs text-slate-500 mt-1">Links Created</div>
                    </div>
                    <div className="bg-slate-900/50 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold text-purple-400 font-mono">
                        {stats.clicks_today}
                      </div>
                      <div className="text-xs text-slate-500 mt-1">Clicks</div>
                    </div>
                  </div>
                </div>
              )}

              {/* URL Stats */}
              {urlStats && (
                <div className="glass rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">Link Analytics</h3>
                    <button
                      onClick={() => { setUrlStats(null); setSelectedUrl(null); }}
                      className="text-slate-500 hover:text-slate-300"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Short URL</p>
                      <p className="text-cyan-400 font-mono text-sm">/{urlStats.short_code}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Total Clicks</p>
                      <p className="text-2xl font-bold font-mono">{urlStats.click_count}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 mb-2">Top Referrers</p>
                      {urlStats.top_referers.length > 0 ? (
                        <div className="space-y-2">
                          {urlStats.top_referers.map((ref, i) => (
                            <div key={i} className="flex items-center justify-between text-sm">
                              <span className="text-slate-400 truncate">{ref.referer}</span>
                              <span className="text-slate-500 font-mono">{ref.count}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-slate-600 text-sm">No clicks yet</p>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* QR Code Modal */}
      {qrCode && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <div className="glass rounded-2xl p-6 max-w-sm w-full">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">QR Code</h3>
              <button
                onClick={() => setQrCode(null)}
                className="text-slate-500 hover:text-slate-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="bg-white rounded-xl p-4 mb-4">
              <img src={qrCode.image} alt="QR Code" className="w-full" />
            </div>
            <p className="text-center text-cyan-400 font-mono text-sm">
              /{qrCode.code}
            </p>
            <a
              href={qrCode.image}
              download={`qr-${qrCode.code}.png`}
              className="btn-glow bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold px-4 py-3 rounded-xl mt-4 flex items-center justify-center gap-2 w-full"
            >
              Download QR Code
            </a>
          </div>
        </div>
      )}

      {/* Trending Modal */}
      {showTrending && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <div className="glass rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <Flame className="w-6 h-6 text-orange-500" />
                Trending Links
              </h3>
              <button
                onClick={() => setShowTrending(false)}
                className="text-slate-500 hover:text-slate-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {trending.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <Flame className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>No trending links yet. Be the first!</p>
              </div>
            ) : (
              <div className="space-y-3 overflow-y-auto flex-1">
                {trending.map((item, index) => (
                  <div
                    key={item.id}
                    className="bg-slate-900/50 rounded-xl p-4 border border-slate-800 hover:border-cyan-500/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl font-bold text-slate-700 font-mono w-8">
                          #{index + 1}
                        </span>
                        <div>
                          <a
                            href={item.short_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-cyan-400 hover:text-cyan-300 font-mono flex items-center gap-1"
                          >
                            /{item.short_code}
                            <ExternalLink className="w-3 h-3" />
                          </a>
                          <p className="text-slate-600 text-xs mt-1">
                            Created {new Date(item.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold text-cyan-400 font-mono">
                          {item.click_count}
                        </div>
                        <div className="text-xs text-slate-500">clicks</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="mt-4 pt-4 border-t border-slate-700/50 text-center text-xs text-slate-500">
              Updated every 5 minutes • Only public links shown
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="relative z-10 py-8 px-6 border-t border-slate-800/50">
        <div className="max-w-6xl mx-auto text-center text-slate-600 text-sm">
          <p>Built with React, FastAPI, and a whole lot of style.</p>
        </div>
      </footer>
    </div>
  )
}

export default App
