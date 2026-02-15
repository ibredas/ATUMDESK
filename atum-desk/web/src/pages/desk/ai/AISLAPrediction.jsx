import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { PageShell, GlassCard } from '../../../components/Premium'
import { TrendingUp, RefreshCw, AlertTriangle, AlertOctagon, CheckCircle, BarChart3, Lightbulb, Target, Sparkles } from 'lucide-react'

export default function AISLAPrediction() {
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [riskTickets, setRiskTickets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) { navigate('/desk/login'); return }
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const res = await fetch('/api/v1/ai/sla/predictions', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.status === 401) { navigate('/desk/login'); return }
      if (res.ok) {
        const data = await res.json()
        setRiskTickets(data.predictions || [])
      }
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const getRiskColor = (probability) => {
    if (probability > 0.7) return 'text-red-400 border-red-700'
    if (probability > 0.4) return 'text-orange-400 border-orange-700'
    return 'text-yellow-400 border-yellow-700'
  }

  const getRiskLabel = (probability) => {
    if (probability > 0.7) return 'HIGH RISK'
    if (probability > 0.4) return 'MEDIUM RISK'
    return 'LOW RISK'
  }

  if (loading) {
    return (
      <PageShell title="SLA Prediction" subtitle="Loading...">
        <div className="flex items-center justify-center py-24">
          <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
        </div>
      </PageShell>
    )
  }

  const highRisk = riskTickets.filter(t => t.breach_probability > 0.7)
  const mediumRisk = riskTickets.filter(t => t.breach_probability > 0.4 && t.breach_probability <= 0.7)
  const lowRisk = riskTickets.filter(t => t.breach_probability <= 0.4)

  return (
    <PageShell
      title="SLA Prediction"
      subtitle="AI-powered SLA breach predictions"
      actions={
        <button onClick={fetchData} className="btn-gold flex items-center gap-2">
          <RefreshCw size={16} /> Refresh Predictions
        </button>
      }
    >
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <GlassCard>
          <div className="p-5">
            <div className="text-sm text-[var(--atum-text-muted)] uppercase mb-2">At Risk</div>
            <div className="text-3xl font-bold text-red-400">{riskTickets.length}</div>
            <div className="text-xs text-[var(--atum-text-muted)]">Total predicted</div>
          </div>
        </GlassCard>
        <GlassCard>
          <div className="p-5">
            <div className="text-sm text-[var(--atum-text-muted)] uppercase mb-2">High Risk</div>
            <div className="text-3xl font-bold text-red-400">{highRisk.length}</div>
            <div className="text-xs text-[var(--atum-text-muted)]">&gt;70% probability</div>
          </div>
        </GlassCard>
        <GlassCard>
          <div className="p-5">
            <div className="text-sm text-[var(--atum-text-muted)] uppercase mb-2">Medium Risk</div>
            <div className="text-3xl font-bold text-orange-400">{mediumRisk.length}</div>
            <div className="text-xs text-[var(--atum-text-muted)]">40-70% probability</div>
          </div>
        </GlassCard>
        <GlassCard>
          <div className="p-5">
            <div className="text-sm text-[var(--atum-text-muted)] uppercase mb-2">Low Risk</div>
            <div className="text-3xl font-bold text-green-400">{lowRisk.length}</div>
            <div className="text-xs text-[var(--atum-text-muted)]">&lt;40% probability</div>
          </div>
        </GlassCard>
      </div>

      {/* Risk Tickets */}
      {riskTickets.length > 0 ? (
        <div className="space-y-4">
          {highRisk.length > 0 && (
            <GlassCard>
              <div className="p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-red-400 mb-4 flex items-center gap-2">
                  <AlertOctagon size={16} /> High Risk - Immediate Action Required
                </h2>
                <div className="space-y-3">
                  {highRisk.map((ticket, idx) => (
                    <div key={idx} className={`p-4 rounded-lg border bg-red-900/20 ${getRiskColor(ticket.breach_probability)}`}>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-semibold">{ticket.subject}</div>
                          <div className="flex items-center gap-3 mt-2 text-sm">
                            <span className={`badge badge-${ticket.priority}`}>{ticket.priority}</span>
                            <span>Due: {ticket.sla_due_at ? new Date(ticket.sla_due_at).toLocaleString() : 'N/A'}</span>
                            <span>Est. resolution: {ticket.estimated_resolution_hours}h</span>
                          </div>
                          {ticket.recommendations?.length > 0 && (
                            <div className="mt-2 text-sm opacity-80">
                              {ticket.recommendations.map((r, i) => <div key={i}>→ {r}</div>)}
                            </div>
                          )}
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold">{Math.round(ticket.breach_probability * 100)}%</div>
                          <div className="text-xs uppercase">{getRiskLabel(ticket.breach_probability)}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </GlassCard>
          )}

          {mediumRisk.length > 0 && (
            <GlassCard>
              <div className="p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-orange-400 mb-4 flex items-center gap-2">
                  <AlertTriangle size={16} /> Medium Risk - Monitor Closely
                </h2>
                <div className="space-y-3">
                  {mediumRisk.map((ticket, idx) => (
                    <div key={idx} className={`p-4 rounded-lg border bg-orange-900/10 ${getRiskColor(ticket.breach_probability)}`}>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-semibold">{ticket.subject}</div>
                          <div className="flex items-center gap-3 mt-2 text-sm">
                            <span className={`badge badge-${ticket.priority}`}>{ticket.priority}</span>
                            <span>Due: {ticket.sla_due_at ? new Date(ticket.sla_due_at).toLocaleString() : 'N/A'}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold">{Math.round(ticket.breach_probability * 100)}%</div>
                          <div className="text-xs uppercase">{getRiskLabel(ticket.breach_probability)}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </GlassCard>
          )}

          {lowRisk.length > 0 && (
            <GlassCard>
              <div className="p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-green-400 mb-4 flex items-center gap-2">
                  <CheckCircle size={16} /> Low Risk - On Track
                </h2>
                <div className="space-y-2">
                  {lowRisk.slice(0, 5).map((ticket, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-[var(--atum-bg)] rounded-lg">
                      <div>
                        <div className="font-medium">{ticket.subject}</div>
                        <div className="text-xs text-[var(--atum-text-muted)]">
                          Due: {ticket.sla_due_at ? new Date(ticket.sla_due_at).toLocaleString() : 'N/A'}
                        </div>
                      </div>
                      <span className="text-green-400 font-medium">{Math.round(ticket.breach_probability * 100)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </GlassCard>
          )}
        </div>
      ) : (
        <GlassCard>
          <div className="text-center py-12">
            <Sparkles size={48} className="mx-auto mb-4 text-[var(--atum-accent-gold)] opacity-30" />
            <h3 className="text-xl font-bold mb-2">All Clear!</h3>
            <p className="text-[var(--atum-text-muted)]">No tickets at risk of SLA breach</p>
          </div>
        </GlassCard>
      )}

      {/* Quick Links */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        {[
          { to: '/desk/ai/analytics', icon: BarChart3, label: 'AI Analytics' },
          { to: '/desk/ai/insights', icon: Lightbulb, label: 'Smart Insights' },
          { to: '/desk/ai/agent-assist', icon: Target, label: 'Agent Assist' },
        ].map(link => (
          <Link key={link.to} to={link.to}
            className="glass-panel rounded-xl p-4 hover:border-[var(--atum-accent-gold)] transition text-center group">
            <link.icon size={24} className="mx-auto mb-2 text-[var(--atum-text-muted)] group-hover:text-[var(--atum-accent-gold)] transition" />
            <div className="font-medium text-sm">{link.label}</div>
          </Link>
        ))}
      </div>
    </PageShell>
  )
}
