import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { Wordmark } from '../../components/Brand/Wordmark'

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
    return <div className="flex items-center justify-center min-h-screen bg-[var(--bg-0)]"><div className="spinner"></div></div>
  }

  return (
    <div className="min-h-screen bg-[var(--bg-0)]">
      <div className="grain-overlay"></div>
      <nav className="relative z-50 flex items-center justify-between px-6 py-4 border-b border-[var(--glass-border)] backdrop-blur-sm">
        <Wordmark className="h-6 text-[#60a5fa]" suffix="PORTAL" />
        <Link to="/portal/tickets" className="text-[10px] uppercase tracking-widest text-[var(--text-2)] hover:text-white transition-colors">
          ← My Tickets
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
              <p className="text-[var(--text-1)] text-sm leading-relaxed mb-4">{ticket.description}</p>
              <div className="text-[10px] text-[var(--text-2)] uppercase tracking-widest border-t border-[var(--glass-border)] pt-4">
                Created: {new Date(ticket.created_at).toLocaleString()}
              </div>
            </div>

            <div className="glass-panel rounded-xl p-6 mb-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">Conversation</h2>
              {comments.length === 0 ? (
                <p className="text-[var(--text-2)] text-sm py-4">No replies yet</p>
              ) : (
                <div className="space-y-4">
                  {comments.map(c => (
                    <div key={c.id} className="glass-card rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-white">{c.author_name} {c.is_ai_generated && '🤖'}</span>
                        <span className="text-[10px] text-[var(--text-2)]">{new Date(c.created_at).toLocaleString()}</span>
                      </div>
                      <p className="text-sm text-[var(--text-1)]">{c.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <form onSubmit={addComment} className="glass-panel rounded-xl p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">Reply</h2>
              <textarea value={newComment} onChange={(e) => setNewComment(e.target.value)}
                className="atum-input mb-4" rows={3} placeholder="Type your reply..." style={{ resize: 'vertical' }} />
              <button type="submit"
                className="py-3 px-6 rounded-lg bg-[#3b82f6] text-white font-bold text-sm tracking-wide transition-all hover:bg-[#2563eb] border border-blue-500/30">
                Send Reply
              </button>
            </form>
          </>
        ) : (
          <div className="text-center py-16 text-[var(--text-2)]"><p>Ticket not found</p></div>
        )}
      </div>
    </div>
  )
}
