import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { PageShell, GlassCard } from '../../components/Premium'
import { ChevronLeft, User, Clock, Tag, MessageSquare, Check, X, Send, Sparkles } from 'lucide-react'

// Mocking AICopilot import if it doesn't exist yet, but assumes it does from Step 3928
// Function AICopilot is likely defined in the file or imported. 
// CHECK: DeskTicketDetail.jsx had it inline. I need to replicate that or extract it.
// CRITICAL: Since I am overwriting the file, if AICopilot was inline, I MUST Preserve it.
// I will verify if I can import it or if I need to copy-paste it.
// Previous view_file showed it was INLINE. I MUST COPY PASTE IT.

// ... (AICopilot Code from previous context) ...
// ACTUALLY: Best practice is to extract it to a component file so user can reuse it. 
// BUT instructions say "DO NOT change existing routes, API calls...". Extracting is a refactor.
// I will include it inline to be safe and fast.

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

  if (loading) return null

  return (
    <PageShell
      title={ticket ? ticket.subject : 'Loading...'}
      subtitle={ticket ? `#${ticket.id}` : ''}
      actions={
        <Link to="/desk/inbox" className="text-sm text-[var(--atum-text-muted)] hover:text-white flex items-center gap-1">
          <ChevronLeft size={16} /> Back to Inbox
        </Link>
      }
    >
      {ticket ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Status & Priority Header */}
            <div className="flex gap-2">
              <span className={`badge badge-${ticket.status}`}>{ticket.status.replace('_', ' ')}</span>
              <span className={`badge badge-${ticket.priority}`}>{ticket.priority}</span>
            </div>

            <AICopilot ticketId={id} ticketContent={ticket.description} onDraftApplied={() => fetchComments()} />

            <GlassCard title="Ticket Description">
              <div className="prose prose-invert max-w-none text-sm text-[var(--atum-text)] leading-relaxed whitespace-pre-wrap">
                {ticket.description}
              </div>
            </GlassCard>

            <GlassCard title={`Comments (${comments.length})`}>
              <div className="space-y-6">
                {comments.map(c => (
                  <div key={c.id} className="flex gap-4 group">
                    <div className="w-8 h-8 rounded-full bg-[var(--atum-surface)] flex items-center justify-center border border-[var(--atum-border)] flex-shrink-0">
                      <User size={14} className="text-[var(--atum-text-muted)]" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-baseline justify-between mb-1">
                        <span className="font-semibold text-sm text-white">{c.author_name}</span>
                        <span className="text-xs text-[var(--atum-text-dim)]">{new Date(c.created_at).toLocaleString()}</span>
                      </div>
                      <div className="p-3 bg-[var(--atum-surface)] rounded-[var(--atum-radius-md)] border border-[var(--atum-border)] text-sm text-[var(--atum-text-muted)] group-hover:bg-[var(--atum-surface-2)] transition-colors">
                        {c.content}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Reply Box */}
              <form onSubmit={addComment} className="mt-8 pt-6 border-t border-[var(--atum-border)]">
                <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2"><MessageSquare size={16} /> Add Reply</h4>
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  className="atum-input min-h-[120px] mb-4 font-sans text-sm"
                  placeholder="Type your reply here..."
                />
                <div className="flex justify-end">
                  <button type="submit" className="btn-gold flex items-center gap-2">
                    <Send size={16} /> Send Reply
                  </button>
                </div>
              </form>
            </GlassCard>
          </div>

          {/* Right: Sidebar */}
          <div className="space-y-6">
            <GlassCard title="Details">
              <div className="space-y-4">
                <div>
                  <div className="text-xs text-[var(--atum-text-dim)] uppercase tracking-wider mb-1">Requester</div>
                  <div className="flex items-center gap-2 text-sm text-white font-medium">
                    <User size={16} className="text-[var(--atum-accent-gold)]" />
                    {ticket.requester_email}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-[var(--atum-text-dim)] uppercase tracking-wider mb-1">Assigned To</div>
                  <div className="flex items-center gap-2 text-sm text-[var(--atum-text-muted)]">
                    {ticket.assigned_to ? (
                      <><User size={16} /> {ticket.assigned_to}</>
                    ) : (
                      <span className="text-[var(--atum-text-dim)] italic">Unassigned</span>
                    )}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-[var(--atum-text-dim)] uppercase tracking-wider mb-1">Created</div>
                  <div className="flex items-center gap-2 text-sm text-[var(--atum-text-muted)]">
                    <Clock size={16} />
                    {new Date(ticket.created_at).toLocaleString()}
                  </div>
                </div>
              </div>
            </GlassCard>

            <GlassCard title="Actions">
              <div className="grid grid-cols-2 gap-2">
                {['accepted', 'in_progress', 'resolved', 'closed'].map(s => (
                  <button
                    key={s}
                    onClick={() => updateStatus(s)}
                    className={`px-3 py-2 rounded text-xs font-bold uppercase tracking-wider border transition-all ${ticket.status === s
                      ? 'bg-[var(--atum-accent-gold)] border-[var(--atum-accent-gold)] text-black'
                      : 'bg-transparent border-[var(--atum-border)] text-[var(--atum-text-muted)] hover:bg-[var(--atum-surface)] hover:text-white'
                      }`}
                  >
                    {s.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </GlassCard>
          </div>
        </div>
      ) : (
        <div className="text-center py-20 text-[var(--atum-text-muted)]">Ticket not found</div>
      )}
    </PageShell>
  )
}

function AICopilot({ ticketId, ticketContent, onDraftApplied }) {
  const [suggestions, setSuggestions] = useState(null)
  const [triage, setTriage] = useState(null)
  const [smartReplies, setSmartReplies] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [triageApplied, setTriageApplied] = useState(false)
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

    // Fetch triage data (Gap 5)
    try {
      const res = await fetch(`/api/v1/ai/tickets/${ticketId}/triage`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) setTriage(await res.json())
    } catch (e) { /* triage may not exist yet */ }

    // Fetch smart replies (Gap 6)
    try {
      const res = await fetch(`/api/v1/ai/tickets/${ticketId}/smart-replies`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setSmartReplies(Array.isArray(data) ? data : data.items || [])
      }
    } catch (e) { /* smart replies may not exist yet */ }

    setLoading(false)
  }

  // Gap 5: Apply triage to ticket
  const applyTriage = async () => {
    try {
      const res = await fetch(`/api/v1/internal/tickets/${ticketId}/apply-triage`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: triage?.suggested_category,
          priority: triage?.suggested_priority,
          tags: triage?.suggested_tags
        })
      })
      if (res.ok) {
        setTriageApplied(true)
        // Fallback: if no dedicated endpoint, try direct update
      } else {
        // Direct update fallback
        await fetch(`/api/v1/internal/tickets/${ticketId}`, {
          method: 'PATCH',
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            category: triage?.suggested_category,
            priority: triage?.suggested_priority,
            tags: triage?.suggested_tags
          })
        })
        setTriageApplied(true)
      }
    } catch (e) { alert('Failed to apply triage: ' + e.message) }
  }

  // Gap 6: Use draft as comment
  const useDraft = async (content) => {
    try {
      await fetch(`/api/v1/comments/ticket/${ticketId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, is_internal: false })
      })
      alert('Draft applied as reply!')
      if (onDraftApplied) onDraftApplied()
    } catch (e) { alert('Failed: ' + e.message) }
  }

  if (!suggestions && !loading && !error) {
    return (
      <div className="mb-6">
        <button onClick={fetchSuggestions} className="w-full py-4 rounded-xl border border-[var(--atum-border)] border-dashed text-[var(--atum-accent-gold)] bg-[var(--atum-surface)] hover:bg-[var(--atum-surface-2)] transition-colors flex items-center justify-center gap-2 font-semibold">
          <Sparkles size={16} /> Analyze with Agent Copilot
        </button>
      </div>
    )
  }

  return (
    <GlassCard className="mb-6 border-[var(--atum-accent-gold)] border-opacity-30 relative overflow-hidden bg-gradient-to-br from-[var(--atum-surface)] to-[rgba(217,181,90,0.03)]">
      {loading && <div className="absolute inset-0 bg-black/50 z-10 flex items-center justify-center"><div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div></div>}

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-accent-gold)] flex items-center gap-2">
          <Brain size={16} /> Agent Copilot
        </h2>
        {suggestions && (
          <span className={`badge ${suggestions.sentiment?.urgency === 'critical' ? 'badge-urgent' : 'badge-new'}`}>
            {suggestions.sentiment?.urgency} urgency
          </span>
        )}
      </div>

      {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

      {/* Gap 5: AI Triage Panel */}
      {triage && (
        <div className="glass-card bg-[rgba(0,0,0,0.2)] p-4 mb-4 border border-[var(--atum-border)] rounded-lg">
          <h3 className="text-[10px] uppercase text-[var(--atum-text-muted)] mb-3 font-bold tracking-wider">Recommended Triage</h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-3">
            <div><span className="text-[10px] text-[var(--atum-text-dim)] block mb-1">Category</span> <span className="text-sm font-medium text-white">{triage.suggested_category || '—'}</span></div>
            <div><span className="text-[10px] text-[var(--atum-text-dim)] block mb-1">Priority</span> <span className={`badge badge-${triage.suggested_priority}`}>{triage.suggested_priority || '—'}</span></div>
            <div>
              <span className="text-[10px] text-[var(--atum-text-dim)] block mb-1">Sentiment</span>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-1.5 bg-[var(--atum-surface)] rounded-full overflow-hidden w-16">
                  <div className="bg-[var(--atum-accent-gold)] h-full" style={{ width: `${(triage.sentiment_score || 0) * 100}%` }}></div>
                </div>
                <span className="text-xs text-white">{((triage.sentiment_score || 0) * 100).toFixed(0)}%</span>
              </div>
            </div>
            <div><span className="text-[10px] text-[var(--atum-text-dim)] block mb-1">Intent</span> <span className="text-sm text-white">{triage.intent_label}</span></div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-[var(--atum-border)] border-opacity-50">
            <div className="flex gap-1">
              {triage.suggested_tags?.map((tag, i) => <span key={i} className="text-[10px] bg-[var(--atum-surface)] px-2 py-1 rounded text-[var(--atum-text-muted)]">#{tag}</span>)}
            </div>
            {!triageApplied ? (
              <button onClick={applyTriage} className="text-xs bg-[var(--atum-accent-gold)] text-black px-3 py-1.5 rounded font-bold hover:brightness-110 transition-all flex items-center gap-1">
                <Check size={12} /> Apply Triage
              </button>
            ) : (
              <span className="text-xs text-[var(--atum-success)] font-bold flex items-center gap-1"><Check size={12} /> Applied</span>
            )}
          </div>
        </div>
      )}

      {suggestions && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Analysis */}
          <div>
            <h3 className="text-[10px] uppercase text-[var(--atum-text-muted)] mb-3 font-bold tracking-wide">Context & RAG</h3>
            <div className="glass-card bg-[rgba(0,0,0,0.2)] p-4 mb-3">
              <div className="flex justify-between mb-2">
                <span className="text-[var(--atum-text-muted)] text-sm">Sentiment Analysis</span>
                <span className="text-white font-bold">{suggestions.sentiment?.sentiment}</span>
              </div>
              <p className="text-xs text-[var(--atum-text-dim)] italic border-l-2 border-[var(--atum-accent-gold)] pl-3">
                "{suggestions.sentiment?.reasoning}"
              </p>
            </div>

            <h3 className="text-[10px] uppercase text-[var(--atum-text-muted)] mb-2 mt-4 font-bold tracking-wide">Similar Tickets</h3>
            {suggestions.similar_tickets?.length > 0 ? (
              <div className="space-y-2">
                {suggestions.similar_tickets.map((t, i) => (
                  <div key={i} className="glass-card p-3 text-xs text-[var(--atum-text-muted)] truncate hover:whitespace-normal cursor-help hover:text-white transition-colors border-l-2 border-transparent hover:border-l-[var(--atum-accent-gold)]">
                    <span className="font-mono text-[var(--atum-accent-gold-2)] mr-2">#{t.metadata?.ticket_id}</span>
                    {t.content.substring(0, 60)}...
                  </div>
                ))}
              </div>
            ) : <p className="text-xs text-[var(--atum-text-dim)]">No similar tickets found.</p>}
          </div>

          {/* Reply */}
          <div className="flex flex-col h-full">
            <h3 className="text-[10px] uppercase text-[var(--atum-text-muted)] mb-3 font-bold tracking-wide">Suggested Response</h3>
            <div className="glass-card p-4 flex-1 bg-[rgba(0,0,0,0.3)] font-mono text-xs text-[var(--atum-text-muted)] mb-3 border-[var(--atum-border-strong)] leading-relaxed">
              {suggestions.reply_suggestion?.content}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => useDraft(suggestions.reply_suggestion?.content)}
                className="flex-1 text-xs bg-[rgba(46,229,157,0.1)] text-[var(--atum-success)] hover:bg-[rgba(46,229,157,0.2)] px-3 py-2 rounded transition-colors font-bold border border-[var(--atum-success)] border-opacity-30 flex items-center justify-center gap-2"
              >
                <Send size={12} /> Use this Draft
              </button>
              <button
                onClick={() => { navigator.clipboard.writeText(suggestions.reply_suggestion?.content); }}
                className="text-xs text-[var(--atum-text-muted)] hover:text-white px-3 py-2"
                title="Copy to clipboard"
              >
                Copy
              </button>
            </div>

            {/* Gap 6: Smart Reply Drafts */}
            {smartReplies.length > 0 && (
              <div className="mt-4 pt-4 border-t border-[var(--atum-border)]">
                <h3 className="text-[10px] uppercase text-[var(--atum-text-muted)] mb-2 font-bold tracking-wide">Alternative Drafts</h3>
                <div className="space-y-2">
                  {smartReplies.slice(0, 2).map((reply, i) => (
                    <div key={reply.id || i} className="glass-card p-2 flex items-center justify-between group">
                      <p className="text-xs text-[var(--atum-text-dim)] truncate pr-4 max-w-[200px]">{reply.content}</p>
                      <button onClick={() => useDraft(reply.content)} className="opacity-0 group-hover:opacity-100 transition-opacity text-[10px] bg-[var(--atum-surface)] text-[var(--atum-accent-gold)] px-2 py-1 rounded font-bold hover:bg-[var(--atum-accent-gold)] hover:text-black">Use</button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </GlassCard>
  )
}
