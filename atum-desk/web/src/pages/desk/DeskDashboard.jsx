import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Wordmark } from '../../components/Brand/Wordmark'

export default function DeskDashboard() {
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [stats, setStats] = useState({ total: 0, open: 0, resolved: 0, urgent: 0 })
  const [recentTickets, setRecentTickets] = useState([])

  useEffect(() => {
    if (!token) { navigate('/desk/login'); return }
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const res = await fetch('/api/v1/analytics/dashboard', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.status === 401) { navigate('/desk/login'); return }
      if (res.ok) {
        const data = await res.json()
        setRecentTickets(data.recent_tickets || [])
        setStats(data.stats || { total: 0, open: 0, resolved: 0, urgent: 0 })
      }
    } catch (e) { console.error(e) }
  }

  const logout = () => {
    localStorage.removeItem('atum_desk_token')
    localStorage.removeItem('atum_desk_refresh')
    navigate('/desk/login')
  }

  return (
    <div className="flex min-h-screen bg-[var(--bg-0)]">
      {/* Sidebar */}
      <div className="desk-sidebar">
        <div className="px-6 mb-8">
          <Wordmark className="h-6 text-[var(--accent-gold)]" suffix="DESK" />
        </div>
        <nav className="flex flex-col gap-1">
          <Link to="/desk/dashboard" className="active">📊 Dashboard</Link>
          <Link to="/desk/inbox">📥 Inbox</Link>
          <div className="mt-auto pt-8">
            <button onClick={logout}>🚪 Sign Out</button>
          </div>
        </nav>
      </div>

      {/* Main */}
      <div className="flex-1 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-2xl font-bold">Dashboard</h1>
            <span className="text-[10px] uppercase tracking-widest text-[var(--text-2)]">ATUM DESK v1.0.0</span>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
            <div className="stat-card">
              <div className="stat-value">{stats.total}</div>
              <div className="stat-label">Total Tickets</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-[#fbbf24]">{stats.open}</div>
              <div className="stat-label">Open</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-[#34d399]">{stats.resolved}</div>
              <div className="stat-label">Resolved</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-[#f87171]">{stats.urgent}</div>
              <div className="stat-label">Urgent</div>
            </div>
          </div>

          {/* Recent Tickets */}
          <div className="glass-panel rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)]">Recent Tickets</h2>
              <Link to="/desk/inbox" className="text-[10px] uppercase tracking-widest text-[var(--accent-gold)] hover:text-white transition-colors">
                View All →
              </Link>
            </div>
            {recentTickets.length === 0 ? (
              <div className="text-center py-12 text-[var(--text-2)]">
                <div className="text-3xl mb-3">📭</div>
                <p className="text-sm">No tickets yet</p>
              </div>
            ) : (
              <table className="atum-table">
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {recentTickets.map(ticket => (
                    <tr key={ticket.id} onClick={() => navigate(`/desk/tickets/${ticket.id}`)}>
                      <td className="font-medium text-white">{ticket.subject}</td>
                      <td><span className={`badge badge-${ticket.status}`}>{ticket.status.replace('_', ' ')}</span></td>
                      <td><span className={`badge badge-${ticket.priority}`}>{ticket.priority}</span></td>
                      <td className="text-xs">{new Date(ticket.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
