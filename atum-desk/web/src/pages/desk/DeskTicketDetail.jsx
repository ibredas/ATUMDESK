import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { Wordmark } from '../../components/Brand/Wordmark'

export default function DeskTicketDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [ticket, setTicket] = useState(null)
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) { navigate('/desk/login'); return }
    fetchTicket()
    fetchComments()
  }, [id])

  const fetchTicket = async () => {
    try {
      const res = await fetch(`/api/v1/internal/tickets/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.status === 401) { navigate('/desk/login'); return }
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
        setComments(Array.isArray(data) ? data : [])
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

  const updateStatus = async (status) => {
    try {
      await fetch(`/api/v1/internal/tickets/${id}/status`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      })
      fetchTicket()
    } catch (e) { console.error(e) }
  }

  const logout = () => {
    localStorage.removeItem('atum_desk_token')
    localStorage.removeItem('atum_desk_refresh')
    navigate('/desk/login')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[var(--bg-0)]">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-[var(--bg-0)]">
      {/* Sidebar */}
      <div className="desk-sidebar">
        <div className="px-6 mb-8">
          <Wordmark className="h-6 text-[var(--accent-gold)]" suffix="DESK" />
        </div>
        <nav className="flex flex-col gap-1">
          <Link to="/desk/dashboard">📊 Dashboard</Link>
          <Link to="/desk/inbox">📥 Inbox</Link>
          <div className="mt-auto pt-8">
            <button onClick={logout}>🚪 Sign Out</button>
          </div>
        </nav>
      </div>

      {/* Main */}
      <div className="flex-1 p-8">
        <div className="max-w-4xl mx-auto">
          {/* Back */}
          <Link to="/desk/inbox" className="text-xs text-[var(--text-2)] hover:text-white transition-colors mb-6 inline-block uppercase tracking-widest">
            ← Back to Inbox
          </Link>

          {ticket ? (
            <>
              {/* AI Copilot Panel */}
              <AICopilot ticketId={id} ticketContent={ticket.description} />

              {/* Header */}
              <div className="glass-panel rounded-xl p-6 mb-6">
                <div className="flex items-start justify-between gap-4 mb-4">
                  <h1 className="text-xl font-bold flex-1">{ticket.subject}</h1>
                  <div className="flex items-center gap-2">
                    <span className={`badge badge-${ticket.status}`}>{ticket.status.replace('_', ' ')}</span>
                    <span className={`badge badge-${ticket.priority}`}>{ticket.priority}</span>
                  </div>
                </div>
                <p className="text-[var(--text-1)] text-sm leading-relaxed mb-4">{ticket.description}</p>
                <div className="flex items-center gap-6 text-[10px] text-[var(--text-2)] uppercase tracking-widest border-t border-[var(--glass-border)] pt-4">
                  <span>From: <span className="text-white">{ticket.requester_email}</span></span>
                  <span>Assigned: <span className="text-white">{ticket.assigned_to || 'Unassigned'}</span></span>
                  <span>Created: <span className="text-white">{new Date(ticket.created_at).toLocaleString()}</span></span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 mb-6">
                <span className="text-[10px] uppercase tracking-widest text-[var(--text-2)] mr-2">Status:</span>
                {['accepted', 'in_progress', 'resolved', 'closed'].map(s => (
                  <button key={s} onClick={() => updateStatus(s)}
                    className={`text-[10px] uppercase tracking-widest font-bold px-3 py-1.5 rounded-full transition-all border border-[var(--glass-border)] ${ticket.status === s ? 'bg-[var(--accent-gold)] text-black border-[var(--accent-gold)]' : 'text-[var(--text-2)] hover:text-white hover:bg-white/5'
                      }`}>
                    {s.replace('_', ' ')}
                  </button>
                ))}
              </div>

              {/* Comments */}
              <div className="glass-panel rounded-xl p-6 mb-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">Comments</h2>
                {comments.length === 0 ? (
                  <p className="text-[var(--text-2)] text-sm py-4">No comments yet</p>
                ) : (
                  <div className="space-y-4">
                    {comments.map(c => (
                      <div key={c.id} className="glass-card rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-bold text-white">{c.author_name}</span>
                          <span className="text-[10px] text-[var(--text-2)]">{new Date(c.created_at).toLocaleString()}</span>
                        </div>
                        <p className="text-sm text-[var(--text-1)]">{c.content}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Add Comment */}
              <form onSubmit={addComment} className="glass-panel rounded-xl p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">Add Reply</h2>
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  className="atum-input mb-4"
                  rows={4}
                  placeholder="Type your reply..."
                  style={{ resize: 'vertical' }}
                />
                <button type="submit" className="btn-gold">
                  <span className="btn-bg"></span>
                  <span className="btn-text">Send Reply</span>
                </button>
              </form>
            </>
          ) : (
            <div className="text-center py-16 text-[var(--text-2)]">
              <p>Ticket not found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function AICopilot({ ticketId, ticketContent }) {
  const [suggestions, setSuggestions] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const token = localStorage.getItem('atum_desk_token')

  const fetchSuggestions = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`/api/v1/internal/tickets/${ticketId}/suggestions`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to fetch suggestions')
      setSuggestions(await res.json())
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  if (!suggestions && !loading && !error) {
    return (
      <div className="mb-6">
        <button onClick={fetchSuggestions} className="btn-gold w-full flex items-center justify-center gap-2">
          <span>✨ Analyze with Agent Copilot</span>
        </button>
      </div>
    )
  }

  return (
    <div className="glass-panel rounded-xl p-6 mb-6 border border-[var(--accent-gold)]/30 relative overflow-hidden">
      {loading && <div className="absolute inset-0 bg-black/50 z-10 flex items-center justify-center"><div className="spinner"></div></div>}

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--accent-gold)]">🧠 Agent Copilot</h2>
        {suggestions && (
          <span className={`badge ${suggestions.sentiment?.urgency === 'critical' ? 'badge-urgent' : 'badge-new'}`}>
            {suggestions.sentiment?.urgency} urgency
          </span>
        )}
      </div>

      {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

      {suggestions && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Analysis */}
          <div>
            <h3 className="text-xs uppercase text-[var(--text-2)] mb-2">Analysis</h3>
            <div className="glass-card p-3 mb-2">
              <div className="flex justify-between mb-1">
                <span className="text-[var(--text-1)]">Sentiment:</span>
                <span className="text-white font-bold">{suggestions.sentiment?.sentiment}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--text-1)]">Score:</span>
                <span className="text-white font-bold">{(suggestions.sentiment?.score * 100).toFixed(0)}%</span>
              </div>
              <p className="text-xs text-[var(--text-2)] mt-2 italic">{suggestions.sentiment?.reasoning}</p>
            </div>

            <h3 className="text-xs uppercase text-[var(--text-2)] mb-2 mt-4">Similar Tickets (RAG)</h3>
            {suggestions.similar_tickets?.length > 0 ? (
              <div className="space-y-2">
                {suggestions.similar_tickets.map((t, i) => (
                  <div key={i} className="glass-card p-2 text-xs truncate hover:whitespace-normal cursor-help" title={t.content}>
                    {t.metadata?.ticket_id ? `#${t.metadata.ticket_id} ` : ''}
                    {t.content.substring(0, 60)}...
                  </div>
                ))}
              </div>
            ) : <p className="text-xs text-[var(--text-2)]">No similar tickets found.</p>}
          </div>

          {/* Reply */}
          <div className="flex flex-col h-full">
            <h3 className="text-xs uppercase text-[var(--text-2)] mb-2">Suggested Reply</h3>
            <div className="glass-card p-3 flex-1 bg-white/5 font-mono text-sm text-[var(--text-1)] mb-2">
              {suggestions.reply_suggestion?.content}
            </div>
            <button
              onClick={() => {
                // Find the textarea and set value (Hack via state would be better but component is separate)
                // We can use a callback prop or just copy to clipboard
                navigator.clipboard.writeText(suggestions.reply_suggestion?.content)
                alert("Copied to clipboard!")
              }}
              className="text-xs text-[var(--accent-gold)] hover:underline self-end"
            >
              Copy to Clipboard
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
