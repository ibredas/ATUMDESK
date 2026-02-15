import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import DeskSidebar from '../../../components/DeskSidebar'
import { Table } from '../../../design-system/components/Table'
import { Button } from '../../../design-system/components/Button'
import { Badge } from '../../../design-system/components/Badge'
import { Input, Textarea, Select } from '../../../design-system/components/Input'
import { Modal, ModalFooter } from '../../../design-system/components/Modal'

const API = '/api/v1/forms/services'

export default function AdminFormsStudio() {
    const navigate = useNavigate()
    const token = localStorage.getItem('atum_desk_token')
    const [forms, setForms] = useState([])
    const [loading, setLoading] = useState(true)
    const [showCreate, setShowCreate] = useState(false)
    const [creating, setCreating] = useState(false)
    const [newForm, setNewForm] = useState({ name: '', description: '', category: 'general', fields: '[]' })

    const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }

    useEffect(() => {
        if (!token) { navigate('/desk/login'); return }
        fetchForms()
    }, [])

    const fetchForms = useCallback(async () => {
        try {
            const res = await fetch(API, { headers })
            if (res.ok) {
                const data = await res.json()
                setForms(Array.isArray(data) ? data : data.items || [])
            }
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }, [token])

    const handleCreate = async () => {
        setCreating(true)
        try {
            let parsedFields = []
            try { parsedFields = JSON.parse(newForm.fields) } catch { parsedFields = [] }

            const res = await fetch(API, {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    name: newForm.name,
                    description: newForm.description,
                    category: newForm.category,
                    fields: parsedFields,
                    is_active: true
                })
            })
            if (res.ok) {
                setShowCreate(false)
                setNewForm({ name: '', description: '', category: 'general', fields: '[]' })
                fetchForms()
            }
        } catch (e) { console.error(e) }
        finally { setCreating(false) }
    }

    const handleDelete = async (id) => {
        if (!confirm('Delete this form template?')) return
        try {
            await fetch(`${API}/${id}`, { method: 'DELETE', headers })
            fetchForms()
        } catch (e) { console.error(e) }
    }

    const columns = [
        { key: 'name', label: 'Form Name', render: (v) => <span className="font-medium text-white">{v}</span> },
        { key: 'category', label: 'Category', render: (v) => <Badge variant="info">{v || 'general'}</Badge> },
        { key: 'description', label: 'Description', render: (v) => <span className="text-xs max-w-[200px] truncate block">{v || '—'}</span> },
        { key: 'is_active', label: 'Status', render: (v) => <Badge variant={v ? 'success' : 'default'}>{v ? 'Active' : 'Disabled'}</Badge> },
        { key: 'created_at', label: 'Created', render: (v) => <span className="text-xs">{v ? new Date(v).toLocaleDateString() : '—'}</span> },
        {
            key: 'id', label: '', render: (v) => (
                <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); handleDelete(v) }}>🗑</Button>
            )
        },
    ]

    return (
        <div className="flex min-h-screen bg-[var(--bg-0)]">
            <DeskSidebar />
            <div className="flex-1 p-8">
                <div className="max-w-6xl mx-auto">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h1 className="text-2xl font-bold">Forms Studio</h1>
                            <p className="text-sm text-[var(--text-2)] mt-1">Create and manage service request form templates</p>
                        </div>
                        <Button onClick={() => setShowCreate(true)}>+ New Form</Button>
                    </div>

                    <div className="glass-panel rounded-xl p-6">
                        {loading ? (
                            <div className="flex items-center justify-center py-16"><div className="spinner"></div></div>
                        ) : forms.length === 0 ? (
                            <div className="text-center py-16 text-[var(--text-2)]">
                                <div className="text-4xl mb-3">📝</div>
                                <p className="text-sm">No form templates yet</p>
                                <Button variant="outline" className="mt-4" onClick={() => setShowCreate(true)}>Create First Form</Button>
                            </div>
                        ) : (
                            <Table columns={columns} data={forms} />
                        )}
                    </div>

                    <div className="mt-4 text-[10px] text-[var(--text-2)] uppercase tracking-widest">
                        {forms.length} form{forms.length !== 1 ? 's' : ''}
                    </div>
                </div>
            </div>

            {/* Create Modal */}
            {showCreate && (
                <Modal title="Create Form Template" onClose={() => setShowCreate(false)}>
                    <div className="space-y-4">
                        <Input label="Form Name" value={newForm.name}
                            onChange={e => setNewForm(p => ({ ...p, name: e.target.value }))}
                            placeholder="e.g. VPN Access Request" />
                        <Textarea label="Description" value={newForm.description}
                            onChange={e => setNewForm(p => ({ ...p, description: e.target.value }))}
                            placeholder="What is this form for?" rows={2} />
                        <Select label="Category" value={newForm.category}
                            onChange={e => setNewForm(p => ({ ...p, category: e.target.value }))}>
                            <option value="general">General</option>
                            <option value="it_support">IT Support</option>
                            <option value="hr">HR</option>
                            <option value="access_request">Access Request</option>
                            <option value="onboarding">Onboarding</option>
                        </Select>
                        <Textarea label="Fields (JSON)" value={newForm.fields}
                            onChange={e => setNewForm(p => ({ ...p, fields: e.target.value }))}
                            placeholder='[{"name":"reason","type":"text","required":true}]' rows={3}
                            className="font-mono text-xs" />
                    </div>
                    <ModalFooter>
                        <Button variant="outline" onClick={() => setShowCreate(false)}>Cancel</Button>
                        <Button onClick={handleCreate} disabled={creating || !newForm.name}>
                            {creating ? 'Creating…' : 'Create Form'}
                        </Button>
                    </ModalFooter>
                </Modal>
            )}
        </div>
    )
}
