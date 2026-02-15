import React, { useState, useEffect } from 'react'
import { PageShell, GlassCard } from '../../components/Premium'
import { FileText, Download, ChevronLeft, ChevronRight, Filter } from 'lucide-react'

export default function DeskAuditLog() {
    const [logs, setLogs] = useState([])
    const [loading, setLoading] = useState(true)
    const [filters, setFilters] = useState({ action: '', user: '', dateFrom: '', dateTo: '' })
    const [page, setPage] = useState(0)
    const [total, setTotal] = useState(0)
    const PAGE_SIZE = 50

    useEffect(() => {
        loadAuditLogs()
    }, [page])

    const loadAuditLogs = async () => {
        setLoading(true)
        try {
            const token = localStorage.getItem('atum_desk_token')
            const params = new URLSearchParams({ limit: PAGE_SIZE, offset: page * PAGE_SIZE })
            if (filters.action) params.append('action', filters.action)
            if (filters.dateFrom) params.append('from', filters.dateFrom)
            if (filters.dateTo) params.append('to', filters.dateTo)

            const response = await fetch(`/api/v1/audit?${params}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setLogs(data.items || [])
                setTotal(data.total || data.items?.length || 0)
            }
        } catch (err) {
            console.error('Failed to load audit logs:', err)
        } finally {
            setLoading(false)
        }
    }

    const applyFilters = () => {
        setPage(0)
        loadAuditLogs()
    }

    const exportCSV = async () => {
        try {
            const token = localStorage.getItem('atum_desk_token')
            const res = await fetch('/api/v1/audit/export?format=csv', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                const blob = await res.blob()
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `audit-log-${new Date().toISOString().slice(0, 10)}.csv`
                a.click()
                URL.revokeObjectURL(url)
            } else {
                const csv = [
                    'Timestamp,Action,Entity Type,Entity ID,User,IP Address',
                    ...logs.map(l =>
                        `"${new Date(l.created_at).toISOString()}","${l.action}","${l.entity_type}","${l.entity_id || ''}","${l.user_email || 'System'}","${l.ip_address || ''}"`
                    )
                ].join('\n')
                const blob = new Blob([csv], { type: 'text/csv' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `audit-log-${new Date().toISOString().slice(0, 10)}.csv`
                a.click()
                URL.revokeObjectURL(url)
            }
        } catch (e) { console.error('Export failed:', e) }
    }

    const totalPages = Math.ceil(total / PAGE_SIZE)

    return (
        <PageShell
            title="Audit Log"
            subtitle="Complete activity trail"
            actions={
                <button onClick={exportCSV} className="btn-gold flex items-center gap-2">
                    <Download size={16} /> Export CSV
                </button>
            }
        >
            {/* Filters */}
            <GlassCard className="mb-6">
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4 p-4">
                    <input type="text" placeholder="Filter by action..." className="atum-input"
                        value={filters.action} onChange={(e) => setFilters({ ...filters, action: e.target.value })} />
                    <input type="text" placeholder="Filter by user..." className="atum-input"
                        value={filters.user} onChange={(e) => setFilters({ ...filters, user: e.target.value })} />
                    <input type="date" className="atum-input"
                        value={filters.dateFrom} onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })} />
                    <input type="date" className="atum-input"
                        value={filters.dateTo} onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })} />
                    <button onClick={applyFilters} className="btn-gold flex items-center justify-center gap-2">
                        <Filter size={14} /> Apply
                    </button>
                </div>
            </GlassCard>

            {/* Table */}
            <GlassCard className="p-0 overflow-hidden">
                {loading ? (
                    <div className="flex items-center justify-center py-24">
                        <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
                    </div>
                ) : logs.length === 0 ? (
                    <div className="text-center py-24 text-[var(--atum-text-muted)]">
                        <FileText size={48} className="mx-auto mb-4 opacity-20" />
                        <p className="text-sm">No audit logs found</p>
                    </div>
                ) : (
                    <table className="glass-table">
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Action</th>
                                <th>Entity</th>
                                <th>User</th>
                                <th>IP Address</th>
                            </tr>
                        </thead>
                        <tbody>
                            {logs.map((log) => (
                                <tr key={log.id}>
                                    <td className="text-xs">
                                        {new Date(log.created_at).toLocaleString()}
                                    </td>
                                    <td>
                                        <span className="badge badge-open text-xs">{log.action}</span>
                                    </td>
                                    <td className="text-xs">
                                        {log.entity_type}: {log.entity_id?.substring(0, 8)}...
                                    </td>
                                    <td className="text-xs">{log.user_email || 'System'}</td>
                                    <td className="text-xs text-[var(--atum-text-muted)]">
                                        {log.ip_address || '-'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </GlassCard>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-between mt-4">
                    <span className="text-xs text-[var(--atum-text-muted)]">
                        Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, total)} of {total}
                    </span>
                    <div className="flex gap-2">
                        <button disabled={page === 0} onClick={() => setPage(page - 1)}
                            className="btn-outline flex items-center gap-1 text-xs disabled:opacity-30">
                            <ChevronLeft size={14} /> Previous
                        </button>
                        <span className="text-xs text-[var(--atum-text-muted)] py-1.5">Page {page + 1} of {totalPages}</span>
                        <button disabled={page >= totalPages - 1} onClick={() => setPage(page + 1)}
                            className="btn-outline flex items-center gap-1 text-xs disabled:opacity-30">
                            Next <ChevronRight size={14} />
                        </button>
                    </div>
                </div>
            )}
        </PageShell>
    )
}
