import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { PageShell, GlassCard } from '../../components/Premium'
import { Inbox, CheckCircle, AlertCircle, Clock, Filter, Search, User } from 'lucide-react'
import DensityToggle from '../../components/DensityToggle'

export default function DeskInbox() {
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [tickets, setTickets] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [density, setDensity] = useState('default')

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


  const filtered = filter === 'all' ? tickets :
    tickets.filter(t => filter === 'open'
      ? ['new', 'accepted', 'assigned', 'in_progress'].includes(t.status)
      : t.status === filter
    )

  const filters = [
    { key: 'all', label: 'All Tickets', icon: Inbox },
    { key: 'open', label: 'Open', icon: Clock },
    { key: 'resolved', label: 'Resolved', icon: CheckCircle },
    { key: 'urgent', label: 'Urgent', icon: AlertCircle },
  ]

  return (
    <PageShell
      title="Inbox"
      subtitle="Manage and respond to customer tickets"
      actions={
        <div className="flex gap-2">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--atum-text-muted)]" />
            <input
              type="text"
              placeholder="Search tickets..."
              className="pl-9 pr-4 py-2 bg-[var(--atum-surface)] border border-[var(--atum-border)] rounded-full text-sm focus:outline-none focus:border-[var(--atum-accent-gold)] w-64 transition-colors"
            />
          </div>
          <button className="btn-gold flex items-center gap-2">
            <Filter size={16} /> <span>Filter</span>
          </button>
          <DensityToggle value={density} onChange={setDensity} />
        </div>
      }
    >
      {/* Filters (Tabs Style) */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2 scrollbar-hide">
        {filters.map(f => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all border ${filter === f.key
              ? 'bg-[var(--atum-accent-gold)] text-black border-[var(--atum-accent-gold)] shadow-[0_0_15px_rgba(217,181,90,0.3)]'
              : 'bg-[var(--atum-surface)] border-[var(--atum-border)] text-[var(--atum-text-muted)] hover:text-white hover:border-[var(--atum-border-strong)]'
              }`}
          >
            <f.icon size={14} /> {f.label}
          </button>
        ))}
      </div>

      <GlassCard className="p-0 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-24">
            <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-24 text-[var(--atum-text-muted)]">
            <Inbox size={48} className="mx-auto mb-4 opacity-20" />
            <p className="text-sm">No tickets found matching this filter</p>
          </div>
        ) : (
          <table className={`w-full text-left border-collapse ${density === 'compact' ? 'density-compact' : ''}`}>
            <thead>
              <tr className="border-b border-[var(--atum-border)] text-xs uppercase tracking-wider text-[var(--atum-text-muted)]">
                <th className="p-4 font-semibold">Subject</th>
                <th className="p-4 font-semibold">Requester</th>
                <th className="p-4 font-semibold">Status</th>
                <th className="p-4 font-semibold">Priority</th>
                <th className="p-4 font-semibold">Assignee</th>
                <th className="p-4 font-semibold">Updated</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--atum-border)]">
              {filtered.map(ticket => (
                <tr
                  key={ticket.id}
                  onClick={() => navigate(`/desk/tickets/${ticket.id}`)}
                  className="group hover:bg-[var(--atum-glass-hover)] transition-colors cursor-pointer"
                >
                  <td className="p-4">
                    <div className="font-medium text-white group-hover:text-[var(--atum-accent-gold)] transition-colors line-clamp-1">
                      {ticket.subject}
                    </div>
                    <div className="text-xs text-[var(--atum-text-muted)] mt-0.5">#{ticket.id.slice(0, 8)}</div>
                  </td>
                  <td className="p-4 text-sm text-[var(--atum-text-1)]">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-[var(--atum-surface-2)] flex items-center justify-center text-[10px]">
                        {ticket.requester_email?.[0].toUpperCase()}
                      </div>
                      {ticket.requester_email}
                    </div>
                  </td>
                  <td className="p-4"><span className={`badge badge-${ticket.status}`}>{ticket.status?.replace('_', ' ')}</span></td>
                  <td className="p-4"><span className={`badge badge-${ticket.priority}`}>{ticket.priority}</span></td>
                  <td className="p-4 text-sm text-[var(--atum-text-muted)]">{ticket.assigned_to || '—'}</td>
                  <td className="p-4 text-xs text-[var(--atum-text-muted)] font-mono">{new Date(ticket.updated_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </GlassCard>
    </PageShell>
  )
}
