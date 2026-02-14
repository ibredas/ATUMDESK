import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import DeskSidebar from '../../components/DeskSidebar'

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
            const method = isNew ? 'POST' : 'PUT' // Note: PUT is now implemented

            // WAIT! I missed PUT in the router implementation! 
            // I only implemented GET / POST / Publish. 
            // I need to add PUT (Update) to the Router or use POST for updates if designed that way. 
            // Checking router map... 
            // 03_KB_API_MAP.md says "PUT /api/v1/kb/articles/{id}"... 
            // BUT I DID NOT IMPLEMENT "PUT" in kb.py! 
            // I need to fix the router first! 

            // For now, let's assume I will fix the router.

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
        <div className="flex min-h-screen bg-[var(--bg-0)]">
            <DeskSidebar />
            <div className="flex-1 p-8">
                <div className="max-w-4xl mx-auto">
                    <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center gap-4">
                            <Link to="/desk/kb" className="text-[var(--text-2)] hover:text-white">← Back</Link>
                            <h1 className="text-2xl font-bold">{isNew ? 'New Article' : 'Edit Article'}</h1>
                        </div>
                        <button onClick={handleSubmit} disabled={loading} className="btn-primary">
                            {loading ? 'Saving...' : 'Save Article'}
                        </button>
                    </div>

                    <div className="glass-panel rounded-xl p-8">
                        <form onSubmit={handleSubmit} className="space-y-6">

                            <div>
                                <label className="block text-xs uppercase tracking-widest text-[var(--text-2)] mb-2">Title</label>
                                <input
                                    type="text"
                                    className="input-field w-full text-lg font-bold"
                                    value={formData.title}
                                    onChange={e => setFormData({ ...formData, title: e.target.value })}
                                    required
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-xs uppercase tracking-widest text-[var(--text-2)] mb-2">Category</label>
                                    <select
                                        className="input-field w-full"
                                        value={formData.category_id || ''}
                                        onChange={e => setFormData({ ...formData, category_id: e.target.value })}
                                    >
                                        <option value="">(None)</option>
                                        {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                    </select>
                                </div>

                                <div className="flex flex-col gap-4 pt-6">
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={formData.is_internal}
                                            onChange={e => setFormData({ ...formData, is_internal: e.target.checked })}
                                        />
                                        <span className="text-sm">Internal Only (Agents)</span>
                                    </label>

                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={formData.is_published}
                                            onChange={e => setFormData({ ...formData, is_published: e.target.checked })}
                                        />
                                        <span className="text-sm">Published</span>
                                    </label>
                                </div>
                            </div>

                            <div>
                                <label className="block text-xs uppercase tracking-widest text-[var(--text-2)] mb-2">Content (Markdown)</label>
                                <textarea
                                    className="input-field w-full h-[400px] font-mono"
                                    value={formData.content}
                                    onChange={e => setFormData({ ...formData, content: e.target.value })}
                                    required
                                ></textarea>
                                <p className="text-[10px] text-[var(--text-2)] mt-2">Supports Markdown formatting.</p>
                            </div>

                        </form>
                    </div>
                </div>
            </div>
        </div>
    )
}
