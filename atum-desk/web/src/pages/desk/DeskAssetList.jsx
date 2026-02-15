import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageShell, GlassCard } from '../../components/Premium'
import { Monitor, Plus, Search } from 'lucide-react'

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
        <PageShell
            title="Assets & CMDB"
            subtitle="Inventory & Configuration Items"
            actions={
                <button className="btn-gold flex items-center gap-2" onClick={() => alert('Create Asset - Coming Soon')}>
                    <Plus size={16} /> New Asset
                </button>
            }
        >
            <GlassCard className="p-0 overflow-hidden">
                {loading ? (
                    <div className="flex items-center justify-center py-24">
                        <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
                    </div>
                ) : assets.length === 0 ? (
                    <div className="text-center py-24 text-[var(--atum-text-muted)]">
                        <Monitor size={48} className="mx-auto mb-4 opacity-20" />
                        <p className="text-sm">No assets recorded.</p>
                    </div>
                ) : (
                    <table className="glass-table">
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
                                <tr key={a.id} className="cursor-pointer">
                                    <td className="font-mono text-xs text-[var(--atum-accent-gold)]">{a.identifier}</td>
                                    <td className="font-medium text-white">{a.name}</td>
                                    <td><span className="badge badge-assigned">{a.asset_type}</span></td>
                                    <td className="text-xs text-[var(--atum-text-muted)]">
                                        {new Date(a.updated_at).toLocaleDateString()}
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
