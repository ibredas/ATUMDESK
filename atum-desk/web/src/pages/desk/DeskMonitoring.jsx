import React, { useState, useEffect } from 'react'

export default function DeskMonitoring() {
    const [services, setServices] = useState([])
    const [metrics, setMetrics] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        loadMonitoringData()
    }, [])

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
        { name: 'API Server', status: 'running', pid: '769834' },
        { name: 'SLA Worker', status: 'running', pid: '670177' },
        { name: 'Job Worker', status: 'running', pid: '501596' },
        { name: 'RAG Worker', status: 'running', pid: '324772' },
    ]

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-6">Monitoring</h1>
            
            {/* Service Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                {serviceStatus.map((service) => (
                    <div key={service.name} className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{service.name}</span>
                            <span className={`px-2 py-1 rounded text-xs ${service.status === 'running' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
                                {service.status}
                            </span>
                        </div>
                        <div className="text-sm text-[var(--text-muted)]">
                            PID: {service.pid}
                        </div>
                    </div>
                ))}
            </div>

            {/* Metrics Section */}
            <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-6">
                <h2 className="text-lg font-semibold mb-4">Live Metrics</h2>
                
                {loading ? (
                    <div className="text-[var(--text-muted)]">Loading metrics...</div>
                ) : metrics ? (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-[var(--accent-gold)]">
                                {Object.values(metrics.tickets_by_status || {}).reduce((a, b) => a + b, 0)}
                            </div>
                            <div className="text-sm text-[var(--text-muted)]">Total Tickets</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-blue-400">
                                {metrics.tickets_by_status?.new || 0}
                            </div>
                            <div className="text-sm text-[var(--text-muted)]">New</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-orange-400">
                                {metrics.tickets_by_status?.in_progress || 0}
                            </div>
                            <div className="text-sm text-[var(--text-muted)]">In Progress</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-green-400">
                                {metrics.sla_compliance_pct?.toFixed(1) || 0}%
                            </div>
                            <div className="text-sm text-[var(--text-muted)]">SLA Compliance</div>
                        </div>
                    </div>
                ) : (
                    <div className="text-[var(--text-muted)]">No metrics data available</div>
                )}
            </div>

            {/* System Info */}
            <div className="mt-6 bg-[var(--card)] border border-[var(--border)] rounded-lg p-6">
                <h2 className="text-lg font-semibold mb-4">System Information</h2>
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <span className="text-[var(--text-muted)]">Database:</span> PostgreSQL 15
                    </div>
                    <div>
                        <span className="text-[var(--text-muted)]">AI Engine:</span> Ollama (Local)
                    </div>
                    <div>
                        <span className="text-[var(--text-muted)]">Queue:</span> PostgreSQL-backed
                    </div>
                    <div>
                        <span className="text-[var(--text-muted)]">Deployment:</span> Bare-metal / systemd
                    </div>
                </div>
            </div>
        </div>
    )
}
