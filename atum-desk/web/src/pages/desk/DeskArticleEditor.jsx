import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { PageShell, GlassCard } from '../../components/Premium'
import { ChevronLeft, Save } from 'lucide-react'

export default function DeskArticleEditor() {
    const { id } = useParams()
    const isNew = !id || id === 'new'
    const navigate = useNavigate()
    const token = localStorage.getItem('atum_desk_token')

    const [formData, setFormData] = useState({
        title: '',
        content: '',
        category_id: null,
        is_internal: false,
        is_published: false
    })
    const [categories, setCategories] = useState([])
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (!token) { navigate('/desk/login'); return }
        fetchCategories()
        if (!isNew) fetchArticle()
    }, [id])

    const fetchCategories = async () => {
        try {
            const res = await fetch('/api/v1/kb/categories', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) setCategories(await res.json())
        } catch (e) { console.error(e) }
    }

    const fetchArticle = async () => {
        try {
            const res = await fetch(`/api/v1/kb/articles/${id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                const data = await res.json()
                setFormData({
                    title: data.title,
                    content: data.content,
                    category_id: data.category_id,
                    is_internal: data.is_internal,
                    is_published: data.is_published
                })
            }
        } catch (e) { console.error(e) }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        try {
            const url = isNew ? '/api/v1/kb/articles' : `/api/v1/kb/articles/${id}`
            const res = await fetch(url, {
                method: isNew ? 'POST' : 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            if (res.ok) {
                navigate('/desk/kb')
            } else {
                alert('Failed to save article')
            }
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    return (
        <PageShell
            title={isNew ? 'New Article' : 'Edit Article'}
            subtitle="Knowledge Base Editor"
            actions={
                <div className="flex items-center gap-3">
                    <Link to="/desk/kb" className="btn-outline flex items-center gap-2">
                        <ChevronLeft size={16} /> Back
                    </Link>
                    <button onClick={handleSubmit} disabled={loading} className="btn-gold flex items-center gap-2">
                        <Save size={16} /> {loading ? 'Saving...' : 'Save Article'}
                    </button>
                </div>
            }
        >
            <GlassCard>
                <form onSubmit={handleSubmit} className="space-y-6 p-6">
                    <div>
                        <label className="atum-label">Title</label>
                        <input
                            type="text"
                            className="atum-input text-lg font-bold"
                            value={formData.title}
                            onChange={e => setFormData({ ...formData, title: e.target.value })}
                            required
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                        <div>
                            <label className="atum-label">Category</label>
                            <select
                                className="atum-input"
                                value={formData.category_id || ''}
                                onChange={e => setFormData({ ...formData, category_id: e.target.value })}
                            >
                                <option value="">(None)</option>
                                {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                            </select>
                        </div>

                        <div className="flex flex-col gap-4 pt-6">
                            <label className="flex items-center gap-2 cursor-pointer text-sm text-[var(--atum-text-1)]">
                                <input
                                    type="checkbox"
                                    checked={formData.is_internal}
                                    onChange={e => setFormData({ ...formData, is_internal: e.target.checked })}
                                    className="accent-[var(--atum-accent-gold)]"
                                />
                                Internal Only (Agents)
                            </label>

                            <label className="flex items-center gap-2 cursor-pointer text-sm text-[var(--atum-text-1)]">
                                <input
                                    type="checkbox"
                                    checked={formData.is_published}
                                    onChange={e => setFormData({ ...formData, is_published: e.target.checked })}
                                    className="accent-[var(--atum-accent-gold)]"
                                />
                                Published
                            </label>
                        </div>
                    </div>

                    <div>
                        <label className="atum-label">Content (Markdown)</label>
                        <textarea
                            className="atum-input h-[400px] font-mono"
                            value={formData.content}
                            onChange={e => setFormData({ ...formData, content: e.target.value })}
                            required
                        ></textarea>
                        <p className="text-[10px] text-[var(--atum-text-dim)] mt-2">Supports Markdown formatting.</p>
                    </div>
                </form>
            </GlassCard>
        </PageShell>
    )
}
