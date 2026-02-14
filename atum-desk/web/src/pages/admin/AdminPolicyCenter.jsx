import React, { useState, useEffect, useCallback } from 'react'

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
            await fetch(`${API}/${id}`, {
                method: 'PUT', headers,
                body: JSON.stringify({ enabled: !enabled })
            })
            fetchPolicies()
        } catch (e) {
            setError(e.message)
        }
    }

    return (
        <div className="desk-page">
            <div className="desk-page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1>🛡️ Policy Center</h1>
                    <p style={{ color: 'var(--text-2)' }}>Manage access control & automation policies</p>
                </div>
                <button
                    onClick={() => setShowCreate(!showCreate)}
                    style={{
                        padding: '10px 20px', borderRadius: '8px', border: 'none', cursor: 'pointer',
                        background: 'var(--accent, #c9a227)', color: '#000', fontWeight: 600
                    }}
                >
                    {showCreate ? 'Cancel' : '+ New Policy'}
                </button>
            </div>

            {error && (
                <div style={{ padding: '12px 16px', background: '#ef444420', border: '1px solid #ef4444', borderRadius: '8px', marginBottom: '16px', color: '#ef4444' }}>
                    {error}
                </div>
            )}

            {showCreate && (
                <div className="glass-panel" style={{ padding: '24px', borderRadius: '12px', marginBottom: '16px', border: '1px solid var(--glass-border)' }}>
                    <h3 style={{ marginBottom: '16px' }}>Create Policy Rule</h3>
                    <form onSubmit={handleCreate} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                        <input
                            placeholder="Policy name..."
                            value={form.name}
                            onChange={e => setForm({ ...form, name: e.target.value })}
                            required
                            style={{ gridColumn: '1 / -1', padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'var(--bg-2, #1a1a2e)', color: 'var(--text-1)' }}
                        />
                        <select value={form.target} onChange={e => setForm({ ...form, target: e.target.value })}
                            style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'var(--bg-2, #1a1a2e)', color: 'var(--text-1)' }}>
                            <option value="ticket">Ticket</option>
                            <option value="kb_article">KB Article</option>
                            <option value="incident">Incident</option>
                            <option value="asset">Asset</option>
                            <option value="user">User</option>
                        </select>
                        <select value={form.action} onChange={e => setForm({ ...form, action: e.target.value })}
                            style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'var(--bg-2, #1a1a2e)', color: 'var(--text-1)' }}>
                            <option value="create">Create</option>
                            <option value="read">Read</option>
                            <option value="update">Update</option>
                            <option value="delete">Delete</option>
                            <option value="assign">Assign</option>
                            <option value="escalate">Escalate</option>
                        </select>
                        <select value={form.effect} onChange={e => setForm({ ...form, effect: e.target.value })}
                            style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'var(--bg-2, #1a1a2e)', color: 'var(--text-1)' }}>
                            <option value="allow">Allow</option>
                            <option value="deny">Deny</option>
                        </select>
                        <input type="number" placeholder="Priority (1-1000)" value={form.priority}
                            onChange={e => setForm({ ...form, priority: parseInt(e.target.value) || 100 })}
                            style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'var(--bg-2, #1a1a2e)', color: 'var(--text-1)' }}
                        />
                        <button type="submit" style={{ gridColumn: '1 / -1', padding: '10px', borderRadius: '8px', border: 'none', background: 'var(--accent, #c9a227)', color: '#000', fontWeight: 600, cursor: 'pointer' }}>
                            Create Policy
                        </button>
                    </form>
                </div>
            )}

            <div className="glass-panel" style={{ borderRadius: '12px', border: '1px solid var(--glass-border)', overflow: 'hidden' }}>
                {loading ? (
                    <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-2)' }}>Loading policies...</div>
                ) : policies.length === 0 ? (
                    <div style={{ padding: '40px', textAlign: 'center' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '12px' }}>🛡️</div>
                        <h3>No Policies Defined</h3>
                        <p style={{ color: 'var(--text-2)' }}>Create your first policy rule to get started</p>
                    </div>
                ) : (
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid var(--glass-border)' }}>
                                <th style={{ padding: '12px 16px', textAlign: 'left' }}>Name</th>
                                <th style={{ padding: '12px 16px', textAlign: 'left' }}>Target</th>
                                <th style={{ padding: '12px 16px', textAlign: 'left' }}>Action</th>
                                <th style={{ padding: '12px 16px', textAlign: 'left' }}>Effect</th>
                                <th style={{ padding: '12px 16px', textAlign: 'left' }}>Priority</th>
                                <th style={{ padding: '12px 16px', textAlign: 'left' }}>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {policies.map(p => (
                                <tr key={p.id} style={{ borderBottom: '1px solid var(--glass-border, #333)' }}>
                                    <td style={{ padding: '12px 16px', fontWeight: 500 }}>{p.name}</td>
                                    <td style={{ padding: '12px 16px' }}>
                                        <span style={{ padding: '3px 8px', borderRadius: '4px', fontSize: '0.8rem', background: 'var(--bg-2, #1a1a2e)' }}>
                                            {p.target}
                                        </span>
                                    </td>
                                    <td style={{ padding: '12px 16px', fontSize: '0.9rem' }}>{p.action}</td>
                                    <td style={{ padding: '12px 16px' }}>
                                        <span style={{
                                            padding: '3px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600,
                                            background: p.effect === 'allow' ? '#22c55e20' : '#ef444420',
                                            color: p.effect === 'allow' ? '#22c55e' : '#ef4444'
                                        }}>
                                            {p.effect?.toUpperCase()}
                                        </span>
                                    </td>
                                    <td style={{ padding: '12px 16px', color: 'var(--text-2)' }}>{p.priority}</td>
                                    <td style={{ padding: '12px 16px' }}>
                                        <button
                                            onClick={() => togglePolicy(p.id, p.enabled)}
                                            style={{
                                                padding: '4px 12px', borderRadius: '12px', border: 'none', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600,
                                                background: p.enabled ? '#22c55e20' : '#6b728020',
                                                color: p.enabled ? '#22c55e' : '#6b7280'
                                            }}
                                        >
                                            {p.enabled ? '● Active' : '○ Disabled'}
                                        </button>
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
