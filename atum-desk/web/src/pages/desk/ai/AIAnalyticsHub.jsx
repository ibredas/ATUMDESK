import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import DeskSidebar from '../../../components/DeskSidebar'

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
      if (res.ok) {
        const json = await res.json()
        setData(json)
      }
    } catch (e) { console.error(e) }
    setLoading(false)
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

  const statusColor = data?.summary?.status === 'healthy' ? 'text-green-400' : 'text-orange-400'

  return (
    <div className="flex min-h-screen bg-[var(--bg-0)]">
      <DeskSidebar />
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-3">
                <span className="text-3xl">🤖</span>
                AI Intelligence Hub
              </h1>
              <p className="text-[var(--text-muted)] mt-1">Enterprise AI-powered operations</p>
            </div>
            <span className="text-[10px] uppercase tracking-widest text-[var(--text-2)]">ATUM DESK v1.0.0</span>
          </div>

          {/* Status Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="glass-panel rounded-xl p-5">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">🎯</span>
                <span className="text-sm text-[var(--text-muted)] uppercase">Status</span>
              </div>
              <div className={`text-2xl font-bold ${statusColor}`}>
                {data?.summary?.status === 'healthy' ? '◆ HEALTHY' : '◆ ACTION NEEDED'}
              </div>
            </div>
            
            <div className="glass-panel rounded-xl p-5">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">⚠️</span>
                <span className="text-sm text-[var(--text-muted)] uppercase">Needs Attention</span>
              </div>
              <div className="text-2xl font-bold text-orange-400">
                {data?.summary?.needs_attention || 0}
              </div>
            </div>

            <div className="glass-panel rounded-xl p-5">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">📈</span>
                <span className="text-sm text-[var(--text-muted)] uppercase">Anomalies</span>
              </div>
              <div className="text-2xl font-bold text-[var(--accent-gold)]">
                {data?.anomalies?.anomaly_count || 0}
              </div>
            </div>

            <div className="glass-panel rounded-xl p-5">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-2xl">⏰</span>
                <span className="text-sm text-[var(--text-muted)] uppercase">SLA Risks</span>
              </div>
              <div className="text-2xl font-bold text-red-400">
                {data?.sla_risks?.count || 0}
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <Link to="/desk/ai/insights" className="glass-panel rounded-xl p-5 hover:border-[var(--accent-gold)] transition-colors group">
              <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">💡</div>
              <h3 className="font-semibold mb-1">Smart Insights</h3>
              <p className="text-xs text-[var(--text-muted)]">AI-generated recommendations</p>
            </Link>
            
            <Link to="/desk/ai/agent-assist" className="glass-panel rounded-xl p-5 hover:border-[var(--accent-gold)] transition-colors group">
              <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">🎯</div>
              <h3 className="font-semibold mb-1">Agent Assist</h3>
              <p className="text-xs text-[var(--text-muted)]">Real-time AI help</p>
            </Link>
            
            <Link to="/desk/ai/sla-prediction" className="glass-panel rounded-xl p-5 hover:border-[var(--accent-gold)] transition-colors group">
              <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">🔮</div>
              <h3 className="font-semibold mb-1">SLA Predict</h3>
              <p className="text-xs text-[var(--text-muted)]">Breach prediction</p>
            </Link>
            
            <Link to="/desk/ai/preferences" className="glass-panel rounded-xl p-5 hover:border-[var(--accent-gold)] transition-colors group">
              <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">⚙️</div>
              <h3 className="font-semibold mb-1">AI Settings</h3>
              <p className="text-xs text-[var(--text-muted)]">Configure preferences</p>
            </Link>
          </div>

          {/* SLA Risks */}
          {data?.sla_risks?.tickets?.length > 0 && (
            <div className="glass-panel rounded-xl p-6 mb-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">
                🚨 At-Risk Tickets
              </h2>
              <div className="space-y-2">
                {data.sla_risks.tickets.slice(0, 5).map((ticket, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                    <div>
                      <div className="font-medium">{ticket.subject}</div>
                      <div className="text-xs text-[var(--text-muted)]">
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
          )}

          {/* Anomalies */}
          {data?.anomalies?.anomalies?.length > 0 && (
            <div className="glass-panel rounded-xl p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">
                📊 Detected Anomalies
              </h2>
              <div className="space-y-2">
                {data.anomalies.anomalies.map((anomaly, idx) => (
                  <div key={idx} className={`p-3 rounded-lg border ${
                    anomaly.severity === 'high' ? 'bg-red-900/20 border-red-700' : 'bg-orange-900/20 border-orange-700'
                  }`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">{anomaly.message}</div>
                        {anomaly.recommendation && (
                          <div className="text-xs text-[var(--text-muted)] mt-1">→ {anomaly.recommendation}</div>
                        )}
                      </div>
                      <span className={`badge badge-${anomaly.severity === 'high' ? 'urgent' : 'high'}`}>
                        {anomaly.severity}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {(!data || (data?.anomalies?.anomaly_count === 0 && data?.sla_risks?.count === 0)) && (
            <div className="glass-panel rounded-xl p-12 text-center">
              <div className="text-5xl mb-4">✨</div>
              <h3 className="text-xl font-bold mb-2">All Systems Operational</h3>
              <p className="text-[var(--text-muted)]">No anomalies or SLA risks detected</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
