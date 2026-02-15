import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import DeskSidebar from '../../../components/DeskSidebar'
import { Table } from '../../../design-system/components/Table'
import { Button } from '../../../design-system/components/Button'
import { Badge } from '../../../design-system/components/Badge'
import { Input, Select } from '../../../design-system/components/Input'
import { Modal, ModalFooter } from '../../../design-system/components/Modal'

export default function AdminOrgManagement() {
    const navigate = useNavigate()
    const token = localStorage.getItem('atum_desk_token')
    const [users, setUsers] = useState([])
    const [loading, setLoading] = useState(true)
    const [showInvite, setShowInvite] = useState(false)
    const [inviting, setInviting] = useState(false)
    const [newUser, setNewUser] = useState({ email: '', full_name: '', role: 'agent', password: '' })
    const [activeTab, setActiveTab] = useState('users')

    const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }

    useEffect(() => {
        if (!token) { navigate('/desk/login'); return }
        fetchUsers()
    }, [])

    const fetchUsers = useCallback(async () => {
        try {
            const res = await fetch('/api/v1/users', { headers })
            if (res.status === 401) { navigate('/desk/login'); return }
            if (res.ok) {
                const data = await res.json()
                setUsers(Array.isArray(data) ? data : data.items || [])
            }
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }, [token])

    const handleInvite = async () => {
        setInviting(true)
        try {
            const res = await fetch('/api/v1/users', {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    email: newUser.email,
                    full_name: newUser.full_name,
                    role: newUser.role,
                    password: newUser.password || 'TempPass123!'
                })
            })
            if (res.ok) {
                setShowInvite(false)
                setNewUser({ email: '', full_name: '', role: 'agent', password: '' })
                fetchUsers()
            }
        } catch (e) { console.error(e) }
        finally { setInviting(false) }
    }

    const roleColors = { admin: 'error', agent: 'info', customer: 'default', manager: 'warning' }

    const columns = [
        {
            key: 'full_name', label: 'Name', render: (v, row) => (
                <div>
                    <div className="font-medium text-white">{v || '—'}</div>
                    <div className="text-xs text-[var(--text-2)]">{row.email}</div>
                </div>
            )
        },
        { key: 'role', label: 'Role', render: (v) => <Badge variant={roleColors[v] || 'default'}>{v}</Badge> },
        {
            key: 'is_active', label: 'Status', render: (v) => (
                <Badge variant={v !== false ? 'success' : 'default'}>{v !== false ? 'Active' : 'Disabled'}</Badge>
            )
        },
        {
            key: 'email_verified', label: 'Verified', render: (v) => (
                <Badge variant={v ? 'success' : 'warning'} size="sm">{v ? '✓' : 'Pending'}</Badge>
            )
        },
        {
            key: 'created_at', label: 'Joined', render: (v) => (
                <span className="text-xs">{v ? new Date(v).toLocaleDateString() : '—'}</span>
            )
        },
    ]

    const tabs = [
        { key: 'users', label: 'Team Members' },
        { key: 'settings', label: 'Org Settings' },
    ]

    return (
        <div className="flex min-h-screen bg-[var(--bg-0)]">
            <DeskSidebar />
            <div className="flex-1 p-8">
                <div className="max-w-6xl mx-auto">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h1 className="text-2xl font-bold">Organization Management</h1>
                            <p className="text-sm text-[var(--text-2)] mt-1">Manage team members, roles, and organization settings</p>
                        </div>
                        <Button onClick={() => setShowInvite(true)}>+ Invite Member</Button>
                    </div>

                    {/* Tabs */}
                    <div className="flex items-center gap-2 mb-6">
                        {tabs.map(t => (
                            <button
                                key={t.key}
                                onClick={() => setActiveTab(t.key)}
                                className={`text-[10px] uppercase tracking-widest font-bold px-3 py-1.5 rounded-full transition-all ${activeTab === t.key
                                        ? 'bg-[var(--accent-gold)] text-black'
                                        : 'text-[var(--text-2)] hover:text-white hover:bg-white/5 border border-[var(--glass-border)]'
                                    }`}
                            >
                                {t.label}
                            </button>
                        ))}
                    </div>

                    {activeTab === 'users' && (
                        <div className="glass-panel rounded-xl p-6">
                            {loading ? (
                                <div className="flex items-center justify-center py-16"><div className="spinner"></div></div>
                            ) : users.length === 0 ? (
                                <div className="text-center py-16 text-[var(--text-2)]">
                                    <div className="text-4xl mb-3">👥</div>
                                    <p className="text-sm">No team members found</p>
                                </div>
                            ) : (
                                <Table columns={columns} data={users} />
                            )}
                            <div className="mt-4 text-[10px] text-[var(--text-2)] uppercase tracking-widest">
                                {users.length} member{users.length !== 1 ? 's' : ''}
                            </div>
                        </div>
                    )}

                    {activeTab === 'settings' && (
                        <div className="glass-panel rounded-xl p-6">
                            <div className="space-y-4">
                                <div className="flex items-center justify-between py-3 border-b border-[var(--border)]">
                                    <div>
                                        <div className="font-medium text-white">Organization Name</div>
                                        <div className="text-xs text-[var(--text-2)]">Display name for your organization</div>
                                    </div>
                                    <span className="text-sm font-mono text-[var(--accent-gold)]">ATUM DESK</span>
                                </div>
                                <div className="flex items-center justify-between py-3 border-b border-[var(--border)]">
                                    <div>
                                        <div className="font-medium text-white">SLA Enforcement</div>
                                        <div className="text-xs text-[var(--text-2)]">Automatically track and enforce SLA targets</div>
                                    </div>
                                    <Badge variant="success">Enabled</Badge>
                                </div>
                                <div className="flex items-center justify-between py-3 border-b border-[var(--border)]">
                                    <div>
                                        <div className="font-medium text-white">AI Copilot</div>
                                        <div className="text-xs text-[var(--text-2)]">Auto-triage, smart replies, and sentiment analysis</div>
                                    </div>
                                    <Badge variant="success">Enabled</Badge>
                                </div>
                                <div className="flex items-center justify-between py-3 border-b border-[var(--border)]">
                                    <div>
                                        <div className="font-medium text-white">RAG Indexing</div>
                                        <div className="text-xs text-[var(--text-2)]">Index tickets for knowledge retrieval</div>
                                    </div>
                                    <Badge variant="success">Active</Badge>
                                </div>
                                <div className="flex items-center justify-between py-3">
                                    <div>
                                        <div className="font-medium text-white">2FA Required</div>
                                        <div className="text-xs text-[var(--text-2)]">Require two-factor authentication for all users</div>
                                    </div>
                                    <Badge variant="warning">Optional</Badge>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Invite Modal */}
            {showInvite && (
                <Modal title="Invite Team Member" onClose={() => setShowInvite(false)}>
                    <div className="space-y-4">
                        <Input label="Full Name" value={newUser.full_name}
                            onChange={e => setNewUser(p => ({ ...p, full_name: e.target.value }))}
                            placeholder="Jane Smith" />
                        <Input label="Email" type="email" value={newUser.email}
                            onChange={e => setNewUser(p => ({ ...p, email: e.target.value }))}
                            placeholder="jane@company.com" />
                        <Select label="Role" value={newUser.role}
                            onChange={e => setNewUser(p => ({ ...p, role: e.target.value }))}>
                            <option value="agent">Agent</option>
                            <option value="manager">Manager</option>
                            <option value="admin">Admin</option>
                        </Select>
                        <Input label="Temporary Password" type="password" value={newUser.password}
                            onChange={e => setNewUser(p => ({ ...p, password: e.target.value }))}
                            placeholder="TempPass123!" />
                    </div>
                    <ModalFooter>
                        <Button variant="outline" onClick={() => setShowInvite(false)}>Cancel</Button>
                        <Button onClick={handleInvite} disabled={inviting || !newUser.email || !newUser.full_name}>
                            {inviting ? 'Inviting…' : 'Invite Member'}
                        </Button>
                    </ModalFooter>
                </Modal>
            )}
        </div>
    )
}
