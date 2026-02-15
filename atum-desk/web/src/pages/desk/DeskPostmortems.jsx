import React, { useState, useEffect, useCallback } from 'react'
import { PageShell, GlassCard } from '../../components/Premium'
import { FileText, ClipboardList } from 'lucide-react'

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
        <PageShell title="Postmortems" icon={ClipboardList} subtitle="Root cause analysis & lessons learned from resolved incidents">
            {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm mb-4">{error}</div>
            )}

            <GlassCard>
                {loading ? (
                    <div className="p-10 text-center text-[var(--atum-text-muted)]">Loading postmortems...</div>
                ) : postmortems.length === 0 ? (
                    <div className="p-10 text-center">
                        <FileText size={48} className="mx-auto mb-3 text-[var(--atum-text-muted)]" />
                        <h3 className="font-semibold">No Postmortems Yet</h3>
                        <p className="text-[var(--atum-text-muted)]">Postmortems will appear here after incidents are resolved</p>
                    </div>
                ) : (
                    <div className="flex flex-col gap-3">
                        {postmortems.map(pm => (
                            <div key={pm.id} className="p-4 rounded-lg border border-[var(--atum-border)] bg-[var(--atum-surface-2)]">
                                <div className="flex justify-between items-center mb-2">
                                    <h3 className="font-semibold">{pm.title}</h3>
                                    <span className="badge" style={{
                                        background: pm.severity === 'SEV1' ? '#ef444420' : pm.severity === 'SEV2' ? '#f59e0b20' : '#3b82f620',
                                        color: pm.severity === 'SEV1' ? '#ef4444' : pm.severity === 'SEV2' ? '#f59e0b' : '#3b82f6',
                                    }}>{pm.severity}</span>
                                </div>
                                {pm.customer_impact_summary && (
                                    <p className="text-[var(--atum-text-muted)] text-sm mb-2">{pm.customer_impact_summary}</p>
                                )}
                                <div className="flex gap-4 text-xs text-[var(--atum-text-muted)]">
                                    <span>Started: {pm.start_at ? new Date(pm.start_at).toLocaleDateString() : '—'}</span>
                                    <span>Resolved: {pm.resolved_at ? new Date(pm.resolved_at).toLocaleDateString() : '—'}</span>
                                    <span className="badge badge-new">{pm.status}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </GlassCard>
        </PageShell>
    )
}
