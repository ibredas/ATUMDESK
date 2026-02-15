import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageShell, GlassCard } from '../../components/Premium'
import { GitBranch, Plus } from 'lucide-react'

export default function DeskChangeList() {
    const navigate = useNavigate()
    const token = localStorage.getItem('atum_desk_token')
    const [changes, setChanges] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!token) { navigate('/desk/login'); return }
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const res = await fetch('/api/v1/changes', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.status === 401) { navigate('/desk/login'); return }
            if (res.ok) {
                const data = await res.json()
                setChanges(Array.isArray(data) ? data : [])
            }
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    return (
        <PageShell
            title="Change Management"
            subtitle="Approvals & Deployments"
            actions={
                <button className="btn-gold flex items-center gap-2" onClick={() => alert('Create Change - Coming Soon')}>
                    <Plus size={16} /> New Change
                </button>
            }
        >
            <GlassCard className="p-0 overflow-hidden">
                {loading ? (
                    <div className="flex items-center justify-center py-24">
                        <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
                    </div>
                ) : changes.length === 0 ? (
                    <div className="text-center py-24 text-[var(--atum-text-muted)]">
                        <GitBranch size={48} className="mx-auto mb-4 opacity-20" />
                        <p className="text-sm">No change requests found.</p>
                    </div>
                ) : (
                    <table className="glass-table">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Type</th>
                                <th>Risk</th>
                                <th>Status</th>
                                <th>Planned Start</th>
                            </tr>
                        </thead>
                        <tbody>
                            {changes.map(c => (
                                <tr key={c.id} className="cursor-pointer">
                                    <td className="font-medium text-white">{c.title}</td>
                                    <td><span className="uppercase text-xs tracking-wider">{c.type}</span></td>
                                    <td>{c.risk_level}</td>
                                    <td><span className="badge badge-assigned">{c.status}</span></td>
                                    <td className="text-xs text-[var(--atum-text-muted)]">
                                        {c.planned_start ? new Date(c.planned_start).toLocaleDateString() : 'TBD'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </GlassCard>
        </PageShell>
    )
}
