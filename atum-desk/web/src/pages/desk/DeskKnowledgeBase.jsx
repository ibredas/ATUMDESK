import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { PageShell, GlassCard } from '../../components/Premium'
import { BookOpen, Plus, Eye, EyeOff } from 'lucide-react'

export default function DeskKnowledgeBase() {
    const navigate = useNavigate()
    const token = localStorage.getItem('atum_desk_token')
    const [articles, setArticles] = useState([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('all')

    useEffect(() => {
        if (!token) { navigate('/desk/login'); return }
        fetchArticles()
    }, [filter])

    const fetchArticles = async () => {
        setLoading(true)
        try {
            const res = await fetch(`/api/v1/kb/articles?visibility=${filter}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.status === 401) { navigate('/desk/login'); return }
            if (res.ok) {
                const data = await res.json()
                setArticles(Array.isArray(data) ? data : [])
            }
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    const togglePublish = async (e, id, currentState) => {
        e.stopPropagation()
        if (!window.confirm(`Are you sure you want to ${currentState ? 'Unpublish' : 'Publish'} this article?`)) return
        try {
            const res = await fetch(`/api/v1/kb/articles/${id}/publish?publish=${!currentState}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) fetchArticles()
        } catch (e) { console.error(e) }
    }

    const filters = [
        { key: 'all', label: 'All' },
        { key: 'public', label: 'Public' },
        { key: 'internal', label: 'Internal' },
    ]

    return (
        <PageShell
            title="Knowledge Base"
            subtitle="Articles & documentation"
            actions={
                <Link to="/desk/kb/new" className="btn-gold flex items-center gap-2">
                    <Plus size={16} /> New Article
                </Link>
            }
        >
            {/* Filters */}
            <div className="flex gap-2 mb-6">
                {filters.map(f => (
                    <button
                        key={f.key}
                        onClick={() => setFilter(f.key)}
                        className={`px-4 py-2 rounded-full text-xs font-semibold uppercase tracking-wider border transition-all ${filter === f.key
                            ? 'bg-[var(--atum-accent-gold)] text-black border-[var(--atum-accent-gold)] shadow-[0_0_15px_rgba(217,181,90,0.3)]'
                            : 'bg-[var(--atum-surface)] border-[var(--atum-border)] text-[var(--atum-text-muted)] hover:text-white hover:border-[var(--atum-border-strong)]'
                            }`}
                    >
                        {f.label}
                    </button>
                ))}
            </div>

            <GlassCard className="p-0 overflow-hidden">
                {loading ? (
                    <div className="flex items-center justify-center py-24">
                        <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
                    </div>
                ) : articles.length === 0 ? (
                    <div className="text-center py-24 text-[var(--atum-text-muted)]">
                        <BookOpen size={48} className="mx-auto mb-4 opacity-20" />
                        <p className="text-sm">No articles found</p>
                    </div>
                ) : (
                    <table className="glass-table">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Visibility</th>
                                <th>Status</th>
                                <th>Views</th>
                                <th>Last Updated</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {articles.map(article => (
                                <tr key={article.id} onClick={() => navigate(`/desk/kb/${article.id}`)} className="cursor-pointer">
                                    <td className="font-medium text-white">{article.title}</td>
                                    <td>
                                        {article.is_internal
                                            ? <span className="badge badge-open">INTERNAL</span>
                                            : <span className="badge badge-in_progress">PUBLIC</span>
                                        }
                                    </td>
                                    <td>
                                        {article.is_published
                                            ? <span className="text-[var(--atum-success)] flex items-center gap-1"><Eye size={12} /> Published</span>
                                            : <span className="text-[var(--atum-text-muted)] flex items-center gap-1"><EyeOff size={12} /> Draft</span>
                                        }
                                    </td>
                                    <td className="text-[var(--atum-text-muted)]">{article.view_count}</td>
                                    <td className="text-xs text-[var(--atum-text-muted)]">
                                        {new Date(article.updated_at).toLocaleDateString()}
                                    </td>
                                    <td>
                                        <button
                                            onClick={(e) => togglePublish(e, article.id, article.is_published)}
                                            className="text-xs text-[var(--atum-accent-gold)] hover:text-white transition-colors"
                                        >
                                            {article.is_published ? 'Unpublish' : 'Publish'}
                                        </button>
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
