import React, { useState, useEffect, useCallback } from 'react'

const API = '/api/v1/incidents'

export default function DeskIncidents() {
    const [incidents, setIncidents] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [showCreate, setShowCreate] = useState(false)
    const [form, setForm] = useState({ title: '', severity: 'SEV3', customer_impact_summary: '' })

    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

    const fetchIncidents = useCallback(async () => {
        try {
            setLoading(true)
            const res = await fetch(API, { headers })
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            const data = await res.json()
            setIncidents(Array.isArray(data) ? data : data.items || [])
        } catch (e) {
            setError(e.message)
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => { fetchIncidents() }, [fetchIncidents])

    const handleCreate = async (e) => {
        e.preventDefault()
        try {
            const res = await fetch(API, { method: 'POST', headers, body: JSON.stringify(form) })
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            setShowCreate(false)
            setForm({ title: '', severity: 'SEV3', customer_impact_summary: '' })
            fetchIncidents()
        } catch (e) {
            setError(e.message)
        }
    }

    const sevColor = (sev) => {
        const m = { SEV1: '#ef4444', SEV2: '#f59e0b', SEV3: '#3b82f6', SEV4: '#6b7280' }
        return m[sev] || '#6b7280'
    }

    const statusColor = (s) => {
        const m = { OPEN: '#ef4444', MITIGATING: '#f59e0b', RESOLVED: '#22c55e', CLOSED: '#6b7280' }
        return m[s] || '#6b7280'
    }

    return (
        <div className="desk-page">
            <div className="desk-page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1>🚨 Incidents</h1>
                    <p style={{ color: 'var(--text-2)' }}>Major incident tracking & management</p>
                </div>
                <button
                    onClick={() => setShowCreate(!showCreate)}
                    style={{
                        padding: '10px 20px', borderRadius: '8px', border: 'none', cursor: 'pointer',
                        background: 'var(--accent, #c9a227)', color: '#000', fontWeight: 600
                    }}
                >
                    {showCreate ? 'Cancel' : '+ Declare Incident'}
                </button>
            </div>

            {error && (
                <div style={{ padding: '12px 16px', background: '#ef444420', border: '1px solid #ef4444', borderRadius: '8px', marginBottom: '16px', color: '#ef4444' }}>
                    {error}
                </div>
            )}

            {showCreate && (
                <div className="glass-panel" style={{ padding: '24px', borderRadius: '12px', marginBottom: '16px', border: '1px solid var(--glass-border)' }}>
                    <h3 style={{ marginBottom: '16px' }}>Declare New Incident</h3>
                    <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <input
                            placeholder="Incident title..."
                            value={form.title}
                            onChange={e => setForm({ ...form, title: e.target.value })}
                            required
                            style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'var(--bg-2, #1a1a2e)', color: 'var(--text-1)' }}
                        />
                        <select
                            value={form.severity}
                            onChange={e => setForm({ ...form, severity: e.target.value })}
                            style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'var(--bg-2, #1a1a2e)', color: 'var(--text-1)' }}
                        >
                            <option value="SEV1">SEV-1 (Critical)</option>
                            <option value="SEV2">SEV-2 (High)</option>
                            <option value="SEV3">SEV-3 (Medium)</option>
                            <option value="SEV4">SEV-4 (Low)</option>
                        </select>
                        <textarea
                            placeholder="Customer impact summary..."
                            value={form.customer_impact_summary}
                            onChange={e => setForm({ ...form, customer_impact_summary: e.target.value })}
                            rows={3}
                            style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'var(--bg-2, #1a1a2e)', color: 'var(--text-1)', resize: 'vertical' }}
                        />
                        <button type="submit" style={{ padding: '10px', borderRadius: '8px', border: 'none', background: '#ef4444', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>
                            🚨 Declare Incident
                        </button>
                    </form>
                </div>
            )}

            <div className="glass-panel" style={{ borderRadius: '12px', border: '1px solid var(--glass-border)', overflow: 'hidden' }}>
                {loading ? (
                    <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-2)' }}>Loading incidents...</div>
                ) : incidents.length === 0 ? (
                    <div style={{ padding: '40px', textAlign: 'center' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '12px' }}>✅</div>
                        <h3>No Active Incidents</h3>
                        <p style={{ color: 'var(--text-2)' }}>All systems operational</p>
                    </div>
                ) : (
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid var(--glass-border)' }}>
                                <th style={{ padding: '12px 16px', textAlign: 'left' }}>Severity</th>
                                <th style={{ padding: '12px 16px', textAlign: 'left' }}>Title</th>
                                <th style={{ padding: '12px 16px', textAlign: 'left' }}>Status</th>
                                <th style={{ padding: '12px 16px', textAlign: 'left' }}>Started</th>
                            </tr>
                        </thead>
                        <tbody>
                            {incidents.map(inc => (
                                <tr key={inc.id} style={{ borderBottom: '1px solid var(--glass-border, #333)' }}>
                                    <td style={{ padding: '12px 16px' }}>
                                        <span style={{ padding: '4px 10px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 700, background: sevColor(inc.severity) + '20', color: sevColor(inc.severity) }}>
                                            {inc.severity}
                                        </span>
                                    </td>
                                    <td style={{ padding: '12px 16px', fontWeight: 500 }}>{inc.title}</td>
                                    <td style={{ padding: '12px 16px' }}>
                                        <span style={{ padding: '4px 10px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600, background: statusColor(inc.status) + '20', color: statusColor(inc.status) }}>
                                            {inc.status}
                                        </span>
                                    </td>
                                    <td style={{ padding: '12px 16px', color: 'var(--text-2)', fontSize: '0.9rem' }}>
                                        {inc.start_at ? new Date(inc.start_at).toLocaleString() : '—'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}
