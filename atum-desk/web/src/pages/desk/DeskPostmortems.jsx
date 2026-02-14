import React, { useState, useEffect, useCallback } from 'react'

const API = '/api/v1/incidents'

export default function DeskPostmortems() {
    const [postmortems, setPostmortems] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

    const fetchData = useCallback(async () => {
        try {
            setLoading(true)
            // Fetch resolved/closed incidents that have postmortems
            const res = await fetch(`${API}?status=RESOLVED&limit=50`, { headers })
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            const data = await res.json()
            const resolved = Array.isArray(data) ? data : data.items || []
            setPostmortems(resolved.filter(i => i.status === 'RESOLVED' || i.status === 'CLOSED'))
        } catch (e) {
            setError(e.message)
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => { fetchData() }, [fetchData])

    return (
        <div className="desk-page">
            <div className="desk-page-header">
                <h1>📋 Postmortems</h1>
                <p style={{ color: 'var(--text-2)' }}>Root cause analysis & lessons learned from resolved incidents</p>
            </div>

            {error && (
                <div style={{ padding: '12px 16px', background: '#ef444420', border: '1px solid #ef4444', borderRadius: '8px', marginBottom: '16px', color: '#ef4444' }}>
                    {error}
                </div>
            )}

            <div className="glass-panel" style={{ borderRadius: '12px', border: '1px solid var(--glass-border)', overflow: 'hidden' }}>
                {loading ? (
                    <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-2)' }}>Loading postmortems...</div>
                ) : postmortems.length === 0 ? (
                    <div style={{ padding: '40px', textAlign: 'center' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '12px' }}>📋</div>
                        <h3>No Postmortems Yet</h3>
                        <p style={{ color: 'var(--text-2)' }}>Postmortems will appear here after incidents are resolved</p>
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', padding: '16px' }}>
                        {postmortems.map(pm => (
                            <div
                                key={pm.id}
                                style={{
                                    padding: '16px 20px', borderRadius: '10px',
                                    border: '1px solid var(--glass-border, #333)',
                                    background: 'var(--bg-2, #1a1a2e)',
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                                    <h3 style={{ margin: 0, fontSize: '1rem' }}>{pm.title}</h3>
                                    <span style={{
                                        padding: '4px 10px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700,
                                        background: pm.severity === 'SEV1' ? '#ef444420' : pm.severity === 'SEV2' ? '#f59e0b20' : '#3b82f620',
                                        color: pm.severity === 'SEV1' ? '#ef4444' : pm.severity === 'SEV2' ? '#f59e0b' : '#3b82f6',
                                    }}>
                                        {pm.severity}
                                    </span>
                                </div>
                                {pm.customer_impact_summary && (
                                    <p style={{ color: 'var(--text-2)', fontSize: '0.9rem', margin: '4px 0 8px' }}>
                                        {pm.customer_impact_summary}
                                    </p>
                                )}
                                <div style={{ display: 'flex', gap: '16px', fontSize: '0.8rem', color: 'var(--text-2)' }}>
                                    <span>Started: {pm.start_at ? new Date(pm.start_at).toLocaleDateString() : '—'}</span>
                                    <span>Resolved: {pm.resolved_at ? new Date(pm.resolved_at).toLocaleDateString() : '—'}</span>
                                    <span style={{ padding: '2px 8px', borderRadius: '4px', background: '#22c55e20', color: '#22c55e' }}>
                                        {pm.status}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
