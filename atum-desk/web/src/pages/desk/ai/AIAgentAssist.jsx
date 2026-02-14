import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import DeskSidebar from '../../../components/DeskSidebar'

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
      if (res.ok) {
        const data = await res.json()
        setSuggestions(data)
      }
    } catch (e) { console.error(e) }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'priority': return '📌'
      case 'context': return '👤'
      case 'similar_tickets': return '📋'
      case 'canned_response': return '💬'
      case 'knowledge_base': return '📚'
      case 'sla_warning': return '⏰'
      case 'ai_reply': return '🤖'
      default: return '💡'
    }
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
      <div className="flex min-h-screen bg-[var(--bg-0)]">
        <DeskSidebar />
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin h-8 w-8 border-2 border-[var(--accent-gold)] border-t-transparent rounded-full"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-[var(--bg-0)]">
      <DeskSidebar />
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-3">
                <span className="text-3xl">🎯</span>
                Agent Assist
              </h1>
              <p className="text-[var(--text-muted)] mt-1">Real-time AI assistance while handling tickets</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Ticket List */}
            <div className="glass-panel rounded-xl p-4">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">
                Select Ticket
              </h2>
              <div className="space-y-2 max-h-[70vh] overflow-y-auto">
                {tickets.map((ticket) => (
                  <div
                    key={ticket.id}
                    onClick={() => fetchSuggestions(ticket.id)}
                    className={`p-3 rounded-lg border cursor-pointer transition ${
                      selectedTicket === ticket.id 
                        ? 'bg-[var(--accent-gold)]/10 border-[var(--accent-gold)]' 
                        : 'bg-[var(--bg)] border-[var(--border)] hover:border-[var(--accent-gold)]'
                    }`}
                  >
                    <div className="font-medium text-sm truncate">{ticket.subject}</div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`badge badge-${ticket.priority}`}>{ticket.priority}</span>
                      <span className={`badge badge-${ticket.status}`}>{ticket.status.replace('_', ' ')}</span>
                    </div>
                  </div>
                ))}
                {!tickets.length && (
                  <div className="text-center py-8 text-[var(--text-muted)]">No tickets available</div>
                )}
              </div>
            </div>

            {/* Suggestions Panel */}
            <div className="lg:col-span-2 glass-panel rounded-xl p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4 flex items-center gap-2">
                <span>🤖</span> AI Suggestions
              </h2>
              
              {!selectedTicket ? (
                <div className="text-center py-16 text-[var(--text-muted)]">
                  <div className="text-5xl mb-4">🎯</div>
                  <p>Select a ticket to get AI assistance</p>
                </div>
              ) : !suggestions ? (
                <div className="flex items-center justify-center py-16">
                  <div className="animate-spin h-6 w-6 border-2 border-[var(--accent-gold)] border-t-transparent rounded-full"></div>
                </div>
              ) : (
                <div className="space-y-3">
                  {suggestions.suggestions?.map((item, idx) => (
                    <div 
                      key={idx} 
                      className={`p-4 rounded-lg border bg-[var(--bg)] ${getPriorityColor(item.priority)}`}
                    >
                      <div className="flex items-start gap-3">
                        <span className="text-2xl">{getTypeIcon(item.type)}</span>
                        <div className="flex-1">
                          <div className="font-medium mb-1">{item.message}</div>
                          
                          {item.type === 'canned_response' && item.data && (
                            <div className="mt-2 space-y-2">
                              {item.data.map((resp, i) => (
                                <div key={i} className="p-2 bg-[var(--bg-2)] rounded text-sm">
                                  <div className="font-medium">{resp.title}</div>
                                  <div className="text-xs text-[var(--text-muted)] mt-1">{resp.content}</div>
                                </div>
                              ))}
                            </div>
                          )}
                          
                          {item.type === 'knowledge_base' && item.data && (
                            <div className="mt-2 space-y-2">
                              {item.data.map((kb, i) => (
                                <a key={i} href={`/desk/kb/articles/${kb.id}`} className="block p-2 bg-[var(--bg-2)] rounded text-sm hover:text-[var(--accent-gold)]">
                                  <div className="font-medium">📚 {kb.title}</div>
                                </a>
                              ))}
                            </div>
                          )}
                          
                          {item.type === 'similar_tickets' && item.data && (
                            <div className="mt-2 space-y-2">
                              {item.data.map((t, i) => (
                                <div key={i} className="p-2 bg-[var(--bg-2)] rounded text-sm">
                                  <div className="font-medium">#{t.id.slice(0,8)}: {t.subject}</div>
                                </div>
                              ))}
                            </div>
                          )}
                          
                          {item.type === 'ai_reply' && item.data?.suggested_reply && (
                            <div className="mt-2 p-3 bg-[var(--accent-gold)]/10 border border-[var(--accent-gold)] rounded">
                              <div className="text-sm">{item.data.suggested_reply}</div>
                            </div>
                          )}
                          
                          {item.type === 'sla_warning' && (
                            <div className="mt-2 p-2 bg-red-900/20 border border-red-700 rounded text-sm text-red-400">
                              ⚠️ SLA breach imminent - take action!
                            </div>
                          )}
                        </div>
                        <span className={`text-xs px-2 py-1 rounded ${
                          item.priority === 'high' ? 'bg-red-900/50 text-red-400' : 
                          item.priority === 'medium' ? 'bg-orange-900/50 text-orange-400' : 
                          'bg-gray-900/50 text-gray-400'
                        }`}>
                          {item.priority}
                        </span>
                      </div>
                    </div>
                  ))}
                  
                  {!suggestions.suggestions?.length && (
                    <div className="text-center py-8 text-[var(--text-muted)]">
                      <div className="text-3xl mb-2">✨</div>
                      <p>No suggestions for this ticket</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
