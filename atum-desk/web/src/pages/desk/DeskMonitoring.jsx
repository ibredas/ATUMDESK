import React, { useState, useEffect } from 'react'
import { PageShell, GlassCard } from '../../components/Premium'
import { Activity, Server, Database, Brain, Cpu, RefreshCw } from 'lucide-react'

export default function DeskMonitoring() {
    const [metrics, setMetrics] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => { loadMonitoringData() }, [])

    const loadMonitoringData = async () => {
        try {
            const token = localStorage.getItem('atum_desk_token')
            const response = await fetch('/api/v1/metrics/live', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setMetrics(data)
            }
        } catch (err) {
            console.error('Failed to load metrics:', err)
        } finally {
            setLoading(false)
        }
    }

    const serviceStatus = [
        { name: 'API Server', status: 'running', pid: '769834', icon: Server },
        { name: 'SLA Worker', status: 'running', pid: '670177', icon: Activity },
        { name: 'Job Worker', status: 'running', pid: '501596', icon: Cpu },
        { name: 'RAG Worker', status: 'running', pid: '324772', icon: Brain },
    ]

    return (
        <PageShell title="Monitoring" icon={Activity}
            actions={<button onClick={loadMonitoringData} className="btn-outline flex items-center gap-2"><RefreshCw size={14} /> Refresh</button>}>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                {serviceStatus.map((service) => (
                    <GlassCard key={service.name}>
                        <div className="flex items-center justify-between mb-2">
                            <span className="font-medium flex items-center gap-2"><service.icon size={16} className="text-[var(--atum-accent-gold)]" /> {service.name}</span>
                            <span className={`px-2 py-1 rounded text-xs ${service.status === 'running' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
                                {service.status}
                            </span>
                        </div>
                        <div className="text-sm text-[var(--atum-text-muted)]">PID: {service.pid}</div>
                    </GlassCard>
                ))}
            </div>

            <GlassCard className="mb-6">
                <h2 className="text-lg font-semibold mb-4">Live Metrics</h2>
                {loading ? (
                    <div className="text-[var(--atum-text-muted)]">Loading metrics...</div>
                ) : metrics ? (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-[var(--atum-accent-gold)]">
                                {Object.values(metrics.tickets_by_status || {}).reduce((a, b) => a + b, 0)}
                            </div>
                            <div className="text-sm text-[var(--atum-text-muted)]">Total Tickets</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-blue-400">{metrics.tickets_by_status?.new || 0}</div>
                            <div className="text-sm text-[var(--atum-text-muted)]">New</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-orange-400">{metrics.tickets_by_status?.in_progress || 0}</div>
                            <div className="text-sm text-[var(--atum-text-muted)]">In Progress</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-green-400">{metrics.sla_compliance_pct?.toFixed(1) || 0}%</div>
                            <div className="text-sm text-[var(--atum-text-muted)]">SLA Compliance</div>
                        </div>
                    </div>
                ) : (
                    <div className="text-[var(--atum-text-muted)]">No metrics data available</div>
                )}
            </GlassCard>

            <GlassCard>
                <h2 className="text-lg font-semibold mb-4">System Information</h2>
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div><span className="text-[var(--atum-text-muted)]">Database:</span> PostgreSQL 15</div>
                    <div><span className="text-[var(--atum-text-muted)]">AI Engine:</span> Ollama (Local)</div>
                    <div><span className="text-[var(--atum-text-muted)]">Queue:</span> PostgreSQL-backed</div>
                    <div><span className="text-[var(--atum-text-muted)]">Deployment:</span> Bare-metal / systemd</div>
                </div>
            </GlassCard>
        </PageShell>
    )
}
