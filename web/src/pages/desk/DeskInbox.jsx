import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Wordmark } from '../../components/Brand/Wordmark'

export default function DeskInbox() {
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [tickets, setTickets] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) { navigate('/desk/login'); return }
    fetchTickets()
  }, [])

  const fetchTickets = async () => {
    try {
      const res = await fetch('/api/v1/internal/tickets', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.status === 401) { navigate('/desk/login'); return }
      if (res.ok) {
        const data = await res.json()
        setTickets(Array.isArray(data) ? data : [])
      }
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const logout = () => {
    localStorage.removeItem('atum_desk_token')
    localStorage.removeItem('atum_desk_refresh')
    navigate('/desk/login')
  }

  const filtered = filter === 'all' ? tickets :
    tickets.filter(t => filter === 'open'
      ? ['new', 'accepted', 'assigned', 'in_progress'].includes(t.status)
      : t.status === filter
    )

  const filters = [
    { key: 'all', label: 'All' },
    { key: 'open', label: 'Open' },
    { key: 'resolved', label: 'Resolved' },
    { key: 'closed', label: 'Closed' },
  ]

  return (
    <div className="flex min-h-screen bg-[var(--bg-0)]">
      {/* Sidebar */}
      <div className="desk-sidebar">
        <div className="px-6 mb-8">
          <Wordmark className="h-6 text-[var(--accent-gold)]" suffix="DESK" />
        </div>
        <nav className="flex flex-col gap-1">
          <Link to="/desk/dashboard">📊 Dashboard</Link>
          <Link to="/desk/inbox" className="active">📥 Inbox</Link>
          <div className="mt-auto pt-8">
            <button onClick={logout}>🚪 Sign Out</button>
          </div>
        </nav>
      </div>

      {/* Main */}
      <div className="flex-1 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-2xl font-bold">Inbox</h1>
            <div className="flex items-center gap-2">
              {filters.map(f => (
                <button
                  key={f.key}
                  onClick={() => setFilter(f.key)}
                  className={`text-[10px] uppercase tracking-widest font-bold px-3 py-1.5 rounded-full transition-all ${filter === f.key
                      ? 'bg-[var(--accent-gold)] text-black'
                      : 'text-[var(--text-2)] hover:text-white hover:bg-white/5 border border-[var(--glass-border)]'
                    }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          <div className="glass-panel rounded-xl p-6">
            {loading ? (
              <div className="flex items-center justify-center py-16">
                <div className="spinner"></div>
              </div>
            ) : filtered.length === 0 ? (
              <div className="text-center py-16 text-[var(--text-2)]">
                <div className="text-4xl mb-3">📭</div>
                <p className="text-sm">No tickets found</p>
              </div>
            ) : (
              <table className="atum-table">
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Requester</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Assigned</th>
                    <th>Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(ticket => (
                    <tr key={ticket.id} onClick={() => navigate(`/desk/tickets/${ticket.id}`)}>
                      <td className="font-medium text-white max-w-[300px] truncate">{ticket.subject}</td>
                      <td className="text-xs">{ticket.requester_email || '—'}</td>
                      <td><span className={`badge badge-${ticket.status}`}>{ticket.status.replace('_', ' ')}</span></td>
                      <td><span className={`badge badge-${ticket.priority}`}>{ticket.priority}</span></td>
                      <td className="text-xs">{ticket.assigned_to || '—'}</td>
                      <td className="text-xs">{new Date(ticket.updated_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="mt-4 text-[10px] text-[var(--text-2)] uppercase tracking-widest">
            {filtered.length} ticket{filtered.length !== 1 ? 's' : ''}
          </div>
        </div>
      </div>
    </div>
  )
}
