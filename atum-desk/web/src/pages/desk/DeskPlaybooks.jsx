import React, { useState, useEffect } from 'react'
import { PageShell, GlassCard } from '../../components/Premium'
import { BookMarked, Plus, AlertOctagon, KeyRound, Server, ShieldAlert, Eye } from 'lucide-react'

export default function DeskPlaybooks() {
    const [playbooks, setPlaybooks] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => { loadPlaybooks() }, [])

    const loadPlaybooks = async () => {
        try {
            const token = localStorage.getItem('atum_desk_token')
            const response = await fetch('/api/v1/playbooks', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setPlaybooks(data)
            }
        } catch (err) {
            setError('Failed to load playbooks')
        } finally {
            setLoading(false)
        }
    }

    return (
        <PageShell title="Playbooks / Runbooks" icon={BookMarked}
            actions={<button className="btn-gold flex items-center gap-2"><Plus size={16} /> Create Playbook</button>}>

            {loading ? (
                <div className="text-[var(--atum-text-muted)]">Loading playbooks...</div>
            ) : error ? (
                <div className="text-red-400">{error}</div>
            ) : playbooks.length === 0 ? (
                <GlassCard className="text-center py-8">
                    <BookMarked size={48} className="mx-auto mb-4 text-[var(--atum-text-muted)]" />
                    <h3 className="text-lg font-medium mb-2">No Playbooks Yet</h3>
                    <p className="text-[var(--atum-text-muted)] mb-4">Create incident response playbooks to guide your team through common scenarios.</p>
                    <button className="btn-gold">Create Your First Playbook</button>
                </GlassCard>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {playbooks.map((playbook) => (
                        <GlassCard key={playbook.id}>
                            <h3 className="font-semibold mb-2">{playbook.name}</h3>
                            <p className="text-sm text-[var(--atum-text-muted)] mb-4">{playbook.description || 'No description'}</p>
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-[var(--atum-text-muted)]">{playbook.steps?.length || 0} steps</span>
                                <button className="text-[var(--atum-accent-gold)] hover:underline flex items-center gap-1"><Eye size={14} /> View</button>
                            </div>
                        </GlassCard>
                    ))}
                </div>
            )}

            <div className="mt-8">
                <h2 className="text-lg font-semibold mb-4">Quick Start Templates</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <GlassCard>
                        <h3 className="font-medium mb-2 flex items-center gap-2"><AlertOctagon size={16} className="text-red-400" /> Incident Response</h3>
                        <p className="text-sm text-[var(--atum-text-muted)]">Standard incident response workflow with escalation steps</p>
                    </GlassCard>
                    <GlassCard>
                        <h3 className="font-medium mb-2 flex items-center gap-2"><KeyRound size={16} className="text-blue-400" /> Password Reset</h3>
                        <p className="text-sm text-[var(--atum-text-muted)]">Guided password reset verification process</p>
                    </GlassCard>
                    <GlassCard>
                        <h3 className="font-medium mb-2 flex items-center gap-2"><Server size={16} className="text-orange-400" /> Server Outage</h3>
                        <p className="text-sm text-[var(--atum-text-muted)]">Server outage troubleshooting and communication steps</p>
                    </GlassCard>
                    <GlassCard>
                        <h3 className="font-medium mb-2 flex items-center gap-2"><ShieldAlert size={16} className="text-purple-400" /> Security Breach</h3>
                        <p className="text-sm text-[var(--atum-text-muted)]">Security incident containment and reporting steps</p>
                    </GlassCard>
                </div>
            </div>
        </PageShell>
    )
}
