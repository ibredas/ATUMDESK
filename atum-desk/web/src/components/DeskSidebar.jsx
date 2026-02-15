import React from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Wordmark } from './Brand/Wordmark'

export default function DeskSidebar() {
    const location = useLocation()
    const navigate = useNavigate()

    const logout = () => {
        localStorage.removeItem('atum_desk_token')
        localStorage.removeItem('atum_desk_refresh')
        navigate('/desk/login')
    }

    const isActive = (path) => location.pathname === path ? 'active' : ''

    return (
        <div className="desk-sidebar">
            <div className="px-6 mb-8">
                <Wordmark className="h-6 text-[var(--accent-gold)]" suffix="DESK" />
            </div>
            <nav className="flex flex-col gap-1">
                <Link to="/desk/dashboard" className={isActive('/desk/dashboard')}>📊 Dashboard</Link>
                <Link to="/desk/inbox" className={isActive('/desk/inbox')}>📥 Inbox</Link>
                <Link to="/desk/kb" className={isActive('/desk/kb')}>📚 Knowledge</Link>
                <Link to="/desk/problems" className={isActive('/desk/problems')}>🧩 Problems</Link>
                <Link to="/desk/changes" className={isActive('/desk/changes')}>🚧 Changes</Link>
                <Link to="/desk/assets" className={isActive('/desk/assets')}>💻 Assets</Link>

                {/* NEW: Operations Section */}
                <div className="mt-4 pt-4 border-t border-[var(--border)]">
                    <span className="text-xs text-[var(--text-muted)] uppercase tracking-wider px-2">Operations</span>
                </div>
                <Link to="/desk/workflows" className={isActive('/desk/workflows')}>⚡ Workflows</Link>
                <Link to="/desk/playbooks" className={isActive('/desk/playbooks')}>📋 Playbooks</Link>
                <Link to="/desk/sla-alerts" className={isActive('/desk/sla-alerts')}>⏰ SLA Alerts</Link>

                {/* AI Section */}
                <div className="mt-4 pt-4 border-t border-[var(--border)]">
                    <span className="text-xs text-[var(--accent-gold)] uppercase tracking-wider px-2">◆ AI Intelligence</span>
                </div>
                <Link to="/desk/ai/analytics" className={isActive('/desk/ai/analytics')}>🤖 AI Hub</Link>
                <Link to="/desk/ai/insights" className={isActive('/desk/ai/insights')}>💡 Smart Insights</Link>
                <Link to="/desk/ai/agent-assist" className={isActive('/desk/ai/agent-assist')}>🎯 Agent Assist</Link>
                <Link to="/desk/ai/sla-prediction" className={isActive('/desk/ai/sla-prediction')}>🔮 SLA Predict</Link>

                {/* NEW: Governance Section */}
                <div className="mt-4 pt-4 border-t border-[var(--border)]">
                    <span className="text-xs text-[var(--text-muted)] uppercase tracking-wider px-2">Governance</span>
                </div>
                <Link to="/desk/audit" className={isActive('/desk/audit')}>📝 Audit Log</Link>
                <Link to="/desk/monitoring" className={isActive('/desk/monitoring')}>📈 Monitoring</Link>
                <Link to="/desk/incidents" className={isActive('/desk/incidents')}>🚨 Incidents</Link>
                <Link to="/desk/postmortems" className={isActive('/desk/postmortems')}>📋 Postmortems</Link>
                <Link to="/desk/kb-suggestions" className={isActive('/desk/kb-suggestions')}>💡 KB Deflection</Link>

                {/* NEW: Admin Section */}
                <div className="mt-4 pt-4 border-t border-[var(--border)]">
                    <span className="text-xs text-[var(--accent-gold)] uppercase tracking-wider px-2">◆ Admin</span>
                </div>
                <Link to="/desk/admin" className={isActive('/desk/admin')}>🎛️ Control Center</Link>
                <Link to="/desk/admin/jobs" className={isActive('/desk/admin/jobs')}>📋 Job Queue</Link>
                <Link to="/desk/admin/policies" className={isActive('/desk/admin/policies')}>🛡️ Policy Center</Link>
                <Link to="/desk/admin/ip-restrictions" className={isActive('/desk/admin/ip-restrictions')}>🔐 IP Restrictions</Link>
                <Link to="/desk/admin/ai-control" className={isActive('/desk/admin/ai-control')}>🤖 AI & RAG</Link>
                <Link to="/desk/admin/forms" className={isActive('/desk/admin/forms')}>📝 Forms Studio</Link>
                <Link to="/desk/admin/org" className={isActive('/desk/admin/org')}>👥 Organization</Link>
                <Link to="/desk/admin/security" className={isActive('/desk/admin/security')}>🔒 Security</Link>

                <div className="mt-auto pt-8">
                    <button onClick={logout}>🚪 Sign Out</button>
                </div>
            </nav>
        </div>
    )
}
