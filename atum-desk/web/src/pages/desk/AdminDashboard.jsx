import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import DeskSidebar from '../../components/DeskSidebar'

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
    { id: 'overview', label: 'Overview', icon: '🎯' },
    { id: 'system', label: 'System Control', icon: '⚙️' },
    { id: 'security', label: 'Security', icon: '🔒' },
    { id: 'ai', label: 'AI & RAG', icon: '🤖' },
    { id: 'automation', label: 'Automation', icon: '⚡' },
    { id: 'services', label: 'Services', icon: '🛠️' },
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
        <div className="max-w-8xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-3">
                <span className="text-3xl">🎛️</span>
                Admin Dashboard
              </h1>
              <p className="text-[var(--text-muted)] mt-1">Complete platform control center</p>
            </div>
            <span className="text-[10px] uppercase tracking-widest text-[var(--text-2)]">ATUM DESK v1.0.0</span>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${
                  activeTab === tab.id 
                    ? 'bg-[var(--accent-gold)] text-black' 
                    : 'bg-[var(--bg-2)] text-[var(--text-1)] border border-[var(--border)] hover:border-[var(--accent-gold)]'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Quick Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="glass-panel rounded-xl p-5">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-2xl">🟢</span>
                    <span className="text-sm text-[var(--text-muted)] uppercase">API Status</span>
                  </div>
                  <div className="text-2xl font-bold text-green-400">{systemHealth?.status || 'HEALTHY'}</div>
                </div>
                
                <div className="glass-panel rounded-xl p-5">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-2xl">📊</span>
                    <span className="text-sm text-[var(--text-muted)] uppercase">Database</span>
                  </div>
                  <div className="text-2xl font-bold text-green-400">{systemHealth?.components?.database?.status?.toUpperCase() || 'CONNECTED'}</div>
                </div>

                <div className="glass-panel rounded-xl p-5">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-2xl">👥</span>
                    <span className="text-sm text-[var(--text-muted)] uppercase">Active Users</span>
                  </div>
                  <div className="text-2xl font-bold text-[var(--accent-gold)]">12</div>
                </div>

                <div className="glass-panel rounded-xl p-5">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-2xl">🎫</span>
                    <span className="text-sm text-[var(--text-muted)] uppercase">Open Tickets</span>
                  </div>
                  <div className="text-2xl font-bold text-blue-400">8</div>
                </div>
              </div>

              {/* Quick Links */}
              <div className="glass-panel rounded-xl p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">Quick Access</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Link to="/desk/audit" className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)] hover:border-[var(--accent-gold)] transition group">
                    <div className="text-2xl mb-2 group-hover:scale-110 transition">📝</div>
                    <div className="font-medium">Audit Logs</div>
                    <div className="text-xs text-[var(--text-muted)]">View all activity</div>
                  </Link>
                  <Link to="/desk/workflows" className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)] hover:border-[var(--accent-gold)] transition group">
                    <div className="text-2xl mb-2 group-hover:scale-110 transition">⚡</div>
                    <div className="font-medium">Workflows</div>
                    <div className="text-xs text-[var(--text-muted)]">Automation rules</div>
                  </Link>
                  <Link to="/desk/ai/analytics" className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)] hover:border-[var(--accent-gold)] transition group">
                    <div className="text-2xl mb-2 group-hover:scale-110 transition">🤖</div>
                    <div className="font-medium">AI Control</div>
                    <div className="text-xs text-[var(--text-muted)]">Configure AI features</div>
                  </Link>
                  <Link to="/desk/admin/security" className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)] hover:border-[var(--accent-gold)] transition group">
                    <div className="text-2xl mb-2 group-hover:scale-110 transition">🔐</div>
                    <div className="font-medium">Security</div>
                    <div className="text-xs text-[var(--text-muted)]">2FA & policies</div>
                  </Link>
                </div>
              </div>

              {/* System Services */}
              <div className="glass-panel rounded-xl p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">System Services</h2>
                <div className="space-y-3">
                  {[
                    { name: 'API Server', status: 'running', pid: '823558', icon: '🚀' },
                    { name: 'SLA Worker', status: 'running', pid: '823860', icon: '⏰' },
                    { name: 'RAG Worker', status: 'running', pid: '324772', icon: '🧠' },
                    { name: 'Job Worker', status: 'running', pid: '501596', icon: '📋' },
                  ].map(service => (
                    <div key={service.name} className="flex items-center justify-between p-3 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                      <div className="flex items-center gap-3">
                        <span className="text-xl">{service.icon}</span>
                        <div>
                          <div className="font-medium">{service.name}</div>
                          <div className="text-xs text-[var(--text-muted)]">PID: {service.pid}</div>
                        </div>
                      </div>
                      <span className="px-2 py-1 rounded text-xs bg-green-900/40 text-green-400 border border-green-700">
                        ● {service.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* System Control Tab */}
          {activeTab === 'system' && (
            <div className="space-y-6">
              <div className="glass-panel rounded-xl p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">Service Management</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                    <h3 className="font-medium mb-2">🚀 API Server</h3>
                    <div className="text-sm text-[var(--text-muted)]">Port: 8000 | Workers: 4</div>
                    <div className="mt-3 flex gap-2">
                      <button className="px-3 py-1 text-xs bg-[var(--accent-gold)] text-black rounded font-medium">Restart</button>
                      <button className="px-3 py-1 text-xs bg-[var(--bg-2)] text-[var(--text-1)] rounded border border-[var(--border)]">Logs</button>
                    </div>
                  </div>
                  <div className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                    <h3 className="font-medium mb-2">⏰ SLA Worker</h3>
                    <div className="text-sm text-[var(--text-muted)]">Interval: 60s | Processing: 3 tickets</div>
                    <div className="mt-3 flex gap-2">
                      <button className="px-3 py-1 text-xs bg-[var(--accent-gold)] text-black rounded font-medium">Restart</button>
                      <button className="px-3 py-1 text-xs bg-[var(--bg-2)] text-[var(--text-1)] rounded border border-[var(--border)]">Logs</button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="glass-panel rounded-xl p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">Job Queue Status</h2>
                <div className="space-y-2">
                  {[
                    { type: 'TRIAGE_TICKET', pending: 0, running: 0 },
                    { type: 'KB_SUGGEST', pending: 0, running: 0 },
                    { type: 'SMART_REPLY', pending: 0, running: 0 },
                    { type: 'SLA_PREDICT', pending: 0, running: 0 },
                  ].map(job => (
                    <div key={job.type} className="flex items-center justify-between p-3 bg-[var(--bg)] rounded-lg">
                      <span className="font-mono text-sm">{job.type}</span>
                      <div className="flex gap-4 text-sm">
                        <span className="text-orange-400">Pending: {job.pending}</span>
                        <span className="text-blue-400">Running: {job.running}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <div className="space-y-6">
              <div className="glass-panel rounded-xl p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">Security Settings</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                    <div>
                      <div className="font-medium">Two-Factor Authentication (2FA)</div>
                      <div className="text-sm text-[var(--text-muted)]">Enforce 2FA for all admin users</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked />
                      <div className="w-11 h-6 bg-[var(--bg-2)] rounded-full peer peer-checked:after:translate-x-full peer-checked:bg-green-600 after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                    </label>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                    <div>
                      <div className="font-medium">IP Restrictions</div>
                      <div className="text-sm text-[var(--text-muted)]">Restrict admin access by IP</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" />
                      <div className="w-11 h-6 bg-[var(--bg-2)] rounded-full peer peer-checked:after:translate-x-full peer-checked:bg-green-600 after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                    <div>
                      <div className="font-medium">Password Policy</div>
                      <div className="text-sm text-[var(--text-muted)]">Min 8 chars, complexity required</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked />
                      <div className="w-11 h-6 bg-[var(--bg-2)] rounded-full peer peer-checked:after:translate-x-full peer-checked:bg-green-600 after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* AI Tab */}
          {activeTab === 'ai' && (
            <div className="space-y-6">
              <div className="glass-panel rounded-xl p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">AI Feature Flags</h2>
                <div className="space-y-4">
                  {[
                    { name: 'AI Auto-Triage', key: 'auto_triage', enabled: true },
                    { name: 'AI Auto-Assign', key: 'auto_assign', enabled: true },
                    { name: 'Sentiment Analysis', key: 'sentiment_analysis', enabled: true },
                    { name: 'Smart Reply', key: 'smarter_reply', enabled: true },
                    { name: 'SLA Prediction', key: 'sla_prediction', enabled: true },
                    { name: 'KB Suggestions', key: 'kb_suggestions', enabled: true },
                  ].map(flag => (
                    <div key={flag.key} className="flex items-center justify-between p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                      <div>
                        <div className="font-medium">{flag.name}</div>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" defaultChecked={flag.enabled} />
                        <div className="w-11 h-6 bg-[var(--bg-2)] rounded-full peer peer-checked:after:translate-x-full peer-checked:bg-green-600 after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              <div className="glass-panel rounded-xl p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">RAG Configuration</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                    <div className="text-sm text-[var(--text-muted)] mb-1">Embedding Model</div>
                    <div className="font-mono text-sm">nomic-embed-text</div>
                  </div>
                  <div className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                    <div className="text-sm text-[var(--text-muted)] mb-1">Vector Dimensions</div>
                    <div className="font-mono text-sm">768</div>
                  </div>
                  <div className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                    <div className="text-sm text-[var(--text-muted)] mb-1">Indexed Documents</div>
                    <div className="font-mono text-sm">142</div>
                  </div>
                  <div className="p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)]">
                    <div className="text-sm text-[var(--text-muted)] mb-1">Index Status</div>
                    <div className="font-mono text-sm text-green-400">● HEALTHY</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Automation Tab */}
          {activeTab === 'automation' && (
            <div className="space-y-6">
              <div className="glass-panel rounded-xl p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">Workflow Engine</h2>
                <div className="space-y-3">
                  <Link to="/desk/workflows" className="block p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)] hover:border-[var(--accent-gold)] transition">
                    <div className="font-medium">⚡ Workflow Builder</div>
                    <div className="text-sm text-[var(--text-muted)]">Create and manage automation rules</div>
                  </Link>
                  <Link to="/desk/rules" className="block p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)] hover:border-[var(--accent-gold)] transition">
                    <div className="font-medium">📋 Rules Engine</div>
                    <div className="text-sm text-[var(--text-muted)]">View active rules and triggers</div>
                  </Link>
                </div>
              </div>

              <div className="glass-panel rounded-xl p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">Playbooks</h2>
                <div className="space-y-3">
                  <Link to="/desk/playbooks" className="block p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)] hover:border-[var(--accent-gold)] transition">
                    <div className="font-medium">📚 Operational Playbooks</div>
                    <div className="text-sm text-[var(--text-muted)]">Incident response templates</div>
                  </Link>
                </div>
              </div>
            </div>
          )}

          {/* Services Tab */}
          {activeTab === 'services' && (
            <div className="space-y-6">
              <div className="glass-panel rounded-xl p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">Service Catalog</h2>
                <div className="space-y-3">
                  <Link to="/desk/admin/services" className="block p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)] hover:border-[var(--accent-gold)] transition">
                    <div className="font-medium">🛠️ Service Catalog</div>
                    <div className="text-sm text-[var(--text-muted)]">Manage services and intake forms</div>
                  </Link>
                  <Link to="/desk/kb" className="block p-4 bg-[var(--bg)] rounded-lg border border-[var(--border)] hover:border-[var(--accent-gold)] transition">
                    <div className="font-medium">📚 Knowledge Base</div>
                    <div className="text-sm text-[var(--text-muted)]">KB articles and categories</div>
                  </Link>
                </div>
              </div>

              <div className="glass-panel rounded-xl p-6">
                <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-2)] mb-4">SLA Policies</h2>
                <div className="text-center py-8 text-[var(--text-muted)]">
                  <div className="text-3xl mb-2">⏰</div>
                  <p>Configure SLA policies per service</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
