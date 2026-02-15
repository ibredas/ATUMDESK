import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageShell, GlassCard } from '../../../components/Premium'
import { Table } from '../../../design-system/components/Table'
import { Button } from '../../../design-system/components/Button'
import { Badge } from '../../../design-system/components/Badge'
import { ListTodo, RefreshCw } from 'lucide-react'

export default function AdminJobQueue() {
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [jobs, setJobs] = useState([])
  const [ragJobs, setRagJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('jobs')

  useEffect(() => {
    if (!token) { navigate('/desk/login'); return }
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [jobsRes, ragRes] = await Promise.all([
        fetch('/api/v1/admin/jobs', { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch('/api/v1/admin/rag-queue', { headers: { 'Authorization': `Bearer ${token}` } })
      ])
      if (jobsRes.ok) { const data = await jobsRes.json(); setJobs(data.jobs || []) }
      if (ragRes.ok) { const data = await ragRes.json(); setRagJobs(data.jobs || []) }
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const columns = [
    { key: 'job_type', header: 'Job Type' },
    {
      key: 'status', header: 'Status', render: (row) => (
        <Badge variant={row.status === 'DONE' ? 'success' : row.status === 'FAILED' ? 'error' : row.status === 'RUNNING' ? 'info' : 'default'}>{row.status}</Badge>
      )
    },
    { key: 'priority', header: 'Priority' },
    { key: 'retry_count', header: 'Retries' },
    { key: 'created_at', header: 'Created', render: (row) => row.created_at ? new Date(row.created_at).toLocaleString() : '-' },
    { key: 'last_error', header: 'Error', render: (row) => row.last_error ? <span className="text-red-400 text-xs">{row.last_error.substring(0, 50)}</span> : '-' },
  ]

  const ragColumns = [
    {
      key: 'status', header: 'Status', render: (row) => (
        <Badge variant={row.status === 'completed' ? 'success' : row.status === 'failed' ? 'error' : 'pending' === row.status ? 'warning' : 'info'}>{row.status}</Badge>
      )
    },
    { key: 'document_type', header: 'Type' },
    { key: 'created_at', header: 'Created', render: (row) => row.created_at ? new Date(row.created_at).toLocaleString() : '-' },
  ]

  if (loading) {
    return (
      <PageShell title="Job Queue Viewer" subtitle="Loading...">
        <div className="flex items-center justify-center py-24">
          <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
        </div>
      </PageShell>
    )
  }

  return (
    <PageShell
      title="Job Queue Viewer"
      subtitle="Monitor and manage background jobs"
      actions={<Button onClick={fetchData}><RefreshCw size={14} className="mr-1" /> Refresh</Button>}
    >
      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {[
          { id: 'jobs', label: `Job Queue (${jobs.length})` },
          { id: 'rag', label: `RAG Index Queue (${ragJobs.length})` },
        ].map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${activeTab === tab.id
                ? 'bg-[var(--atum-accent-gold)] text-black'
                : 'bg-[var(--atum-surface)] text-[var(--atum-text-muted)] border border-[var(--atum-border)]'
              }`}>{tab.label}</button>
        ))}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Pending', count: jobs.filter(j => j.status === 'PENDING').length, color: 'text-orange-400' },
          { label: 'Running', count: jobs.filter(j => j.status === 'RUNNING').length, color: 'text-blue-400' },
          { label: 'Failed', count: jobs.filter(j => j.status === 'FAILED').length, color: 'text-red-400' },
          { label: 'Completed', count: jobs.filter(j => j.status === 'DONE').length, color: 'text-green-400' },
        ].map(s => (
          <GlassCard key={s.label}>
            <div className="p-4">
              <div className="text-sm text-[var(--atum-text-muted)] uppercase">{s.label}</div>
              <div className={`text-2xl font-bold ${s.color}`}>{s.count}</div>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* Job Types */}
      <GlassCard className="mb-6">
        <div className="p-4">
          <h3 className="text-sm font-semibold mb-3">Job Types Running</h3>
          <div className="flex flex-wrap gap-2">
            {['TRIAGE_TICKET', 'KB_SUGGEST', 'SMART_REPLY', 'SLA_PREDICT', 'SENTIMENT_ANALYSIS'].map(type => (
              <span key={type} className="px-3 py-1 bg-[var(--atum-bg-2)] border border-[var(--atum-border)] rounded-full text-xs font-mono">{type}</span>
            ))}
          </div>
        </div>
      </GlassCard>

      {/* Table */}
      <GlassCard>
        <div className="p-6">
          <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">
            {activeTab === 'jobs' ? 'Job Queue' : 'RAG Index Queue'}
          </h2>
          {activeTab === 'jobs' ? (
            <Table columns={columns} data={jobs} emptyMessage="No jobs in queue" />
          ) : (
            <Table columns={ragColumns} data={ragJobs} emptyMessage="No RAG jobs in queue" />
          )}
        </div>
      </GlassCard>
    </PageShell>
  )
}
