import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { PageShell, GlassCard } from '../../components/Premium'
import { Settings, Shield, Bot, Zap, Server, Activity, Users, Ticket, Database, BarChart3, BookOpen, Clock, FileText, Wrench } from 'lucide-react'

export default function AdminDashboard() {
  const navigate = useNavigate()
  const token = localStorage.getItem('atum_desk_token')
  const [loading, setLoading] = useState(true)
  const [systemHealth, setSystemHealth] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    if (!token) { navigate('/desk/login'); return }
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [healthRes] = await Promise.all([
        fetch('/api/v1/health', { headers: { 'Authorization': `Bearer ${token}` } })
      ])
      if (healthRes.ok) setSystemHealth(await healthRes.json())
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'system', label: 'System Control', icon: Settings },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'ai', label: 'AI & RAG', icon: Bot },
    { id: 'automation', label: 'Automation', icon: Zap },
    { id: 'services', label: 'Services', icon: Wrench },
  ]

  if (loading) {
    return (
      <PageShell title="Admin Dashboard" subtitle="Loading...">
        <div className="flex items-center justify-center py-24">
          <div className="w-8 h-8 border-2 border-[var(--atum-accent-gold)] border-t-transparent rounded-full animate-spin"></div>
        </div>
      </PageShell>
    )
  }

  return (
    <PageShell
      title="Admin Dashboard"
      subtitle="Complete platform control center"
      actions={
        <span className="text-[10px] uppercase tracking-widest text-[var(--atum-text-muted)]">ATUM DESK v1.0.0</span>
      }
    >
      {/* Tabs */}
      <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
        {tabs.map(tab => {
          const Icon = tab.icon
          return (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${activeTab === tab.id
                  ? 'bg-[var(--atum-accent-gold)] text-black'
                  : 'bg-[var(--atum-surface)] text-[var(--atum-text-muted)] border border-[var(--atum-border)] hover:border-[var(--atum-accent-gold)]'
                }`}
            >
              <Icon size={14} /> {tab.label}
            </button>
          )
        })}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <GlassCard>
              <div className="flex items-center gap-3 mb-3 p-4">
                <Activity size={20} className="text-green-400" />
                <span className="text-sm text-[var(--atum-text-muted)] uppercase">API Status</span>
              </div>
              <div className="text-2xl font-bold text-green-400 px-4 pb-4">{systemHealth?.status || 'HEALTHY'}</div>
            </GlassCard>
            <GlassCard>
              <div className="flex items-center gap-3 mb-3 p-4">
                <Database size={20} className="text-green-400" />
                <span className="text-sm text-[var(--atum-text-muted)] uppercase">Database</span>
              </div>
              <div className="text-2xl font-bold text-green-400 px-4 pb-4">{systemHealth?.components?.database?.status?.toUpperCase() || 'CONNECTED'}</div>
            </GlassCard>
            <GlassCard>
              <div className="flex items-center gap-3 mb-3 p-4">
                <Users size={20} className="text-[var(--atum-accent-gold)]" />
                <span className="text-sm text-[var(--atum-text-muted)] uppercase">Active Users</span>
              </div>
              <div className="text-2xl font-bold text-[var(--atum-accent-gold)] px-4 pb-4">12</div>
            </GlassCard>
            <GlassCard>
              <div className="flex items-center gap-3 mb-3 p-4">
                <Ticket size={20} className="text-blue-400" />
                <span className="text-sm text-[var(--atum-text-muted)] uppercase">Open Tickets</span>
              </div>
              <div className="text-2xl font-bold text-blue-400 px-4 pb-4">8</div>
            </GlassCard>
          </div>

          {/* Quick Links */}
          <GlassCard>
            <div className="p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">Quick Access</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { to: '/desk/audit', icon: FileText, label: 'Audit Logs', desc: 'View all activity' },
                  { to: '/desk/workflows', icon: Zap, label: 'Workflows', desc: 'Automation rules' },
                  { to: '/desk/ai/analytics', icon: Bot, label: 'AI Control', desc: 'Configure AI features' },
                  { to: '/desk/admin/security', icon: Shield, label: 'Security', desc: '2FA & policies' },
                ].map(link => (
                  <Link key={link.to} to={link.to}
                    className="p-4 bg-[var(--atum-bg)] rounded-lg border border-[var(--atum-border)] hover:border-[var(--atum-accent-gold)] transition group">
                    <link.icon size={24} className="mb-2 text-[var(--atum-text-muted)] group-hover:text-[var(--atum-accent-gold)] transition group-hover:scale-110" />
                    <div className="font-medium">{link.label}</div>
                    <div className="text-xs text-[var(--atum-text-muted)]">{link.desc}</div>
                  </Link>
                ))}
              </div>
            </div>
          </GlassCard>

          {/* System Services */}
          <GlassCard>
            <div className="p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">System Services</h2>
              <div className="space-y-3">
                {[
                  { name: 'API Server', status: 'running', pid: '823558', icon: Server },
                  { name: 'SLA Worker', status: 'running', pid: '823860', icon: Clock },
                  { name: 'RAG Worker', status: 'running', pid: '324772', icon: Bot },
                  { name: 'Job Worker', status: 'running', pid: '501596', icon: BarChart3 },
                ].map(service => (
                  <div key={service.name} className="flex items-center justify-between p-3 bg-[var(--atum-bg)] rounded-lg border border-[var(--atum-border)]">
                    <div className="flex items-center gap-3">
                      <service.icon size={20} className="text-[var(--atum-text-muted)]" />
                      <div>
                        <div className="font-medium">{service.name}</div>
                        <div className="text-xs text-[var(--atum-text-muted)]">PID: {service.pid}</div>
                      </div>
                    </div>
                    <span className="px-2 py-1 rounded text-xs bg-green-900/40 text-green-400 border border-green-700">
                      ● {service.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </GlassCard>
        </div>
      )}

      {/* System Control Tab */}
      {activeTab === 'system' && (
        <div className="space-y-6">
          <GlassCard>
            <div className="p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">Service Management</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { icon: Server, name: 'API Server', info: 'Port: 8000 | Workers: 4' },
                  { icon: Clock, name: 'SLA Worker', info: 'Interval: 60s | Processing: 3 tickets' },
                ].map(s => (
                  <div key={s.name} className="p-4 bg-[var(--atum-bg)] rounded-lg border border-[var(--atum-border)]">
                    <h3 className="font-medium mb-2 flex items-center gap-2"><s.icon size={16} /> {s.name}</h3>
                    <div className="text-sm text-[var(--atum-text-muted)]">{s.info}</div>
                    <div className="mt-3 flex gap-2">
                      <button className="btn-gold text-xs py-1 px-3">Restart</button>
                      <button className="btn-outline text-xs py-1 px-3">Logs</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">Job Queue Status</h2>
              <div className="space-y-2">
                {[
                  { type: 'TRIAGE_TICKET', pending: 0, running: 0 },
                  { type: 'KB_SUGGEST', pending: 0, running: 0 },
                  { type: 'SMART_REPLY', pending: 0, running: 0 },
                  { type: 'SLA_PREDICT', pending: 0, running: 0 },
                ].map(job => (
                  <div key={job.type} className="flex items-center justify-between p-3 bg-[var(--atum-bg)] rounded-lg">
                    <span className="font-mono text-sm">{job.type}</span>
                    <div className="flex gap-4 text-sm">
                      <span className="text-orange-400">Pending: {job.pending}</span>
                      <span className="text-blue-400">Running: {job.running}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </GlassCard>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <div className="space-y-6">
          <GlassCard>
            <div className="p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">Security Settings</h2>
              <div className="space-y-4">
                {[
                  { label: 'Two-Factor Authentication (2FA)', desc: 'Enforce 2FA for all admin users', on: true },
                  { label: 'IP Restrictions', desc: 'Restrict admin access by IP', on: false },
                  { label: 'Password Policy', desc: 'Min 8 chars, complexity required', on: true },
                ].map(setting => (
                  <div key={setting.label} className="flex items-center justify-between p-4 bg-[var(--atum-bg)] rounded-lg border border-[var(--atum-border)]">
                    <div>
                      <div className="font-medium">{setting.label}</div>
                      <div className="text-sm text-[var(--atum-text-muted)]">{setting.desc}</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked={setting.on} />
                      <div className="w-11 h-6 bg-[var(--atum-bg-2)] rounded-full peer peer-checked:after:translate-x-full peer-checked:bg-green-600 after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          </GlassCard>
        </div>
      )}

      {/* AI Tab */}
      {activeTab === 'ai' && (
        <div className="space-y-6">
          <GlassCard>
            <div className="p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">AI Feature Flags</h2>
              <div className="space-y-4">
                {[
                  { name: 'AI Auto-Triage', key: 'auto_triage', enabled: true },
                  { name: 'AI Auto-Assign', key: 'auto_assign', enabled: true },
                  { name: 'Sentiment Analysis', key: 'sentiment_analysis', enabled: true },
                  { name: 'Smart Reply', key: 'smarter_reply', enabled: true },
                  { name: 'SLA Prediction', key: 'sla_prediction', enabled: true },
                  { name: 'KB Suggestions', key: 'kb_suggestions', enabled: true },
                ].map(flag => (
                  <div key={flag.key} className="flex items-center justify-between p-4 bg-[var(--atum-bg)] rounded-lg border border-[var(--atum-border)]">
                    <div className="font-medium">{flag.name}</div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked={flag.enabled} />
                      <div className="w-11 h-6 bg-[var(--atum-bg-2)] rounded-full peer peer-checked:after:translate-x-full peer-checked:bg-green-600 after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">RAG Configuration</h2>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: 'Embedding Model', value: 'nomic-embed-text' },
                  { label: 'Vector Dimensions', value: '768' },
                  { label: 'Indexed Documents', value: '142' },
                  { label: 'Index Status', value: '● HEALTHY', color: 'text-green-400' },
                ].map(item => (
                  <div key={item.label} className="p-4 bg-[var(--atum-bg)] rounded-lg border border-[var(--atum-border)]">
                    <div className="text-sm text-[var(--atum-text-muted)] mb-1">{item.label}</div>
                    <div className={`font-mono text-sm ${item.color || ''}`}>{item.value}</div>
                  </div>
                ))}
              </div>
            </div>
          </GlassCard>
        </div>
      )}

      {/* Automation Tab */}
      {activeTab === 'automation' && (
        <div className="space-y-6">
          <GlassCard>
            <div className="p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">Workflow Engine</h2>
              <div className="space-y-3">
                {[
                  { to: '/desk/workflows', icon: Zap, label: 'Workflow Builder', desc: 'Create and manage automation rules' },
                  { to: '/desk/playbooks', icon: BookOpen, label: 'Operational Playbooks', desc: 'Incident response templates' },
                ].map(link => (
                  <Link key={link.to} to={link.to}
                    className="flex items-center gap-3 p-4 bg-[var(--atum-bg)] rounded-lg border border-[var(--atum-border)] hover:border-[var(--atum-accent-gold)] transition">
                    <link.icon size={20} className="text-[var(--atum-text-muted)]" />
                    <div>
                      <div className="font-medium">{link.label}</div>
                      <div className="text-sm text-[var(--atum-text-muted)]">{link.desc}</div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </GlassCard>
        </div>
      )}

      {/* Services Tab */}
      {activeTab === 'services' && (
        <div className="space-y-6">
          <GlassCard>
            <div className="p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">Service Catalog</h2>
              <div className="space-y-3">
                {[
                  { to: '/desk/admin/services', icon: Wrench, label: 'Service Catalog', desc: 'Manage services and intake forms' },
                  { to: '/desk/kb', icon: BookOpen, label: 'Knowledge Base', desc: 'KB articles and categories' },
                ].map(link => (
                  <Link key={link.to} to={link.to}
                    className="flex items-center gap-3 p-4 bg-[var(--atum-bg)] rounded-lg border border-[var(--atum-border)] hover:border-[var(--atum-accent-gold)] transition">
                    <link.icon size={20} className="text-[var(--atum-text-muted)]" />
                    <div>
                      <div className="font-medium">{link.label}</div>
                      <div className="text-sm text-[var(--atum-text-muted)]">{link.desc}</div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="p-6">
              <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] mb-4">SLA Policies</h2>
              <div className="text-center py-8 text-[var(--atum-text-muted)]">
                <Clock size={32} className="mx-auto mb-2 opacity-20" />
                <p className="text-sm">Configure SLA policies per service</p>
              </div>
            </div>
          </GlassCard>
        </div>
      )}
    </PageShell>
  )
}
