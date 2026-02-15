import React, { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom'
import {
    LayoutDashboard, Inbox, BookOpen, AlertTriangle, Wrench, Boxes,
    GitPullRequest, Shield, Activity, Cpu, FileText, Settings,
    ChevronLeft, ChevronRight, LogOut, Search, Plus, Ticket,
    Siren, ClipboardList, Command
} from 'lucide-react'

// Sidebar Groups
const NAV_GROUPS = [
    {
        title: 'Desk',
        items: [
            { label: 'Dashboard', path: '/desk/dashboard', icon: LayoutDashboard },
            {
                label: 'Inbox', path: '/desk/inbox', icon: Inbox,
                actions: [
                    { label: 'New Ticket', icon: Plus, action: 'new-ticket' },
                ]
            },
            { label: 'Knowledge', path: '/desk/kb', icon: BookOpen },
            { label: 'Problems', path: '/desk/problems', icon: AlertTriangle },
            { label: 'Changes', path: '/desk/changes', icon: GitPullRequest },
            { label: 'Assets', path: '/desk/assets', icon: Boxes },
        ]
    },
    {
        title: 'Operations',
        items: [
            { label: 'Incidents', path: '/desk/incidents', icon: Siren },
            { label: 'Postmortems', path: '/desk/postmortems', icon: ClipboardList },
            { label: 'Workflows', path: '/desk/workflows', icon: Activity },
            { label: 'Playbooks', path: '/desk/playbooks', icon: FileText },
            { label: 'SLA Alerts', path: '/desk/sla-alerts', icon: AlertTriangle },
        ]
    },
    {
        title: 'AI Intelligence',
        items: [
            { label: 'Control Center', path: '/desk/admin/ai', icon: Cpu, needs_admin: true },
            { label: 'Analytics Hub', path: '/desk/ai/analytics', icon: Activity },
            { label: 'Agent Assist', path: '/desk/ai/assist', icon: Cpu },
        ]
    },
    {
        title: 'Admin',
        items: [
            { label: 'System', path: '/desk/admin/dashboard', icon: Settings, needs_admin: true },
            { label: 'Security', path: '/desk/admin/security', icon: Shield, needs_admin: true },
            { label: 'Policies', path: '/desk/admin/policies', icon: Shield, needs_admin: true },
            { label: 'Audit Log', path: '/desk/audit', icon: FileText, needs_admin: true },
            { label: 'Monitoring', path: '/desk/monitoring', icon: Activity, needs_admin: true },
        ]
    }
]

export default function DeskLayout() {
    const [collapsed, setCollapsed] = useState(localStorage.getItem('atum_sidebar_collapsed') === 'true')
    const location = useLocation()
    const navigate = useNavigate()

    const toggleSidebar = () => {
        const newState = !collapsed
        setCollapsed(newState)
        localStorage.setItem('atum_sidebar_collapsed', newState)
    }

    const logout = () => {
        localStorage.removeItem('atum_desk_token')
        navigate('/desk/login')
    }

    return (
        <div className="flex min-h-screen bg-[var(--atum-bg)] text-[var(--atum-text)] font-sans antialiased overflow-hidden">

            {/* ── SIDEBAR ── */}
            <aside
                className={`flex-shrink-0 bg-[var(--atum-bg-2)] border-r border-[var(--atum-border)] transition-all duration-300 flex flex-col relative z-20 ${collapsed ? 'w-[72px]' : 'w-64'
                    }`}
            >
                {/* Brand */}
                <div className="h-16 flex items-center px-5 border-b border-[var(--atum-border)]">
                    <Link to="/desk/dashboard" className="flex items-center gap-3 group">
                        <div className="w-9 h-9 rounded-lg bg-[var(--atum-accent-gold)] flex items-center justify-center flex-shrink-0 shadow-[0_0_15px_var(--atum-accent-glow)] group-hover:shadow-[0_0_25px_var(--atum-accent-glow-strong)] transition-shadow">
                            <span className="text-black font-extrabold text-lg leading-none">A</span>
                        </div>
                        {!collapsed && (
                            <div className="animate-in">
                                <h1 className="font-bold tracking-tight text-white text-sm">ATUM NEXUS</h1>
                                <p className="text-[9px] text-[var(--atum-accent-gold)] tracking-[0.2em] font-semibold">ENTERPRISE</p>
                            </div>
                        )}
                    </Link>
                </div>

                {/* Toggle */}
                <button
                    onClick={toggleSidebar}
                    className="absolute -right-3 top-20 bg-[var(--atum-bg-2)] border border-[var(--atum-border)] text-[var(--atum-text-muted)] rounded-full p-1 hover:text-white hover:border-[var(--atum-accent-gold)] transition-colors z-50 shadow-lg"
                >
                    {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
                </button>

                {/* Quick Search Hint */}
                {!collapsed && (
                    <div className="px-4 pt-4">
                        <button
                            onClick={() => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', ctrlKey: true }))}
                            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-[var(--atum-surface)] border border-[var(--atum-border)] text-xs text-[var(--atum-text-dim)] hover:border-[var(--atum-border-strong)] hover:text-[var(--atum-text-muted)] transition-colors"
                        >
                            <Search size={13} />
                            <span className="flex-1 text-left">Search...</span>
                            <kbd className="text-[10px] font-mono bg-[var(--atum-bg)] px-1.5 py-0.5 rounded border border-[var(--atum-border)]">⌘K</kbd>
                        </button>
                    </div>
                )}

                {/* Nav Items */}
                <div className="flex-1 overflow-y-auto py-4 space-y-6 px-3 no-scrollbar">
                    {NAV_GROUPS.map((group, idx) => (
                        <div key={idx}>
                            {!collapsed && (
                                <h3 className="px-2 text-[10px] uppercase tracking-widest text-[var(--atum-text-dim)] font-bold mb-2">
                                    {group.title}
                                </h3>
                            )}
                            {collapsed && idx > 0 && <div className="h-px bg-[var(--atum-border)] mx-2 my-2" />}

                            <div className="space-y-0.5">
                                {group.items.map((item) => {
                                    const isActive = location.pathname === item.path ||
                                        (item.path !== '/desk/dashboard' && location.pathname.startsWith(item.path + '/'))
                                    return (
                                        <div key={item.path} className="relative group">
                                            <Link
                                                to={item.path}
                                                className={`flex items-center px-3 py-2 rounded-lg transition-all duration-200 relative ${isActive
                                                    ? 'bg-[var(--atum-glass-hover)] text-white'
                                                    : 'text-[var(--atum-text-muted)] hover:bg-[var(--atum-surface)] hover:text-white'
                                                    }`}
                                                title={collapsed ? item.label : undefined}
                                            >
                                                {/* Active indicator */}
                                                {isActive && (
                                                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r bg-[var(--atum-accent-gold)]" />
                                                )}

                                                <item.icon
                                                    size={18}
                                                    className={`transition-colors flex-shrink-0 ${isActive ? 'text-[var(--atum-accent-gold)]' : ''}`}
                                                    strokeWidth={1.5}
                                                />

                                                {!collapsed && (
                                                    <>
                                                        <span className="ml-3 text-[13px] font-medium flex-1 truncate">{item.label}</span>
                                                        {/* Quick Actions on Hover */}
                                                        {item.actions && (
                                                            <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                                                                {item.actions.map((action, i) => (
                                                                    <button
                                                                        key={i}
                                                                        className="p-1 hover:bg-[var(--atum-surface-2)] rounded text-[var(--atum-accent-gold)]"
                                                                        title={action.label}
                                                                        onClick={(e) => {
                                                                            e.preventDefault()
                                                                            e.stopPropagation()
                                                                            if (action.action === 'new-ticket') navigate('/desk/inbox')
                                                                        }}
                                                                    >
                                                                        <action.icon size={13} />
                                                                    </button>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </>
                                                )}
                                            </Link>

                                            {/* Collapsed tooltip */}
                                            {collapsed && (
                                                <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1.5 rounded-lg bg-[var(--atum-bg-3)] border border-[var(--atum-border)] text-xs text-white whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none shadow-xl z-50">
                                                    {item.label}
                                                </div>
                                            )}
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    ))}
                </div>

                {/* User Footer */}
                <div className="p-3 border-t border-[var(--atum-border)]">
                    <div className={`flex items-center ${collapsed ? 'justify-center' : 'gap-3'}`}>
                        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[var(--atum-accent-gold)] to-[#b39238] flex items-center justify-center text-black text-xs font-bold flex-shrink-0">
                            AD
                        </div>
                        {!collapsed && (
                            <div className="flex-1 min-w-0">
                                <div className="text-[13px] font-medium text-white truncate">Administrator</div>
                                <button onClick={logout} className="text-[11px] text-[var(--atum-text-muted)] hover:text-red-400 flex items-center gap-1 mt-0.5 transition-colors">
                                    <LogOut size={10} /> Sign Out
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </aside>

            {/* ── MAIN CONTENT ── */}
            <main className="flex-1 min-w-0 bg-[var(--atum-bg)] overflow-y-auto relative no-scrollbar">
                <div className="p-6 md:p-8 lg:p-10 max-w-[1600px] mx-auto min-h-screen">
                    <Outlet />
                </div>
            </main>

        </div>
    )
}
