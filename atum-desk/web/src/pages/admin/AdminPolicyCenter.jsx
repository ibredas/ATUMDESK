import React, { useState, useEffect, useCallback } from 'react'
import { PageShell, GlassCard } from '../../components/Premium'
import { Shield, Plus, X, ToggleLeft, ToggleRight } from 'lucide-react'

const API = '/api/v1/policies'

export default function AdminPolicyCenter() {
    const [policies, setPolicies] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [showCreate, setShowCreate] = useState(false)
    const [form, setForm] = useState({ name: '', target: 'ticket', action: 'create', effect: 'allow', priority: 100 })

    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

    const fetchPolicies = useCallback(async () => {
        try {
            setLoading(true)
            const res = await fetch(API, { headers })
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            const data = await res.json()
            setPolicies(Array.isArray(data) ? data : data.items || [])
        } catch (e) {
            setError(e.message)
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => { fetchPolicies() }, [fetchPolicies])

    const handleCreate = async (e) => {
        e.preventDefault()
        try {
            const res = await fetch(API, { method: 'POST', headers, body: JSON.stringify(form) })
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            setShowCreate(false)
            setForm({ name: '', target: 'ticket', action: 'create', effect: 'allow', priority: 100 })
            fetchPolicies()
        } catch (e) {
            setError(e.message)
        }
    }

    const togglePolicy = async (id, enabled) => {
        try {
            await fetch(`${API}/${id}`, { method: 'PUT', headers, body: JSON.stringify({ enabled: !enabled }) })
            fetchPolicies()
        } catch (e) {
            setError(e.message)
        }
    }

    return (
        <PageShell title="Policy Center" icon={Shield} subtitle="Manage access control & automation policies"
            actions={<button onClick={() => setShowCreate(!showCreate)} className="btn-gold flex items-center gap-2">{showCreate ? <><X size={16} /> Cancel</> : <><Plus size={16} /> New Policy</>}</button>}>

            {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm mb-4">{error}</div>
            )}

            {showCreate && (
                <GlassCard className="mb-6">
                    <h3 className="font-semibold mb-4">Create Policy Rule</h3>
                    <form onSubmit={handleCreate} className="grid grid-cols-2 gap-3">
                        <input placeholder="Policy name..." value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required className="atum-input col-span-2" />
                        <select value={form.target} onChange={e => setForm({ ...form, target: e.target.value })} className="atum-input">
                            <option value="ticket">Ticket</option><option value="kb_article">KB Article</option><option value="incident">Incident</option><option value="asset">Asset</option><option value="user">User</option>
                        </select>
                        <select value={form.action} onChange={e => setForm({ ...form, action: e.target.value })} className="atum-input">
                            <option value="create">Create</option><option value="read">Read</option><option value="update">Update</option><option value="delete">Delete</option><option value="assign">Assign</option><option value="escalate">Escalate</option>
                        </select>
                        <select value={form.effect} onChange={e => setForm({ ...form, effect: e.target.value })} className="atum-input">
                            <option value="allow">Allow</option><option value="deny">Deny</option>
                        </select>
                        <input type="number" placeholder="Priority (1-1000)" value={form.priority} onChange={e => setForm({ ...form, priority: parseInt(e.target.value) || 100 })} className="atum-input" />
                        <button type="submit" className="btn-gold col-span-2">Create Policy</button>
                    </form>
                </GlassCard>
            )}

            <GlassCard>
                {loading ? (
                    <div className="p-10 text-center text-[var(--atum-text-muted)]">Loading policies...</div>
                ) : policies.length === 0 ? (
                    <div className="p-10 text-center">
                        <Shield size={48} className="mx-auto mb-3 text-[var(--atum-text-muted)]" />
                        <h3 className="font-semibold">No Policies Defined</h3>
                        <p className="text-[var(--atum-text-muted)]">Create your first policy rule to get started</p>
                    </div>
                ) : (
                    <table className="glass-table">
                        <thead><tr><th>Name</th><th>Target</th><th>Action</th><th>Effect</th><th>Priority</th><th>Status</th></tr></thead>
                        <tbody>
                            {policies.map(p => (
                                <tr key={p.id}>
                                    <td className="font-medium">{p.name}</td>
                                    <td><span className="badge">{p.target}</span></td>
                                    <td>{p.action}</td>
                                    <td><span className="badge" style={{ background: p.effect === 'allow' ? '#22c55e20' : '#ef444420', color: p.effect === 'allow' ? '#22c55e' : '#ef4444' }}>{p.effect?.toUpperCase()}</span></td>
                                    <td className="text-[var(--atum-text-muted)]">{p.priority}</td>
                                    <td>
                                        <button onClick={() => togglePolicy(p.id, p.enabled)} className="flex items-center gap-1 text-sm">
                                            {p.enabled ? <ToggleRight size={18} className="text-green-400" /> : <ToggleLeft size={18} className="text-gray-500" />}
                                            {p.enabled ? 'Active' : 'Disabled'}
                                        </button>
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
