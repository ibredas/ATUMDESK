import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import DeskSidebar from '../../components/DeskSidebar'

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
        <div className="flex min-h-screen bg-[var(--bg-0)]">
            <DeskSidebar />
            <div className="flex-1 p-8">
                <div className="max-w-6xl mx-auto">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h1 className="text-2xl font-bold">Change Management</h1>
                            <p className="text-[var(--text-2)] text-sm">Approvals & Deployments</p>
                        </div>
                        <button className="btn-primary" onClick={() => alert('Create Change - Coming Soon')}>
                            + New Change
                        </button>
                    </div>

                    <div className="glass-panel rounded-xl p-6">
                        {loading ? (
                            <div className="p-12 text-center text-[var(--text-2)]">Loading...</div>
                        ) : changes.length === 0 ? (
                            <div className="p-12 text-center text-[var(--text-2)]">
                                <div className="text-3xl mb-3">🚧</div>
                                <p>No change requests found.</p>
                            </div>
                        ) : (
                            <table className="atum-table">
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
                                        <tr key={c.id} className="hover:bg-white/5 cursor-pointer">
                                            <td className="font-medium text-white">{c.title}</td>
                                            <td><span className="uppercase text-xs tracking-wider">{c.type}</span></td>
                                            <td>{c.risk_level}</td>
                                            <td><span className="badge badge-neutral">{c.status}</span></td>
                                            <td className="text-xs text-[var(--text-2)]">
                                                {c.planned_start ? new Date(c.planned_start).toLocaleDateString() : 'TBD'}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
