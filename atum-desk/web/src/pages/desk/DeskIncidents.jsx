import React, { useState, useEffect, useCallback } from 'react'
import { PageShell, GlassCard } from '../../components/Premium'
import { Siren, CheckCircle, Plus, X } from 'lucide-react'
import ActivityTimeline from '../../components/ActivityTimeline'

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
        <PageShell title="Incidents" icon={Siren} subtitle="Major incident tracking & management"
            actions={<button onClick={() => setShowCreate(!showCreate)} className="btn-gold flex items-center gap-2">{showCreate ? <><X size={16} /> Cancel</> : <><Plus size={16} /> Declare Incident</>}</button>}>

            {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm mb-4">{error}</div>
            )}

            {showCreate && (
                <GlassCard className="mb-6">
                    <h3 className="font-semibold mb-4">Declare New Incident</h3>
                    <form onSubmit={handleCreate} className="flex flex-col gap-3">
                        <input placeholder="Incident title..." value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} required className="atum-input" />
                        <select value={form.severity} onChange={e => setForm({ ...form, severity: e.target.value })} className="atum-input">
                            <option value="SEV1">SEV-1 (Critical)</option>
                            <option value="SEV2">SEV-2 (High)</option>
                            <option value="SEV3">SEV-3 (Medium)</option>
                            <option value="SEV4">SEV-4 (Low)</option>
                        </select>
                        <textarea placeholder="Customer impact summary..." value={form.customer_impact_summary} onChange={e => setForm({ ...form, customer_impact_summary: e.target.value })} rows={3} className="atum-input" style={{ resize: 'vertical' }} />
                        <button type="submit" className="btn-gold flex items-center justify-center gap-2"><Siren size={16} /> Declare Incident</button>
                    </form>
                </GlassCard>
            )}

            <GlassCard>
                {loading ? (
                    <div className="p-10 text-center text-[var(--atum-text-muted)]">Loading incidents...</div>
                ) : incidents.length === 0 ? (
                    <div className="p-10 text-center">
                        <CheckCircle size={48} className="mx-auto mb-3 text-green-400" />
                        <h3 className="font-semibold">No Active Incidents</h3>
                        <p className="text-[var(--atum-text-muted)]">All systems operational</p>
                    </div>
                ) : (
                    <table className="glass-table">
                        <thead><tr><th>Severity</th><th>Title</th><th>Status</th><th>Started</th></tr></thead>
                        <tbody>
                            {incidents.map(inc => (
                                <tr key={inc.id}>
                                    <td><span className="badge" style={{ background: sevColor(inc.severity) + '20', color: sevColor(inc.severity) }}>{inc.severity}</span></td>
                                    <td className="font-medium">{inc.title}</td>
                                    <td><span className="badge" style={{ background: statusColor(inc.status) + '20', color: statusColor(inc.status) }}>{inc.status}</span></td>
                                    <td className="text-[var(--atum-text-muted)] text-sm">{inc.start_at ? new Date(inc.start_at).toLocaleString() : '—'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </GlassCard>

            {/* Incident Activity Timeline */}
            {incidents.length > 0 && (
                <GlassCard title="Incident Activity" className="mt-6">
                    <ActivityTimeline events={incidents.slice(0, 10).map(inc => ({
                        id: inc.id,
                        type: inc.severity === 'SEV1' ? 'error' : inc.severity === 'SEV2' ? 'warning' : 'info',
                        title: inc.title,
                        description: `${inc.severity} — ${inc.status}${inc.customer_impact_summary ? ': ' + inc.customer_impact_summary : ''}`,
                        timestamp: inc.start_at || inc.created_at,
                        badge: inc.status
                    }))} />
                </GlassCard>
            )}
        </PageShell>
    )
}
