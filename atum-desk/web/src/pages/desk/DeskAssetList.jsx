import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import DeskSidebar from '../../components/DeskSidebar'

export default function DeskAssetList() {
    const navigate = useNavigate()
    const token = localStorage.getItem('atum_desk_token')
    const [assets, setAssets] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!token) { navigate('/desk/login'); return }
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const res = await fetch('/api/v1/assets', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.status === 401) { navigate('/desk/login'); return }
            if (res.ok) {
                const data = await res.json()
                setAssets(Array.isArray(data) ? data : [])
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
                            <h1 className="text-2xl font-bold">Assets & CMDB</h1>
                            <p className="text-[var(--text-2)] text-sm">Inventory & Configuration Items</p>
                        </div>
                        <button className="btn-primary" onClick={() => alert('Create Asset - Coming Soon')}>
                            + New Asset
                        </button>
                    </div>

                    <div className="glass-panel rounded-xl p-6">
                        {loading ? (
                            <div className="p-12 text-center text-[var(--text-2)]">Loading...</div>
                        ) : assets.length === 0 ? (
                            <div className="p-12 text-center text-[var(--text-2)]">
                                <div className="text-3xl mb-3">💻</div>
                                <p>No assets recorded.</p>
                            </div>
                        ) : (
                            <table className="atum-table">
                                <thead>
                                    <tr>
                                        <th>Identifier</th>
                                        <th>Name</th>
                                        <th>Type</th>
                                        <th>Last Scan</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {assets.map(a => (
                                        <tr key={a.id} className="hover:bg-white/5 cursor-pointer">
                                            <td className="font-mono text-xs text-[var(--accent-gold)]">{a.identifier}</td>
                                            <td className="font-medium text-white">{a.name}</td>
                                            <td><span className="badge badge-neutral">{a.asset_type}</span></td>
                                            <td className="text-xs text-[var(--text-2)]">
                                                {new Date(a.updated_at).toLocaleDateString()}
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
