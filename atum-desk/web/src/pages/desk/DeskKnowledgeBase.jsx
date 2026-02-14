import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import DeskSidebar from '../../components/DeskSidebar'

export default function DeskKnowledgeBase() {
    const navigate = useNavigate()
    const token = localStorage.getItem('atum_desk_token')
    const [articles, setArticles] = useState([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('all') // all, public, internal

    useEffect(() => {
        if (!token) { navigate('/desk/login'); return }
        fetchArticles()
    }, [filter])

    const fetchArticles = async () => {
        setLoading(true)
        try {
            // visibility param: public, internal, all
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

    return (
        <div className="flex min-h-screen bg-[var(--bg-0)]">
            <DeskSidebar />
            <div className="flex-1 p-8">
                <div className="max-w-6xl mx-auto">
                    <div className="flex items-center justify-between mb-8">
                        <h1 className="text-2xl font-bold">Knowledge Base</h1>
                        <Link to="/desk/kb/new" className="btn-primary">
                            + New Article
                        </Link>
                    </div>

                    {/* Filters */}
                    <div className="flex gap-2 mb-6">
                        {['all', 'public', 'internal'].map(f => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${filter === f
                                        ? 'bg-[var(--accent-gold)] text-black border-[var(--accent-gold)]'
                                        : 'text-[var(--text-2)] border-[var(--glass-border)] hover:text-white'
                                    }`}
                            >
                                {f}
                            </button>
                        ))}
                    </div>

                    <div className="glass-panel rounded-xl p-6">
                        {loading ? (
                            <div className="p-12 text-center text-[var(--text-2)]">Loading...</div>
                        ) : articles.length === 0 ? (
                            <div className="p-12 text-center text-[var(--text-2)]">No articles found</div>
                        ) : (
                            <table className="atum-table">
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
                                        <tr key={article.id} onClick={() => navigate(`/desk/kb/${article.id}`)} className="cursor-pointer hover:bg-white/5">
                                            <td className="font-medium text-white">{article.title}</td>
                                            <td>
                                                {article.is_internal
                                                    ? <span className="text-xs text-amber-500 border border-amber-500/20 px-2 py-0.5 rounded">INTERNAL</span>
                                                    : <span className="text-xs text-blue-400 border border-blue-400/20 px-2 py-0.5 rounded">PUBLIC</span>
                                                }
                                            </td>
                                            <td>
                                                {article.is_published
                                                    ? <span className="text-[#34d399]">Published</span>
                                                    : <span className="text-[var(--text-2)]">Draft</span>
                                                }
                                            </td>
                                            <td className="text-[var(--text-2)]">{article.view_count}</td>
                                            <td className="text-xs text-[var(--text-2)]">
                                                {new Date(article.updated_at).toLocaleDateString()}
                                            </td>
                                            <td>
                                                <button
                                                    onClick={(e) => togglePublish(e, article.id, article.is_published)}
                                                    className="text-xs hover:text-white text-[var(--text-2)] underline"
                                                >
                                                    {article.is_published ? 'Unpublish' : 'Publish'}
                                                </button>
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
