import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

export default function DeskKBSuggestions() {
    const [summary, setSummary] = useState(null)
    const [suggestions, setSuggestions] = useState([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('all')

    useEffect(() => {
        fetchSummary()
    }, [])

    const fetchSummary = async () => {
        try {
            const token = localStorage.getItem('atum_desk_token')
            const res = await fetch('/api/v1/kb/suggestions/summary', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            const data = await res.json()
            setSummary(data)
            setSuggestions(data.failing_suggestions || [])
        } catch (err) {
            console.error('Failed to load KB suggestions:', err)
        } finally {
            setLoading(false)
        }
    }

    const voteSuggestion = async (id, isHelpful) => {
        try {
            const token = localStorage.getItem('atum_desk_token')
            await fetch(`/api/v1/kb/suggestions/vote?id=${id}&is_helpful=${isHelpful}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            })
            fetchSummary()
        } catch (err) {
            console.error('Failed to vote:', err)
        }
    }

    if (loading) return <div className="p-8 text-[var(--text-1)]">Loading KB Suggestions...</div>

    return (
        <div className="desk-page">
            <div className="desk-page-header">
                <h1>📚 KB Suggestions Analytics</h1>
                <p className="text-[var(--text-1)]">Track knowledge base deflection effectiveness</p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <div className="glass-panel p-6 rounded-xl border border-[var(--glass-border)]">
                    <div className="text-3xl font-bold text-[var(--accent-gold)]">{summary?.total_suggestions || 0}</div>
                    <div className="text-sm text-[var(--text-2)]">Total Suggestions</div>
                </div>
                <div className="glass-panel p-6 rounded-xl border border-[var(--glass-border)]">
                    <div className="text-3xl font-bold text-green-400">{summary?.helpful_count || 0}</div>
                    <div className="text-sm text-[var(--text-2)]">Helpful Votes</div>
                </div>
                <div className="glass-panel p-6 rounded-xl border border-[var(--glass-border)]">
                    <div className="text-3xl font-bold text-blue-400">{summary?.deflection_rate || 0}%</div>
                    <div className="text-sm text-[var(--text-2)]">Deflection Rate</div>
                </div>
                <div className="glass-panel p-6 rounded-xl border border-[var(--glass-border)]">
                    <div className="text-3xl font-bold text-orange-400">{summary?.deflected_tickets || 0}</div>
                    <div className="text-sm text-[var(--text-2)]">Self-Resolved</div>
                </div>
            </div>

            {/* Top Articles */}
            <div className="glass-panel p-6 rounded-xl border border-[var(--glass-border)] mb-8">
                <h2 className="text-xl font-bold mb-4">🏆 Top Performing Articles</h2>
                <div className="space-y-3">
                    {summary?.top_articles?.map((article, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 bg-[rgba(255,255,255,0.02)] rounded-lg">
                            <div className="flex-1">
                                <div className="font-medium">{article.title}</div>
                                <div className="text-xs text-[var(--text-2)]">
                                    {article.suggestion_count} suggestions • {article.helpful_count} helpful
                                </div>
                            </div>
                            <div className="text-green-400 text-sm">
                                {Math.round(article.helpful_count / article.suggestion_count * 100)}%
                            </div>
                        </div>
                    ))}
                    {(!summary?.top_articles || summary.top_articles.length === 0) && (
                        <div className="text-[var(--text-2)] text-center py-4">No data yet</div>
                    )}
                </div>
            </div>

            {/* Failing Suggestions */}
            <div className="glass-panel p-6 rounded-xl border border-[var(--glass-border)]">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-bold">⚠️ Suggestions Needing Improvement</h2>
                    <span className="text-sm text-[var(--text-2)]">
                        Low relevance scores may indicate KB gaps
                    </span>
                </div>
                <div className="space-y-3">
                    {suggestions.map((sugg, idx) => (
                        <div key={idx} className="flex items-center justify-between p-4 bg-[rgba(255,255,255,0.02)] rounded-lg">
                            <div className="flex-1">
                                <Link to={`/desk/ticket/${sugg.ticket_id}`} className="font-medium hover:text-[var(--accent-gold)]">
                                    {sugg.title}
                                </Link>
                                <div className="text-xs text-[var(--text-2)]">
                                    Score: {sugg.relevance_score.toFixed(2)} • {sugg.created_at}
                                </div>
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => voteSuggestion(sugg.id, true)}
                                    className="px-3 py-1 text-sm bg-green-500/20 text-green-400 rounded hover:bg-green-500/30"
                                >
                                    👍 Helpful
                                </button>
                                <button
                                    onClick={() => voteSuggestion(sugg.id, false)}
                                    className="px-3 py-1 text-sm bg-red-500/20 text-red-400 rounded hover:bg-red-500/30"
                                >
                                    👎 Not Helpful
                                </button>
                            </div>
                        </div>
                    ))}
                    {suggestions.length === 0 && (
                        <div className="text-[var(--text-2)] text-center py-4">All suggestions are helpful! 🎉</div>
                    )}
                </div>
            </div>
        </div>
    )
}
