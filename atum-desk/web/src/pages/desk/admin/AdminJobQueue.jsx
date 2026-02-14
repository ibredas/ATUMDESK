import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import DeskSidebar from '../../../components/DeskSidebar'
import { Table } from '../../../design-system/components/Table'
import { Button } from '../../../design-system/components/Button'
import { Badge } from '../../../design-system/components/Badge'

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
      
      if (jobsRes.ok) {
        const data = await jobsRes.json()
        setJobs(data.jobs || [])
      }
      
      if (ragRes.ok) {
        const data = await ragRes.json()
        setRagJobs(data.jobs || [])
      }
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  const columns = [
    { key: 'job_type', header: 'Job Type' },
    { key: 'status', header: 'Status', render: (row) => (
      <Badge variant={row.status === 'DONE' ? 'success' : row.status === 'FAILED' ? 'error' : row.status === 'RUNNING' ? 'info' : 'default'}>
        {row.status}
      </Badge>
    )},
    { key: 'priority', header: 'Priority' },
    { key: 'retry_count', header: 'Retries' },
    { key: 'created_at', header: 'Created', render: (row) => row.created_at ? new Date(row.created_at).toLocaleString() : '-' },
    { key: 'last_error', header: 'Error', render: (row) => row.last_error ? <span className="text-red-400 text-xs">{row.last_error.substring(0, 50)}</span> : '-' },
  ]

  const ragColumns = [
    { key: 'status', header: 'Status', render: (row) => (
      <Badge variant={row.status === 'completed' ? 'success' : row.status === 'failed' ? 'error' : 'pending' === row.status ? 'warning' : 'info'}>
        {row.status}
      </Badge>
    )},
    { key: 'document_type', header: 'Type' },
    { key: 'created_at', header: 'Created', render: (row) => row.created_at ? new Date(row.created_at).toLocaleString() : '-' },
  ]

  if (loading) {
    return (
      <div className="flex min-h-screen bg-[var(--bg-0)]">
        <DeskSidebar />
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin h-8 w-8 border-2 border-[var(--accent-gold)] border-t-transparent rounded-full"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-[var(--bg-0)]">
      <DeskSidebar />
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-3">
                <span className="text-3xl">📋</span>
                Job Queue Viewer
              </h1>
              <p className="text-[var(--text-muted)] mt-1">Monitor and manage background jobs</p>
            </div>
            <Button onClick={fetchData}>Refresh</Button>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => setActiveTab('jobs')}
              className={`px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${
                activeTab === 'jobs' 
                  ? 'bg-[var(--accent-gold)] text-black' 
                  : 'bg-[var(--bg-2)] text-[var(--text-1)] border border-[var(--border)]'
              }`}
            >
              Job Queue ({jobs.length})
            </button>
            <button
              onClick={() => setActiveTab('rag')}
              className={`px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${
                activeTab === 'rag' 
                  ? 'bg-[var(--accent-gold)] text-black' 
                  : 'bg-[var(--bg-2)] text-[var(--text-1)] border border-[var(--border)]'
              }`}
            >
              RAG Index Queue ({ragJobs.length})
            </button>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="glass-panel rounded-xl p-4">
              <div className="text-sm text-[var(--text-muted)] uppercase">Pending</div>
              <div className="text-2xl font-bold text-orange-400">{jobs.filter(j => j.status === 'PENDING').length}</div>
            </div>
            <div className="glass-panel rounded-xl p-4">
              <div className="text-sm text-[var(--text-muted)] uppercase">Running</div>
              <div className="text-2xl font-bold text-blue-400">{jobs.filter(j => j.status === 'RUNNING').length}</div>
            </div>
            <div className="glass-panel rounded-xl p-4">
              <div className="text-sm text-[var(--text-muted)] uppercase">Failed</div>
              <div className="text-2xl font-bold text-red-400">{jobs.filter(j => j.status === 'FAILED').length}</div>
            </div>
            <div className="glass-panel rounded-xl p-4">
              <div className="text-sm text-[var(--text-muted)] uppercase">Completed</div>
              <div className="text-2xl font-bold text-green-400">{jobs.filter(j => j.status === 'DONE').length}</div>
            </div>
          </div>

          {/* Job Types */}
          <div className="glass-panel rounded-xl p-4 mb-6">
            <h3 className="text-sm font-semibold text-[var(--text-1)] mb-3">Job Types Running</h3>
            <div className="flex flex-wrap gap-2">
              {['TRIAGE_TICKET', 'KB_SUGGEST', 'SMART_REPLY', 'SLA_PREDICT', 'SENTIMENT_ANALYSIS'].map(type => (
                <span key={type} className="px-3 py-1 bg-[var(--bg-2)] border border-[var(--border)] rounded-full text-xs font-mono">
                  {type}
                </span>
              ))}
            </div>
          </div>

          {/* Table */}
          {activeTab === 'jobs' ? (
            <div className="glass-panel rounded-xl p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">Job Queue</h2>
              <Table columns={columns} data={jobs} emptyMessage="No jobs in queue" />
            </div>
          ) : (
            <div className="glass-panel rounded-xl p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">RAG Index Queue</h2>
              <Table columns={ragColumns} data={ragJobs} emptyMessage="No RAG jobs in queue" />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
