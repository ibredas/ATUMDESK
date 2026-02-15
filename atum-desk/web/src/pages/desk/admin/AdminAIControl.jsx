import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import DeskSidebar from '../../../components/DeskSidebar'
import { Badge } from '../../../design-system/components/Badge'
import { Button } from '../../../design-system/components/Button'
import { Card, CardHeader, CardTitle, CardContent } from '../../../design-system/components/Card'

export default function AdminAIControl() {
    const navigate = useNavigate()
    const token = localStorage.getItem('atum_desk_token')
    const [loading, setLoading] = useState(true)
    const [models, setModels] = useState(null)
    const [insights, setInsights] = useState(null)
    const [ragHealth, setRagHealth] = useState(null)

    useEffect(() => {
        if (!token) { navigate('/desk/login'); return }
        fetchAll()
    }, [])

    const fetchAll = async () => {
        const headers = { 'Authorization': `Bearer ${token}` }
        try {
            const [modelsRes, insightsRes, ragRes] = await Promise.all([
                fetch('/api/v1/ai/models/status', { headers }).catch(() => null),
                fetch('/api/v1/ai/insights/dashboard', { headers }).catch(() => null),
                fetch('/api/v1/rag/health', { headers }).catch(() => null),
            ])
            if (modelsRes?.ok) setModels(await modelsRes.json())
            if (insightsRes?.ok) setInsights(await insightsRes.json())
            if (ragRes?.ok) setRagHealth(await ragRes.json())
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
                            <h1 className="text-2xl font-bold">AI & RAG Control Center</h1>
                            <p className="text-sm text-[var(--text-2)] mt-1">Monitor and manage AI models, RAG indexing, and inference pipeline</p>
                        </div>
                        <Button variant="outline" onClick={fetchAll}>↻ Refresh</Button>
                    </div>

                    {loading ? (
                        <div className="flex items-center justify-center py-16"><div className="spinner"></div></div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {/* Ollama Status */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>🤖 Ollama Models</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    {models?.models?.length > 0 ? (
                                        <div className="space-y-3">
                                            {models.models.map((m, i) => (
                                                <div key={i} className="flex items-center justify-between">
                                                    <span className="text-sm font-mono">{m.name || m.model}</span>
                                                    <Badge variant="success">loaded</Badge>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="text-center py-4">
                                            <Badge variant="warning">No models loaded</Badge>
                                        </div>
                                    )}
                                    <div className="mt-4 pt-3 border-t border-[var(--border)]">
                                        <div className="text-xs text-[var(--text-2)]">
                                            Endpoint: <span className="font-mono">localhost:11434</span>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* RAG Health */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>📚 RAG Pipeline</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    {ragHealth ? (
                                        <div className="space-y-2">
                                            <div className="flex justify-between items-center">
                                                <span className="text-sm">Status</span>
                                                <Badge variant={ragHealth.status === 'healthy' ? 'success' : 'error'}>
                                                    {ragHealth.status || 'unknown'}
                                                </Badge>
                                            </div>
                                            {ragHealth.documents_count !== undefined && (
                                                <div className="flex justify-between items-center">
                                                    <span className="text-sm">Documents</span>
                                                    <span className="text-sm font-mono">{ragHealth.documents_count}</span>
                                                </div>
                                            )}
                                            {ragHealth.chunks_count !== undefined && (
                                                <div className="flex justify-between items-center">
                                                    <span className="text-sm">Chunks</span>
                                                    <span className="text-sm font-mono">{ragHealth.chunks_count}</span>
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="text-center py-4">
                                            <Badge variant="error">RAG unavailable</Badge>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>

                            {/* AI Insights */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>💡 AI Insights</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    {insights ? (
                                        <div className="space-y-2">
                                            {insights.total_triages !== undefined && (
                                                <div className="flex justify-between items-center">
                                                    <span className="text-sm">Total AI Triages</span>
                                                    <span className="text-sm font-bold">{insights.total_triages}</span>
                                                </div>
                                            )}
                                            {insights.avg_confidence !== undefined && (
                                                <div className="flex justify-between items-center">
                                                    <span className="text-sm">Avg Confidence</span>
                                                    <span className="text-sm font-bold">{(insights.avg_confidence * 100).toFixed(0)}%</span>
                                                </div>
                                            )}
                                            {insights.categories && (
                                                <div className="mt-3 pt-3 border-t border-[var(--border)]">
                                                    <div className="text-xs text-[var(--text-2)] mb-2">Top Categories</div>
                                                    <div className="flex flex-wrap gap-1">
                                                        {Object.entries(insights.categories || {}).slice(0, 4).map(([k, v]) => (
                                                            <Badge key={k} variant="info" size="sm">{k}: {v}</Badge>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="text-center py-4 text-sm text-[var(--text-2)]">No AI data yet</div>
                                    )}
                                </CardContent>
                            </Card>

                            {/* Job Queue Stats */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>⚙️ Job Queue</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-sm text-[var(--text-2)]">
                                        AI jobs are processed by the background job worker.
                                        <a href="/desk/admin/jobs" className="text-[var(--accent-gold)] ml-1 hover:underline">View Queue →</a>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Active Model */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>🎯 Active Model</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm">Model</span>
                                            <span className="text-xs font-mono text-[var(--accent-gold)]">ATUM-DESK-COPILOT</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm">Provider</span>
                                            <span className="text-xs font-mono">Ollama (local)</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm">Features</span>
                                            <div className="flex gap-1">
                                                <Badge variant="gold" size="sm">Triage</Badge>
                                                <Badge variant="gold" size="sm">Reply</Badge>
                                                <Badge variant="gold" size="sm">Sentiment</Badge>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Config */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>🔧 Configuration</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-sm text-[var(--text-2)] space-y-1">
                                        <p>• RAG indexes on ticket creation</p>
                                        <p>• AI triage on every new ticket</p>
                                        <p>• Sentiment analysis + escalation detection</p>
                                        <p>• Smart reply generation</p>
                                        <p>• SLA prediction per ticket</p>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
