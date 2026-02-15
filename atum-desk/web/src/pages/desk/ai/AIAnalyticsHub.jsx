import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { PageShell, GlassCard } from '../../../components/Premium'
import { Bot, Activity, AlertTriangle, TrendingUp, Clock, Lightbulb, Target, Settings, BarChart3, BookOpen, Sparkles } from 'lucide-react'

export default function AIAnalyticsHub() {
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState(null)

  useEffect(() => {
    if (!token) { navigate('/desk/login'); return }
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const res = await fetch('/api/v1/ai/analytics/overview?days=7', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.status === 401) { navigate('/desk/login'); return }
      if (res.ok) setData(await res.json())
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  if (loading) {
    return (
      <PageShell title="AI Intelligence Hub" subtitle="Loading...">
        <div className="flex items-center justify-center py-24">
          <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
        </div>
      </PageShell>
    )
  }

  const statusColor = data?.summary?.status === 'healthy' ? 'text-green-400' : 'text-orange-400'

  return (
    <PageShell title="AI Intelligence Hub" subtitle="Enterprise AI-powered operations">
      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <GlassCard>
          <div className="p-5">
            <div className="flex items-center gap-3 mb-3">
              <Activity size={20} className="text-[var(--atum-accent-gold)]" />
              <span className="text-sm text-[var(--atum-text-muted)] uppercase">Status</span>
            </div>
            <div className={`text-2xl font-bold ${statusColor}`}>
              {data?.summary?.status === 'healthy' ? '◆ HEALTHY' : '◆ ACTION NEEDED'}
            </div>
          </div>
        </GlassCard>
        <GlassCard>
          <div className="p-5">
            <div className="flex items-center gap-3 mb-3">
              <AlertTriangle size={20} className="text-orange-400" />
              <span className="text-sm text-[var(--atum-text-muted)] uppercase">Needs Attention</span>
            </div>
            <div className="text-2xl font-bold text-orange-400">{data?.summary?.needs_attention || 0}</div>
          </div>
        </GlassCard>
        <GlassCard>
          <div className="p-5">
            <div className="flex items-center gap-3 mb-3">
              <TrendingUp size={20} className="text-[var(--atum-accent-gold)]" />
              <span className="text-sm text-[var(--atum-text-muted)] uppercase">Anomalies</span>
            </div>
            <div className="text-2xl font-bold text-[var(--atum-accent-gold)]">{data?.anomalies?.anomaly_count || 0}</div>
          </div>
        </GlassCard>
        <GlassCard>
          <div className="p-5">
            <div className="flex items-center gap-3 mb-3">
              <Clock size={20} className="text-red-400" />
              <span className="text-sm text-[var(--atum-text-muted)] uppercase">SLA Risks</span>
            </div>
            <div className="text-2xl font-bold text-red-400">{data?.sla_risks?.count || 0}</div>
          </div>
        </GlassCard>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { to: '/desk/ai/insights', icon: Lightbulb, label: 'Smart Insights', desc: 'AI-generated recommendations' },
          { to: '/desk/ai/agent-assist', icon: Target, label: 'Agent Assist', desc: 'Real-time AI help' },
          { to: '/desk/ai/sla-prediction', icon: TrendingUp, label: 'SLA Predict', desc: 'Breach prediction' },
          { to: '/desk/ai/preferences', icon: Settings, label: 'AI Settings', desc: 'Configure preferences' },
        ].map(link => (
          <Link key={link.to} to={link.to} className="glass-panel rounded-xl p-5 hover:border-[var(--atum-accent-gold)] transition-colors group">
            <link.icon size={28} className="mb-3 text-[var(--atum-text-muted)] group-hover:text-[var(--atum-accent-gold)] group-hover:scale-110 transition-all" />
            <h3 className="font-semibold mb-1">{link.label}</h3>
            <p className="text-xs text-[var(--atum-text-muted)]">{link.desc}</p>
          </Link>
        ))}
      </div>

      {/* SLA Risks */}
      {data?.sla_risks?.tickets?.length > 0 && (
        <GlassCard className="mb-6">
          <div className="p-6">
            <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4 flex items-center gap-2">
              <AlertTriangle size={16} className="text-red-400" /> At-Risk Tickets
            </h2>
            <div className="space-y-2">
              {data.sla_risks.tickets.slice(0, 5).map((ticket, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-[var(--atum-bg)] rounded-lg border border-[var(--atum-border)]">
                  <div>
                    <div className="font-medium">{ticket.subject}</div>
                    <div className="text-xs text-[var(--atum-text-muted)]">
                      Priority: {ticket.priority} • Due: {ticket.sla_due_at ? new Date(ticket.sla_due_at).toLocaleString() : 'N/A'}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-orange-400">{Math.round(ticket.breach_probability * 100)}% risk</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </GlassCard>
      )}

      {/* Anomalies */}
      {data?.anomalies?.anomalies?.length > 0 && (
        <GlassCard>
          <div className="p-6">
            <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4 flex items-center gap-2">
              <BarChart3 size={16} /> Detected Anomalies
            </h2>
            <div className="space-y-2">
              {data.anomalies.anomalies.map((anomaly, idx) => (
                <div key={idx} className={`p-3 rounded-lg border ${anomaly.severity === 'high' ? 'bg-red-900/20 border-red-700' : 'bg-orange-900/20 border-orange-700'
                  }`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{anomaly.message}</div>
                      {anomaly.recommendation && (
                        <div className="text-xs text-[var(--atum-text-muted)] mt-1">→ {anomaly.recommendation}</div>
                      )}
                    </div>
                    <span className={`badge badge-${anomaly.severity === 'high' ? 'urgent' : 'high'}`}>{anomaly.severity}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </GlassCard>
      )}

      {(!data || (data?.anomalies?.anomaly_count === 0 && data?.sla_risks?.count === 0)) && (
        <GlassCard>
          <div className="text-center py-12">
            <Sparkles size={48} className="mx-auto mb-4 text-[var(--atum-accent-gold)] opacity-30" />
            <h3 className="text-xl font-bold mb-2">All Systems Operational</h3>
            <p className="text-[var(--atum-text-muted)]">No anomalies or SLA risks detected</p>
          </div>
        </GlassCard>
      )}
    </PageShell>
  )
}
