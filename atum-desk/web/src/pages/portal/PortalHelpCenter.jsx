import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Wordmark } from '../../components/Brand/Wordmark'
import { Search, ThumbsUp, ThumbsDown, LogOut } from 'lucide-react'
import ReactMarkdown from 'react-markdown' // Note: Ensure this exists or use simple display

// Simple Article View Overlay or Navigate?
// Let's keep it simple: List with expand or navigate to detail?
// Portal usually has a detail page. I'll implement a simple master-detail here or separate page?
// App.jsx has no route for ticket detail. I should add one if needed.
// For now, expand in place or modal is easier for "Lite". 
// Actually, let's stick to the route plan: /portal/help usually lists categories.
// I'll implement a SEARCH + LIST view.

export default function PortalHelpCenter() {
  const navigate = useNavigate()
  // Portal technically works with "Customer Token" OR Public if we allow it.
  // KB router allows ANY authenticated user, checks role.
  // If Public Portal is truly public (unauthenticated), we need to adjust Router.
  // BUT the App only has PortalLogin. So we assume Authenticated Customer.

  const token = localStorage.getItem('atum_desk_token')
  const [articles, setArticles] = useState([])
  const [categories, setCategories] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [selectedArticle, setSelectedArticle] = useState(null)

  useEffect(() => {
    if (!token) { navigate('/portal/login'); return }
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [artRes, catRes] = await Promise.all([
        fetch('/api/v1/kb/articles?visibility=public', { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch('/api/v1/kb/categories', { headers: { 'Authorization': `Bearer ${token}` } })
      ])

      if (artRes.ok) setArticles(await artRes.json())
      if (catRes.ok) setCategories(await catRes.json())

    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const logout = () => {
    localStorage.removeItem('atum_desk_token')
    localStorage.removeItem('atum_desk_refresh')
    navigate('/portal/login')
  }

  const filteredArticles = articles.filter(a =>
    a.title.toLowerCase().includes(search.toLowerCase()) ||
    (a.content && a.content.toLowerCase().includes(search.toLowerCase()))
  )

  return (
    <div className="min-h-screen bg-[var(--atum-bg)]">
      <div className="grain-overlay"></div>

      {/* Header */}
      <nav className="relative z-50 flex items-center justify-between px-6 py-4 border-b border-[var(--atum-border)] backdrop-blur-sm">
        <div className="flex items-center gap-4">
          <Wordmark className="h-6 text-[#60a5fa]" suffix="PORTAL" />
          <Link to="/portal/tickets" className="text-sm text-[var(--atum-text-muted)] hover:text-white ml-6">My Tickets</Link>
          <Link to="/portal/help" className="text-sm font-bold text-white">Help Center</Link>
        </div>
        <button onClick={logout} className="text-[10px] uppercase tracking-widest text-[var(--atum-text-muted)] hover:text-red-400 transition-colors flex items-center gap-1">
          <LogOut size={12} /> Sign Out
        </button>
      </nav>

      <div className="relative z-10 max-w-4xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold mb-2 text-center text-white">How can we help?</h1>

        {/* Search */}
        <div className="max-w-xl mx-auto mb-12 relative">
          <input
            type="text"
            className="atum-input w-full pl-10 py-3 rounded-full bg-black/20 focus:bg-black/50 transition-all font-medium"
            placeholder="Search for answers..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <Search size={16} className="absolute left-4 top-3.5 text-[var(--atum-text-muted)]" />
        </div>

        {selectedArticle ? (
          <div className="glass-panel p-8 rounded-xl animate-fade-in">
            <button onClick={() => setSelectedArticle(null)} className="text-sm text-[var(--atum-text-muted)] mb-4 hover:text-white">← Back to Search</button>
            <h2 className="text-2xl font-bold mb-4 text-[#60a5fa]">{selectedArticle.title}</h2>
            <div className="prose prose-invert max-w-none whitespace-pre-wrap font-light text-[var(--atum-text-1)]">
              {selectedArticle.content}
            </div>
            <div className="mt-8 pt-6 border-t border-[var(--atum-border)] flex justify-between text-xs text-[var(--atum-text-muted)]">
              <span>Views: {selectedArticle.view_count}</span>
              <span className="flex items-center gap-2">Was this helpful? <ThumbsUp size={12} className="cursor-pointer hover:text-green-400" /> <ThumbsDown size={12} className="cursor-pointer hover:text-red-400" /></span>
            </div>
          </div>
        ) : (
          <div className="space-y-8">
            {loading ? <div className="spinner mx-auto"></div> : (
              <>
                {/* Categories? Only if we had many. List matches directly is better for now. */}

                {filteredArticles.length === 0 ? (
                  <div className="text-center text-[var(--atum-text-muted)]">No matches found.</div>
                ) : (
                  <div className="grid gap-4">
                    {filteredArticles.map(article => (
                      <div
                        key={article.id}
                        onClick={() => setSelectedArticle(article)}
                        className="glass-panel p-5 rounded-lg cursor-pointer hover:bg-white/5 transition-all group"
                      >
                        <h3 className="text-lg font-bold group-hover:text-[#60a5fa] transition-colors mb-1">{article.title}</h3>
                        <p className="text-sm text-[var(--atum-text-muted)] line-clamp-2">{article.content}</p>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
