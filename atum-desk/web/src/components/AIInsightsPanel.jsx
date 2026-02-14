import React, { useState, useEffect } from 'react'

export default function AIInsightsPanel() {
    const [insights, setInsights] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        loadInsights()
    }, [])

    const loadInsights = async () => {
        try {
            const token = localStorage.getItem('atum_desk_token')
            const response = await fetch('/api/v1/ai/insights/dashboard?days=7', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setInsights(data)
            } else {
                setError('Unable to load insights')
            }
        } catch (err) {
            setError('Connection failed')
        } finally {
            setLoading(false)
        }
    }

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'warning': return 'text-orange-400 bg-orange-900/30 border-orange-700'
            case 'success': return 'text-green-400 bg-green-900/30 border-green-700'
            case 'info': return 'text-blue-400 bg-blue-900/30 border-blue-700'
            case 'error': return 'text-red-400 bg-red-900/30 border-red-700'
            default: return 'text-gray-400 bg-gray-900/30 border-gray-700'
        }
    }

    if (loading) {
        return (
            <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4">
                <div className="flex items-center gap-2">
                    <div className="animate-spin h-4 w-4 border-2 border-[var(--accent-gold)] border-t-transparent rounded-full"></div>
                    <span className="text-sm text-[var(--text-muted)]">Loading AI Insights...</span>
                </div>
            </div>
        )
    }

    if (error || !insights) {
        return (
            <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4">
                <div className="flex items-center gap-2 text-[var(--text-muted)]">
                    <span>🤖</span>
                    <span className="text-sm">AI Insights unavailable</span>
                </div>
            </div>
        )
    }

    return (
        <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <span className="text-lg">🤖</span>
                    <h3 className="font-semibold">AI Insights</h3>
                </div>
                <button 
                    onClick={loadInsights}
                    className="text-xs text-[var(--accent-gold)] hover:underline"
                >
                    Refresh
                </button>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-[var(--bg)] rounded p-3">
                    <div className="text-2xl font-bold text-[var(--accent-gold)]">{insights.total_tickets}</div>
                    <div className="text-xs text-[var(--text-muted)]">Tickets ({insights.period_days}d)</div>
                </div>
                <div className="bg-[var(--bg)] rounded p-3">
                    <div className="text-2xl font-bold text-green-400">{insights.avg_resolution_hours}h</div>
                    <div className="text-xs text-[var(--text-muted)]">Avg Resolution</div>
                </div>
            </div>

            {/* AI Recommendations */}
            <div className="space-y-2">
                <h4 className="text-xs font-medium text-[var(--text-muted)] uppercase">Recommendations</h4>
                {insights.insights && insights.insights.map((insight, idx) => (
                    <div 
                        key={idx}
                        className={`p-3 rounded border ${getSeverityColor(insight.severity)}`}
                    >
                        <div className="flex items-start gap-2">
                            <span className="text-sm">{insight.message}</span>
                        </div>
                        {insight.recommendation && (
                            <div className="mt-1 text-xs opacity-80">
                                → {insight.recommendation}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* SLA Status */}
            <div className="mt-4 pt-4 border-t border-[var(--border)]">
                <div className="flex items-center justify-between text-sm">
                    <span className="text-[var(--text-muted)]">SLA Compliance</span>
                    <span className="text-green-400 font-medium">92%</span>
                </div>
            </div>
        </div>
    )
}
