import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageShell, GlassCard } from '../../components/Premium'
import { AlertTriangle, TrendingUp } from 'lucide-react'

export default function DeskSLAAlerts() {
    const navigate = useNavigate()
    const token = localStorage.getItem('atum_desk_token')
    const [alerts, setAlerts] = useState([])
    const [predictions, setPredictions] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!token) { navigate('/desk/login'); return }
        fetchAlerts()
    }, [])

    const fetchAlerts = async () => {
        try {
            const res = await fetch('/api/v1/ai/sla/predictions', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                const data = await res.json()
                setPredictions(Array.isArray(data) ? data : data.items || [])
            }
        } catch (e) { /* best effort */ }

        try {
            const res = await fetch('/api/v1/notifications?type=sla_warning', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                const data = await res.json()
                setAlerts(Array.isArray(data) ? data : data.items || [])
            }
        } catch (e) { /* best effort */ }
        setLoading(false)
    }

    return (
        <PageShell title="SLA Alerts & Predictions" subtitle="Real-time SLA monitoring">
            {loading ? (
                <div className="flex items-center justify-center py-24">
                    <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
                </div>
            ) : (
                <div className="space-y-8">
                    {/* Active Alerts */}
                    <GlassCard>
                        <div className="p-6">
                            <h2 className="text-sm font-bold uppercase tracking-widest text-red-400 mb-4 flex items-center gap-2">
                                <AlertTriangle size={16} /> Active SLA Alerts
                            </h2>
                            {alerts.length === 0 ? (
                                <p className="text-sm text-[var(--atum-text-muted)] py-4">No active SLA alerts — all tickets within bounds.</p>
                            ) : (
                                <div className="space-y-3">
                                    {alerts.map((alert, i) => (
                                        <div key={alert.id || i} className="glass-card rounded-lg p-4 border border-red-500/20">
                                            <div className="flex items-center justify-between">
                                                <div>
                                                    <h3 className="text-sm font-medium text-white">{alert.title}</h3>
                                                    <p className="text-xs text-[var(--atum-text-muted)] mt-1">{alert.message}</p>
                                                </div>
                                                <span className="text-[10px] text-[var(--atum-text-muted)]">{new Date(alert.created_at).toLocaleString()}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </GlassCard>

                    {/* SLA Predictions */}
                    <GlassCard className="p-0 overflow-hidden">
                        <div className="p-6 pb-0">
                            <h2 className="text-sm font-bold uppercase tracking-widest text-amber-400 mb-4 flex items-center gap-2">
                                <TrendingUp size={16} /> SLA Risk Predictions
                            </h2>
                        </div>
                        {predictions.length === 0 ? (
                            <p className="text-sm text-[var(--atum-text-muted)] px-6 py-8">No SLA predictions available yet.</p>
                        ) : (
                            <table className="glass-table">
                                <thead>
                                    <tr>
                                        <th>Ticket</th>
                                        <th>Risk Score</th>
                                        <th>Time to Breach</th>
                                        <th>Priority</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {predictions.map((p, i) => (
                                        <tr key={p.ticket_id || i} onClick={() => navigate(`/desk/tickets/${p.ticket_id}`)} className="cursor-pointer">
                                            <td className="text-xs font-mono">{(p.ticket_id || '').substring(0, 8)}...</td>
                                            <td>
                                                <span className={`badge ${p.sla_risk_score > 0.7 ? 'badge-urgent' : p.sla_risk_score > 0.4 ? 'badge-high' : 'badge-low'}`}>
                                                    {((p.sla_risk_score || 0) * 100).toFixed(0)}%
                                                </span>
                                            </td>
                                            <td className="text-xs">{p.time_to_breach_minutes ? `${p.time_to_breach_minutes} min` : '—'}</td>
                                            <td><span className={`badge badge-${p.priority}`}>{p.priority || '—'}</span></td>
                                            <td><span className={`badge badge-${p.status}`}>{(p.status || '—').replace('_', ' ')}</span></td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </GlassCard>
                </div>
            )}
        </PageShell>
    )
}
