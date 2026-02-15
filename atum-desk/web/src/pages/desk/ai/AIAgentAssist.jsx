import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageShell, GlassCard } from '../../../components/Premium'
import { Target, Bot, Pin, User, Copy, BookOpen, Clock, AlertTriangle, Sparkles } from 'lucide-react'

export default function AIAgentAssist() {
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [tickets, setTickets] = useState([])
  const [selectedTicket, setSelectedTicket] = useState(null)
  const [suggestions, setSuggestions] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) { navigate('/desk/login'); return }
    fetchTickets()
  }, [])

  const fetchTickets = async () => {
    try {
      const res = await fetch('/api/v1/tickets', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.status === 401) { navigate('/desk/login'); return }
      if (res.ok) {
        const data = await res.json()
        setTickets(data.slice(0, 20))
      }
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const fetchSuggestions = async (ticketId) => {
    setSelectedTicket(ticketId)
    try {
      const res = await fetch(`/api/v1/ai/agent-assist/${ticketId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) setSuggestions(await res.json())
    } catch (e) { console.error(e) }
  }

  const getTypeIcon = (type) => {
    const icons = {
      priority: Pin, context: User, similar_tickets: Copy,
      canned_response: Copy, knowledge_base: BookOpen,
      sla_warning: Clock, ai_reply: Bot
    }
    const Icon = icons[type] || Sparkles
    return <Icon size={20} />
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-400 border-red-700'
      case 'medium': return 'text-orange-400 border-orange-700'
      default: return 'text-gray-400 border-gray-700'
    }
  }

  if (loading) {
    return (
      <PageShell title="Agent Assist" subtitle="Loading...">
        <div className="flex items-center justify-center py-24">
          <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
        </div>
      </PageShell>
    )
  }

  return (
    <PageShell title="Agent Assist" subtitle="Real-time AI assistance while handling tickets">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Ticket List */}
        <GlassCard>
          <div className="p-4">
            <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">Select Ticket</h2>
            <div className="space-y-2 max-h-[70vh] overflow-y-auto">
              {tickets.map((ticket) => (
                <div key={ticket.id} onClick={() => fetchSuggestions(ticket.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${selectedTicket === ticket.id
                      ? 'bg-[var(--atum-accent-gold)]/10 border-[var(--atum-accent-gold)]'
                      : 'bg-[var(--atum-bg)] border-[var(--atum-border)] hover:border-[var(--atum-accent-gold)]'
                    }`}>
                  <div className="font-medium text-sm truncate">{ticket.subject}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`badge badge-${ticket.priority}`}>{ticket.priority}</span>
                    <span className={`badge badge-${ticket.status}`}>{ticket.status.replace('_', ' ')}</span>
                  </div>
                </div>
              ))}
              {!tickets.length && (
                <div className="text-center py-8 text-[var(--atum-text-muted)]">No tickets available</div>
              )}
            </div>
          </div>
        </GlassCard>

        {/* Suggestions Panel */}
        <div className="lg:col-span-2">
          <GlassCard>
            <div className="p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4 flex items-center gap-2">
                <Bot size={16} /> AI Suggestions
              </h2>
              {!selectedTicket ? (
                <div className="text-center py-16 text-[var(--atum-text-muted)]">
                  <Target size={48} className="mx-auto mb-4 opacity-20" />
                  <p>Select a ticket to get AI assistance</p>
                </div>
              ) : !suggestions ? (
                <div className="flex items-center justify-center py-16">
                  <div className="w-6 h-6 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : (
                <div className="space-y-3">
                  {suggestions.suggestions?.map((item, idx) => (
                    <div key={idx} className={`p-4 rounded-lg border bg-[var(--atum-bg)] ${getPriorityColor(item.priority)}`}>
                      <div className="flex items-start gap-3">
                        <span className="text-[var(--atum-text-muted)] mt-0.5">{getTypeIcon(item.type)}</span>
                        <div className="flex-1">
                          <div className="font-medium mb-1">{item.message}</div>
                          {item.type === 'canned_response' && item.data && (
                            <div className="mt-2 space-y-2">
                              {item.data.map((resp, i) => (
                                <div key={i} className="p-2 bg-[var(--atum-bg-2)] rounded text-sm">
                                  <div className="font-medium">{resp.title}</div>
                                  <div className="text-xs text-[var(--atum-text-muted)] mt-1">{resp.content}</div>
                                </div>
                              ))}
                            </div>
                          )}
                          {item.type === 'knowledge_base' && item.data && (
                            <div className="mt-2 space-y-2">
                              {item.data.map((kb, i) => (
                                <a key={i} href={`/desk/kb/articles/${kb.id}`}
                                  className="flex items-center gap-2 p-2 bg-[var(--atum-bg-2)] rounded text-sm hover:text-[var(--atum-accent-gold)]">
                                  <BookOpen size={14} /> {kb.title}
                                </a>
                              ))}
                            </div>
                          )}
                          {item.type === 'similar_tickets' && item.data && (
                            <div className="mt-2 space-y-2">
                              {item.data.map((t, i) => (
                                <div key={i} className="p-2 bg-[var(--atum-bg-2)] rounded text-sm">
                                  <div className="font-medium">#{t.id.slice(0, 8)}: {t.subject}</div>
                                </div>
                              ))}
                            </div>
                          )}
                          {item.type === 'ai_reply' && item.data?.suggested_reply && (
                            <div className="mt-2 p-3 bg-[var(--atum-accent-gold)]/10 border border-[var(--atum-accent-gold)] rounded">
                              <div className="text-sm">{item.data.suggested_reply}</div>
                            </div>
                          )}
                          {item.type === 'sla_warning' && (
                            <div className="mt-2 p-2 bg-red-900/20 border border-red-700 rounded text-sm text-red-400 flex items-center gap-2">
                              <AlertTriangle size={14} /> SLA breach imminent - take action!
                            </div>
                          )}
                        </div>
                        <span className={`text-xs px-2 py-1 rounded ${item.priority === 'high' ? 'bg-red-900/50 text-red-400' :
                            item.priority === 'medium' ? 'bg-orange-900/50 text-orange-400' :
                              'bg-gray-900/50 text-gray-400'
                          }`}>{item.priority}</span>
                      </div>
                    </div>
                  ))}
                  {!suggestions.suggestions?.length && (
                    <div className="text-center py-8 text-[var(--atum-text-muted)]">
                      <Sparkles size={32} className="mx-auto mb-2 opacity-20" />
                      <p>No suggestions for this ticket</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </GlassCard>
        </div>
      </div>
    </PageShell>
  )
}
