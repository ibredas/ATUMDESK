import React, { useState, useEffect } from 'react'

export default function DeskAuditLog() {
    const [logs, setLogs] = useState([])
    const [loading, setLoading] = useState(true)
    const [filters, setFilters] = useState({ action: '', user: '', dateFrom: '', dateTo: '' })

    useEffect(() => {
        loadAuditLogs()
    }, [])

    const loadAuditLogs = async () => {
        try {
            const token = localStorage.getItem('atum_desk_token')
            const response = await fetch('/api/v1/audit?limit=100', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setLogs(data.items || [])
            }
        } catch (err) {
            console.error('Failed to load audit logs:', err)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-6">Audit Log</h1>
            
            {/* Filters */}
            <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <input
                        type="text"
                        placeholder="Filter by action..."
                        className="px-3 py-2 bg-[var(--bg)] border border-[var(--border)] rounded"
                        value={filters.action}
                        onChange={(e) => setFilters({...filters, action: e.target.value})}
                    />
                    <input
                        type="date"
                        className="px-3 py-2 bg-[var(--bg)] border border-[var(--border)] rounded"
                        value={filters.dateFrom}
                        onChange={(e) => setFilters({...filters, dateFrom: e.target.value})}
                    />
                    <input
                        type="date"
                        className="px-3 py-2 bg-[var(--bg)] border border-[var(--border)] rounded"
                        value={filters.dateTo}
                        onChange={(e) => setFilters({...filters, dateTo: e.target.value})}
                    />
                    <button className="px-4 py-2 bg-[var(--accent-gold)] text-black rounded font-medium">
                        Apply Filters
                    </button>
                </div>
            </div>

            {/* Table */}
            <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg overflow-hidden">
                {loading ? (
                    <div className="p-6 text-[var(--text-muted)]">Loading audit logs...</div>
                ) : logs.length === 0 ? (
                    <div className="p-6 text-[var(--text-muted)]">No audit logs found</div>
                ) : (
                    <table className="w-full">
                        <thead className="bg-[var(--bg)] border-b border-[var(--border)]">
                            <tr>
                                <th className="px-4 py-3 text-left text-sm font-medium">Timestamp</th>
                                <th className="px-4 py-3 text-left text-sm font-medium">Action</th>
                                <th className="px-4 py-3 text-left text-sm font-medium">Entity</th>
                                <th className="px-4 py-3 text-left text-sm font-medium">User</th>
                                <th className="px-4 py-3 text-left text-sm font-medium">IP Address</th>
                            </tr>
                        </thead>
                        <tbody>
                            {logs.map((log) => (
                                <tr key={log.id} className="border-b border-[var(--border)] hover:bg-[var(--bg)]">
                                    <td className="px-4 py-3 text-sm">
                                        {new Date(log.created_at).toLocaleString()}
                                    </td>
                                    <td className="px-4 py-3 text-sm">
                                        <span className="px-2 py-1 bg-blue-900 text-blue-300 rounded text-xs">
                                            {log.action}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm">
                                        {log.entity_type}: {log.entity_id?.substring(0, 8)}...
                                    </td>
                                    <td className="px-4 py-3 text-sm">{log.user_email || 'System'}</td>
                                    <td className="px-4 py-3 text-sm text-[var(--text-muted)]">
                                        {log.ip_address || '-'}
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
