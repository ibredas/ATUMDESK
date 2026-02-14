import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import DeskSidebar from '../../components/DeskSidebar'

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
        <div className="flex min-h-screen bg-[var(--bg-0)]">
            <DeskSidebar />
            <div className="flex-1 p-8">
                <div className="max-w-6xl mx-auto">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h1 className="text-2xl font-bold">Problem Management</h1>
                            <p className="text-[var(--text-2)] text-sm">Root Cause Analysis & Recurring Incidents</p>
                        </div>
                        <button className="btn-primary" onClick={() => alert('Create Problem - Coming Soon')}>
                            + New Problem
                        </button>
                    </div>

                    <div className="glass-panel rounded-xl p-6">
                        {loading ? (
                            <div className="p-12 text-center text-[var(--text-2)]">Loading...</div>
                        ) : problems.length === 0 ? (
                            <div className="p-12 text-center text-[var(--text-2)]">
                                <div className="text-3xl mb-3">🧩</div>
                                <p>No problems recorded yet.</p>
                            </div>
                        ) : (
                            <table className="atum-table">
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
                                        <tr key={p.id} className="hover:bg-white/5 cursor-pointer">
                                            <td className="font-medium text-white">{p.title}</td>
                                            <td><span className="badge badge-neutral">{p.status}</span></td>
                                            <td><span className="badge badge-neutral">{p.severity}</span></td>
                                            <td className="text-xs text-[var(--text-2)]">
                                                {new Date(p.updated_at).toLocaleDateString()}
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
