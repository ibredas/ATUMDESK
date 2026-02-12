import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Wordmark } from '../../components/Brand/Wordmark'

export default function PortalTickets() {
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) { navigate('/portal/login'); return }
    fetchTickets()
  }, [])

  const fetchTickets = async () => {
    try {
      const res = await fetch('/api/v1/tickets', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.status === 401) { navigate('/portal/login'); return }
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
    navigate('/portal/login')
  }

  return (
    <div className="min-h-screen bg-[var(--bg-0)]">
      <div className="grain-overlay"></div>
      {/* Header */}
      <nav className="relative z-50 flex items-center justify-between px-6 py-4 border-b border-[var(--glass-border)] backdrop-blur-sm">
        <Wordmark className="h-6 text-[#60a5fa]" suffix="PORTAL" />
        <div className="flex items-center gap-3">
          <Link to="/portal/tickets/new" className="btn-outline" style={{ borderColor: 'rgba(59,130,246,0.3)', color: '#60a5fa' }}>
            + New Ticket
          </Link>
          <button onClick={logout} className="text-[10px] uppercase tracking-widest text-[var(--text-2)] hover:text-red-400 transition-colors">
            Sign Out
          </button>
        </div>
      </nav>

      <div className="relative z-10 max-w-4xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-6">My Tickets</h1>

        <div className="glass-panel rounded-xl p-6">
          {loading ? (
            <div className="flex items-center justify-center py-16"><div className="spinner"></div></div>
          ) : tickets.length === 0 ? (
            <div className="text-center py-16 text-[var(--text-2)]">
              <div className="text-4xl mb-3">🎫</div>
              <p className="text-sm mb-4">No tickets yet</p>
              <Link to="/portal/tickets/new" className="btn-outline" style={{ borderColor: 'rgba(59,130,246,0.3)', color: '#60a5fa' }}>
                Submit a Ticket
              </Link>
            </div>
          ) : (
            <table className="atum-table">
              <thead>
                <tr><th>Subject</th><th>Status</th><th>Priority</th><th>Updated</th></tr>
              </thead>
              <tbody>
                {tickets.map(t => (
                  <tr key={t.id} onClick={() => navigate(`/portal/tickets/${t.id}`)}>
                    <td className="font-medium text-white">{t.subject}</td>
                    <td><span className={`badge badge-${t.status}`}>{t.status.replace('_', ' ')}</span></td>
                    <td><span className={`badge badge-${t.priority}`}>{t.priority}</span></td>
                    <td className="text-xs">{new Date(t.updated_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}
