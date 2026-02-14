import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import DeskSidebar from '../../../components/DeskSidebar'

export default function AISmartInsights() {
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [insights, setInsights] = useState(null)
  const [trends, setTrends] = useState(null)
  const [predictions, setPredictions] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) { navigate('/desk/login'); return }
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [insightsRes, trendsRes, predictionsRes] = await Promise.all([
        fetch('/api/v1/ai/insights/dashboard?days=7', { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch('/api/v1/ai/insights/trends?metric=tickets&days=14', { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch('/api/v1/ai/insights/predictions', { headers: { 'Authorization': `Bearer ${token}` } })
      ])
      
      if (insightsRes.ok) setInsights(await insightsRes.json())
      if (trendsRes.ok) setTrends(await trendsRes.json())
      if (predictionsRes.ok) setPredictions(await predictionsRes.json())
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const getSeverityStyle = (severity) => {
    switch (severity) {
      case 'warning': return 'bg-orange-900/30 border-orange-700 text-orange-400'
      case 'success': return 'bg-green-900/30 border-green-700 text-green-400'
      case 'info': return 'bg-blue-900/30 border-blue-700 text-blue-400'
      default: return 'bg-gray-900/30 border-gray-700 text-gray-400'
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
                <span className="text-3xl">💡</span>
                Smart Insights
              </h1>
              <p className="text-[var(--text-muted)] mt-1">AI-powered analytics and recommendations</p>
            </div>
            <button 
              onClick={fetchData}
              className="px-4 py-2 bg-[var(--accent-gold)] text-black font-semibold rounded-lg hover:brightness-110 transition"
            >
              Refresh
            </button>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="glass-panel rounded-xl p-5">
              <div className="text-sm text-[var(--text-muted)] uppercase mb-2">Total Tickets</div>
              <div className="text-3xl font-bold text-[var(--accent-gold)]">{insights?.total_tickets || 0}</div>
              <div className="text-xs text-[var(--text-muted)]">Last 7 days</div>
            </div>
            <div className="glass-panel rounded-xl p-5">
              <div className="text-sm text-[var(--text-muted)] uppercase mb-2">Avg Resolution</div>
              <div className="text-3xl font-bold text-green-400">{insights?.avg_resolution_hours || 0}h</div>
              <div className="text-xs text-[var(--text-muted)]">Per ticket</div>
            </div>
            <div className="glass-panel rounded-xl p-5">
              <div className="text-sm text-[var(--text-muted)] uppercase mb-2">Predicted Volume</div>
              <div className="text-3xl font-bold text-blue-400">{predictions?.ticket_volume?.next_7_days?.predicted || 0}</div>
              <div className="text-xs text-[var(--text-muted)]">Next 7 days</div>
            </div>
            <div className="glass-panel rounded-xl p-5">
              <div className="text-sm text-[var(--text-muted)] uppercase mb-2">SLA At Risk</div>
              <div className="text-3xl font-bold text-orange-400">{predictions?.sla_risks?.at_risk || 0}</div>
              <div className="text-xs text-[var(--text-muted)]">Need attention</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* AI Recommendations */}
            <div className="glass-panel rounded-xl p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4 flex items-center gap-2">
                <span>🤖</span> AI Recommendations
              </h2>
              <div className="space-y-3">
                {insights?.insights?.map((insight, idx) => (
                  <div key={idx} className={`p-4 rounded-lg border ${getSeverityStyle(insight.severity)}`}>
                    <div className="font-medium">{insight.message}</div>
                    {insight.recommendation && (
                      <div className="text-sm opacity-80 mt-1">→ {insight.recommendation}</div>
                    )}
                  </div>
                ))}
                {!insights?.insights?.length && (
                  <div className="text-[var(--text-muted)] text-center py-8">No insights available</div>
                )}
              </div>
            </div>

            {/* Predictions */}
            <div className="glass-panel rounded-xl p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4 flex items-center gap-2">
                <span>🔮</span> AI Predictions
              </h2>
              <div className="space-y-4">
                <div className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">Ticket Volume (7 days)</span>
                    <span className="text-green-400">{predictions?.ticket_volume?.next_7_days?.confidence * 100}% conf</span>
                  </div>
                  <div className="text-2xl font-bold text-[var(--accent-gold)]">
                    {predictions?.ticket_volume?.next_7_days?.predicted || 0} tickets
                  </div>
                  <div className="text-xs text-[var(--text-muted)]">
                    Trend: {predictions?.ticket_volume?.next_7_days?.trend}
                  </div>
                </div>

                <div className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">SLA Risks</span>
                    <span className="text-orange-400">{predictions?.sla_risks?.at_risk || 0} at risk</span>
                  </div>
                  <div className="space-y-1">
                    {predictions?.sla_risks?.recommendations?.slice(0, 3).map((rec, idx) => (
                      <div key={idx} className="text-sm text-[var(--text-muted)]">→ {rec}</div>
                    ))}
                  </div>
                </div>

                <div className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                  <div className="font-medium mb-2">Category Distribution</div>
                  <div className="flex flex-wrap gap-2">
                    {predictions?.category_distribution && Object.entries(predictions.category_distribution).map(([cat, count]) => (
                      <span key={cat} className="px-2 py-1 bg-[var(--bg-2)] rounded text-xs">
                        {cat}: {count}%
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mt-6 glass-panel rounded-xl p-6">
            <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">
              ⚡ Quick Actions
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Link to="/desk/ai/analytics" className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)] hover:border-[var(--accent-gold)] transition text-center">
                <div className="text-2xl mb-2">📊</div>
                <div className="font-medium">View Analytics</div>
              </Link>
              <Link to="/desk/ai/agent-assist" className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)] hover:border-[var(--accent-gold)] transition text-center">
                <div className="text-2xl mb-2">🎯</div>
                <div className="font-medium">Agent Assist</div>
              </Link>
              <Link to="/desk/ai/sla-prediction" className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)] hover:border-[var(--accent-gold)] transition text-center">
                <div className="text-2xl mb-2">⏰</div>
                <div className="font-medium">SLA Predictions</div>
              </Link>
              <Link to="/desk/kb" className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)] hover:border-[var(--accent-gold)] transition text-center">
                <div className="text-2xl mb-2">📚</div>
                <div className="font-medium">Knowledge Base</div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
