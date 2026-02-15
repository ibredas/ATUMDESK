import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { Wordmark } from '../../components/Brand/Wordmark'
import { ArrowLeft, Bot, BookOpen, ThumbsUp, ThumbsDown, CheckCircle } from 'lucide-react'

export default function PortalTicketDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [ticket, setTicket] = useState(null)
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) { navigate('/portal/login'); return }
    fetchTicket()
    fetchComments()
  }, [id])

  const fetchTicket = async () => {
    try {
      const res = await fetch(`/api/v1/tickets/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.status === 401) { navigate('/portal/login'); return }
      if (res.ok) setTicket(await res.json())
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const fetchComments = async () => {
    try {
      const res = await fetch(`/api/v1/comments/ticket/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setComments(Array.isArray(data) ? data.filter(c => !c.is_internal) : [])
      }
    } catch (e) { console.error(e) }
  }

  const addComment = async (e) => {
    e.preventDefault()
    if (!newComment.trim()) return
    try {
      await fetch(`/api/v1/comments/ticket/${id}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: newComment, is_internal: false }),
      })
      setNewComment('')
      fetchComments()
    } catch (e) { console.error(e) }
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-[var(--atum-bg)]"><div className="spinner"></div></div>
  }

  return (
    <div className="min-h-screen bg-[var(--atum-bg)]">
      <div className="grain-overlay"></div>
      <nav className="relative z-50 flex items-center justify-between px-6 py-4 border-b border-[var(--atum-border)] backdrop-blur-sm">
        <Wordmark className="h-6 text-[#60a5fa]" suffix="PORTAL" />
        <Link to="/portal/tickets" className="text-[10px] uppercase tracking-widest text-[var(--atum-text-muted)] hover:text-white transition-colors flex items-center gap-1">
          <ArrowLeft size={12} /> My Tickets
        </Link>
      </nav>

      <div className="relative z-10 max-w-3xl mx-auto px-6 py-8">
        {ticket ? (
          <>
            <div className="glass-panel rounded-xl p-6 mb-6">
              <div className="flex items-start justify-between gap-4 mb-4">
                <h1 className="text-xl font-bold flex-1">{ticket.subject}</h1>
                <div className="flex items-center gap-2">
                  <span className={`badge badge-${ticket.status}`}>{ticket.status.replace('_', ' ')}</span>
                  <span className={`badge badge-${ticket.priority}`}>{ticket.priority}</span>
                </div>
              </div>
              <p className="text-[var(--atum-text-1)] text-sm leading-relaxed mb-4">{ticket.description}</p>
              <div className="text-[10px] text-[var(--atum-text-muted)] uppercase tracking-widest border-t border-[var(--atum-border)] pt-4">
                Created: {new Date(ticket.created_at).toLocaleString()}
              </div>
            </div>

            {/* Gap 7: KB Suggestions */}
            <KBSuggestions ticketId={id} />

            <div className="glass-panel rounded-xl p-6 mb-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">Conversation</h2>
              {comments.length === 0 ? (
                <p className="text-[var(--atum-text-muted)] text-sm py-4">No replies yet</p>
              ) : (
                <div className="space-y-4">
                  {comments.map(c => (
                    <div key={c.id} className="glass-card rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-white flex items-center gap-1">{c.author_name} {c.is_ai_generated && <Bot size={12} className="text-blue-400" />}</span>
                        <span className="text-[10px] text-[var(--atum-text-muted)]">{new Date(c.created_at).toLocaleString()}</span>
                      </div>
                      <p className="text-sm text-[var(--atum-text-1)]">{c.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <form onSubmit={addComment} className="glass-panel rounded-xl p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">Reply</h2>
              <textarea value={newComment} onChange={(e) => setNewComment(e.target.value)}
                className="atum-input mb-4" rows={3} placeholder="Type your reply..." style={{ resize: 'vertical' }} />
              <button type="submit"
                className="py-3 px-6 rounded-lg bg-[#3b82f6] text-white font-bold text-sm tracking-wide transition-all hover:bg-[#2563eb] border border-blue-500/30">
                Send Reply
              </button>
            </form>
          </>
        ) : (
          <div className="text-center py-16 text-[var(--atum-text-muted)]"><p>Ticket not found</p></div>
        )}
      </div>
    </div>
  )
}

function KBSuggestions({ ticketId }) {
  const [articles, setArticles] = useState([])
  const [loaded, setLoaded] = useState(false)
  const token = localStorage.getItem('atum_desk_token')

  useEffect(() => {
    const fetchKB = async () => {
      try {
        const res = await fetch(`/api/v1/ai/tickets/${ticketId}/kb-suggestions`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          setArticles(Array.isArray(data) ? data : data.items || [])
        }
      } catch (e) { /* KB suggestions may not exist */ }
      setLoaded(true)
    }
    fetchKB()
  }, [ticketId])

  const voteArticle = async (articleId, helpful) => {
    try {
      await fetch(`/api/v1/ai/tickets/${ticketId}/kb-suggestions/${articleId}/vote`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ helpful })
      })
      setArticles(prev => prev.map(a => a.id === articleId ? { ...a, voted: helpful } : a))
    } catch (e) { /* best effort */ }
  }

  if (!loaded || articles.length === 0) return null

  return (
    <div className="glass-panel rounded-xl p-6 mb-6 border border-blue-500/20">
      <h2 className="text-sm font-bold uppercase tracking-widest text-blue-400 mb-4 flex items-center gap-2"><BookOpen size={14} /> Related Articles</h2>
      <p className="text-xs text-[var(--atum-text-muted)] mb-4">These knowledge base articles may help resolve your issue:</p>
      <div className="space-y-3">
        {articles.slice(0, 5).map((article, i) => (
          <div key={article.id || i} className="glass-card rounded-lg p-4">
            <h3 className="text-sm font-medium text-white mb-1">{article.title || 'Article'}</h3>
            <p className="text-xs text-[var(--atum-text-1)] mb-2">{article.excerpt?.substring(0, 150) || ''}</p>
            <div className="flex items-center gap-3">
              <span className="text-[10px] text-[var(--atum-text-muted)]">Relevance: {((article.relevance_score || 0) * 100).toFixed(0)}%</span>
              {article.voted === undefined ? (
                <>
                  <button onClick={() => voteArticle(article.id, true)} className="text-[10px] bg-green-500/20 text-green-300 px-2 py-0.5 rounded hover:bg-green-500/40 flex items-center gap-0.5"><ThumbsUp size={10} /> Helpful</button>
                  <button onClick={() => voteArticle(article.id, false)} className="text-[10px] bg-red-500/20 text-red-300 px-2 py-0.5 rounded hover:bg-red-500/40 flex items-center gap-0.5"><ThumbsDown size={10} /> Not Helpful</button>
                </>
              ) : (
                <span className="text-[10px] text-green-400 flex items-center gap-0.5"><CheckCircle size={10} /> Thanks for feedback</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
