import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { PageShell, GlassCard } from '../../components/Premium'
import { Ticket, AlertCircle, CheckCircle, Clock, Database, Brain, Activity } from 'lucide-react'
import MiniSparkline from '../../components/MiniSparkline'

export default function DeskDashboard() {
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [stats, setStats] = useState({ total: 0, open: 0, resolved: 0, urgent: 0 })
  const [recentTickets, setRecentTickets] = useState([])
  const [widgets, setWidgets] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) { navigate('/desk/login'); return }
    fetchData()
    const interval = setInterval(fetchWidgets, 30000)
    return () => clearInterval(interval)
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
    await fetchWidgets()
    setLoading(false)
  }

  const fetchWidgets = async () => {
    try {
      const res = await fetch('/api/v1/metrics/dashboard', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) setWidgets(await res.json())
    } catch (e) { /* best effort */ }
  }

  if (loading) return null

  return (
    <PageShell
      title="Dashboard"
      subtitle="Overview of your service desk operations"
      actions={
        <Link to="/desk/inbox" className="btn-gold shadow-lg shadow-amber-900/20 flex items-center gap-2">
          <Ticket size={16} /> <span>New Ticket</span>
        </Link>
      }
    >
      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <GlassCard className="relative overflow-hidden group">
          <div className="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <Ticket size={80} />
          </div>
          <div className="text-[var(--atum-text-muted)] text-xs font-semibold uppercase tracking-wider mb-1">Total Tickets</div>
          <div className="flex items-end gap-3">
            <div className="text-3xl font-bold text-white">{stats.total}</div>
            <MiniSparkline data={[12, 19, 14, 25, 22, 30, stats.total || 28]} color="var(--atum-accent-gold)" />
          </div>
          <div className="text-xs text-[var(--atum-success)] flex items-center gap-1 mt-2">
            <Activity size={12} /> +12% this week
          </div>
        </GlassCard>

        <GlassCard className="relative overflow-hidden group">
          <div className="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <Clock size={80} />
          </div>
          <div className="text-[var(--atum-text-muted)] text-xs font-semibold uppercase tracking-wider mb-1">Open</div>
          <div className="flex items-end gap-3">
            <div className="text-3xl font-bold text-[var(--atum-warning)]">{stats.open}</div>
            <MiniSparkline data={[8, 6, 10, 7, 9, 5, stats.open || 4]} color="#f59e0b" />
          </div>
          <div className="text-xs text-[var(--atum-text-muted)] mt-2">Requires attention</div>
        </GlassCard>

        <GlassCard className="relative overflow-hidden group">
          <div className="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <CheckCircle size={80} />
          </div>
          <div className="text-[var(--atum-text-muted)] text-xs font-semibold uppercase tracking-wider mb-1">Resolved</div>
          <div className="text-3xl font-bold text-[var(--atum-success)] mb-2">{stats.resolved}</div>
          <div className="text-xs text-[var(--atum-success)]">Exceeding targets</div>
        </GlassCard>

        <GlassCard className="relative overflow-hidden group">
          <div className="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <AlertCircle size={80} />
          </div>
          <div className="text-[var(--atum-text-muted)] text-xs font-semibold uppercase tracking-wider mb-1">Urgent</div>
          <div className="text-3xl font-bold text-[var(--atum-danger)] mb-2">{stats.urgent}</div>
          <div className="text-xs text-[var(--atum-danger)] font-bold">Action needed</div>
        </GlassCard>
      </div>

      {/* Widgets & Recent */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content: Recent Tickets */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-lg font-bold text-white mb-4">Recent Activity</h2>
          <div className="space-y-3">
            {recentTickets.map(t => (
              <Link key={t.id} to={`/desk/tickets/${t.id}`} className="block">
                <div className="glass-card p-4 hover:border-[var(--atum-accent-gold)] flex items-center justify-between group">
                  <div className="flex items-center gap-4">
                    <div className={`w-2 h-12 rounded-full ${t.priority === 'urgent' ? 'bg-[var(--atum-danger)]' : 'bg-[var(--atum-border-strong)]'}`}></div>
                    <div>
                      <div className="font-semibold text-white group-hover:text-[var(--atum-accent-gold)] transition-colors">{t.subject}</div>
                      <div className="text-xs text-[var(--atum-text-muted)] flex items-center gap-2 mt-1">
                        <span>#{t.id.slice(0, 8)}</span> • <span>{t.status}</span> • <span>{new Date(t.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity text-[var(--atum-accent-gold)] text-sm font-medium">
                    View Details →
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Right Rail: Insights & Metrics */}
        <div className="space-y-6">
          <h2 className="text-lg font-bold text-white mb-4">Live Insights</h2>

          {widgets && (
            <>
              {/* AI Stats */}
              <GlassCard title="AI Copilot Performance">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400"><Brain size={18} /></div>
                    <div>
                      <div className="text-sm font-bold text-white">{widgets.ai_utilization?.triage_generated || 0}</div>
                      <div className="text-xs text-[var(--atum-text-muted)]">Triages</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400"><Ticket size={18} /></div>
                    <div>
                      <div className="text-sm font-bold text-white">{widgets.ai_utilization?.reply_generated || 0}</div>
                      <div className="text-xs text-[var(--atum-text-muted)]">Drafts</div>
                    </div>
                  </div>
                </div>
                <div className="w-full bg-[var(--atum-bg)] h-1.5 rounded-full overflow-hidden">
                  <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-full w-[65%]"></div>
                </div>
                <div className="text-[10px] text-[var(--atum-text-muted)] mt-2 text-right">65% Automation Rate</div>
              </GlassCard>

              {/* RAG Health */}
              <GlassCard title="RAG Knowledge Pipeline">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400"><Database size={18} /></div>
                  <div className="text-sm text-white">Knowledge Index</div>
                </div>
                <div className="flex justify-between items-center text-xs text-[var(--atum-text-muted)] border-t border-[var(--atum-border)] pt-3 mt-3">
                  <span>Indexed Documents</span>
                  <span className="text-white font-mono">1,248</span>
                </div>
                <div className="flex justify-between items-center text-xs text-[var(--atum-text-muted)] mt-1">
                  <span>Queue Backlog</span>
                  <span className="text-[var(--atum-success)] font-mono">0</span>
                </div>
              </GlassCard>
            </>
          )}
        </div>
      </div>
    </PageShell>
  )
}
