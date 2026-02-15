import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageShell, GlassCard } from '../../../components/Premium'
import { Table } from '../../../design-system/components/Table'
import { Button } from '../../../design-system/components/Button'
import { Badge } from '../../../design-system/components/Badge'
import { Input, Select } from '../../../design-system/components/Input'
import { Modal, ModalFooter } from '../../../design-system/components/Modal'
import { Users, UserPlus, Check } from 'lucide-react'

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
                method: 'POST', headers,
                body: JSON.stringify({
                    email: newUser.email, full_name: newUser.full_name,
                    role: newUser.role, password: newUser.password || 'TempPass123!'
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
                    <div className="text-xs text-[var(--atum-text-muted)]">{row.email}</div>
                </div>
            )
        },
        { key: 'role', label: 'Role', render: (v) => <Badge variant={roleColors[v] || 'default'}>{v}</Badge> },
        { key: 'is_active', label: 'Status', render: (v) => <Badge variant={v !== false ? 'success' : 'default'}>{v !== false ? 'Active' : 'Disabled'}</Badge> },
        { key: 'email_verified', label: 'Verified', render: (v) => <Badge variant={v ? 'success' : 'warning'} size="sm">{v ? <Check size={12} /> : 'Pending'}</Badge> },
        { key: 'created_at', label: 'Joined', render: (v) => <span className="text-xs">{v ? new Date(v).toLocaleDateString() : '—'}</span> },
    ]

    const tabs = [
        { key: 'users', label: 'Team Members' },
        { key: 'settings', label: 'Org Settings' },
    ]

    return (
        <PageShell
            title="Organization Management"
            subtitle="Manage team members, roles, and organization settings"
            actions={<Button onClick={() => setShowInvite(true)}><UserPlus size={14} className="mr-1" /> Invite Member</Button>}
        >
            {/* Tabs */}
            <div className="flex items-center gap-2 mb-6">
                {tabs.map(t => (
                    <button key={t.key} onClick={() => setActiveTab(t.key)}
                        className={`text-[10px] uppercase tracking-widest font-bold px-3 py-1.5 rounded-full transition-all ${activeTab === t.key
                            ? 'bg-[var(--atum-accent-gold)] text-black'
                            : 'text-[var(--atum-text-muted)] hover:text-white hover:bg-white/5 border border-[var(--atum-border)]'
                            }`}>{t.label}</button>
                ))}
            </div>

            {activeTab === 'users' && (
                <GlassCard>
                    <div className="p-6">
                        {loading ? (
                            <div className="flex items-center justify-center py-16">
                                <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
                            </div>
                        ) : users.length === 0 ? (
                            <div className="text-center py-16 text-[var(--atum-text-muted)]">
                                <Users size={48} className="mx-auto mb-3 opacity-20" />
                                <p className="text-sm">No team members found</p>
                            </div>
                        ) : (
                            <Table columns={columns} data={users} />
                        )}
                        <div className="mt-4 text-[10px] text-[var(--atum-text-muted)] uppercase tracking-widest">
                            {users.length} member{users.length !== 1 ? 's' : ''}
                        </div>
                    </div>
                </GlassCard>
            )}

            {activeTab === 'settings' && (
                <GlassCard>
                    <div className="p-6">
                        <div className="space-y-4">
                            {[
                                { label: 'Organization Name', desc: 'Display name for your organization', value: 'ATUM DESK', badge: null },
                                { label: 'SLA Enforcement', desc: 'Automatically track and enforce SLA targets', badge: { variant: 'success', text: 'Enabled' } },
                                { label: 'AI Copilot', desc: 'Auto-triage, smart replies, and sentiment analysis', badge: { variant: 'success', text: 'Enabled' } },
                                { label: 'RAG Indexing', desc: 'Index tickets for knowledge retrieval', badge: { variant: 'success', text: 'Active' } },
                                { label: '2FA Required', desc: 'Require two-factor authentication for all users', badge: { variant: 'warning', text: 'Optional' } },
                            ].map((setting, i) => (
                                <div key={i} className={`flex items-center justify-between py-3 ${i < 4 ? 'border-b border-[var(--atum-border)]' : ''}`}>
                                    <div>
                                        <div className="font-medium text-white">{setting.label}</div>
                                        <div className="text-xs text-[var(--atum-text-muted)]">{setting.desc}</div>
                                    </div>
                                    {setting.value ? (
                                        <span className="text-sm font-mono text-[var(--atum-accent-gold)]">{setting.value}</span>
                                    ) : (
                                        <Badge variant={setting.badge.variant}>{setting.badge.text}</Badge>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                </GlassCard>
            )}

            {showInvite && (
                <Modal title="Invite Team Member" onClose={() => setShowInvite(false)}>
                    <div className="space-y-4">
                        <Input label="Full Name" value={newUser.full_name}
                            onChange={e => setNewUser(p => ({ ...p, full_name: e.target.value }))} placeholder="Jane Smith" />
                        <Input label="Email" type="email" value={newUser.email}
                            onChange={e => setNewUser(p => ({ ...p, email: e.target.value }))} placeholder="jane@company.com" />
                        <Select label="Role" value={newUser.role}
                            onChange={e => setNewUser(p => ({ ...p, role: e.target.value }))}>
                            <option value="agent">Agent</option>
                            <option value="manager">Manager</option>
                            <option value="admin">Admin</option>
                        </Select>
                        <Input label="Temporary Password" type="password" value={newUser.password}
                            onChange={e => setNewUser(p => ({ ...p, password: e.target.value }))} placeholder="TempPass123!" />
                    </div>
                    <ModalFooter>
                        <Button variant="outline" onClick={() => setShowInvite(false)}>Cancel</Button>
                        <Button onClick={handleInvite} disabled={inviting || !newUser.email || !newUser.full_name}>
                            {inviting ? 'Inviting…' : 'Invite Member'}
                        </Button>
                    </ModalFooter>
                </Modal>
            )}
        </PageShell>
    )
}
