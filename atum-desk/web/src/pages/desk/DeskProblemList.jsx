import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageShell, GlassCard } from '../../components/Premium'
import { Puzzle, Plus } from 'lucide-react'

export default function DeskProblemList() {
    const navigate = useNavigate()
    const token = localStorage.getItem('atum_desk_token')
    const [problems, setProblems] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!token) { navigate('/desk/login'); return }
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const res = await fetch('/api/v1/problems', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.status === 401) { navigate('/desk/login'); return }
            if (res.ok) {
                const data = await res.json()
                setProblems(Array.isArray(data) ? data : [])
            }
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    return (
        <PageShell
            title="Problem Management"
            subtitle="Root Cause Analysis & Recurring Incidents"
            actions={
                <button className="btn-gold flex items-center gap-2" onClick={() => alert('Create Problem - Coming Soon')}>
                    <Plus size={16} /> New Problem
                </button>
            }
        >
            <GlassCard className="p-0 overflow-hidden">
                {loading ? (
                    <div className="flex items-center justify-center py-24">
                        <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
                    </div>
                ) : problems.length === 0 ? (
                    <div className="text-center py-24 text-[var(--atum-text-muted)]">
                        <Puzzle size={48} className="mx-auto mb-4 opacity-20" />
                        <p className="text-sm">No problems recorded yet.</p>
                    </div>
                ) : (
                    <table className="glass-table">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Status</th>
                                <th>Severity</th>
                                <th>Last Updated</th>
                            </tr>
                        </thead>
                        <tbody>
                            {problems.map(p => (
                                <tr key={p.id} className="cursor-pointer">
                                    <td className="font-medium text-white">{p.title}</td>
                                    <td><span className="badge badge-assigned">{p.status}</span></td>
                                    <td><span className="badge badge-high">{p.severity}</span></td>
                                    <td className="text-xs text-[var(--atum-text-muted)]">
                                        {new Date(p.updated_at).toLocaleDateString()}
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
