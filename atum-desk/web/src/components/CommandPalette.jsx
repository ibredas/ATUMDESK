import React, { useState, useEffect, useRef, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, ArrowRight, LayoutDashboard, Inbox, BookOpen, Shield, Activity, Settings, FileText, Cpu, AlertTriangle, Boxes, GitPullRequest, X } from 'lucide-react'

const ALL_COMMANDS = [
    { label: 'Dashboard', path: '/desk/dashboard', icon: LayoutDashboard, group: 'Navigation' },
    { label: 'Inbox', path: '/desk/inbox', icon: Inbox, group: 'Navigation' },
    { label: 'Knowledge Base', path: '/desk/kb', icon: BookOpen, group: 'Navigation' },
    { label: 'Problems', path: '/desk/problems', icon: AlertTriangle, group: 'Navigation' },
    { label: 'Changes', path: '/desk/changes', icon: GitPullRequest, group: 'Navigation' },
    { label: 'Assets', path: '/desk/assets', icon: Boxes, group: 'Navigation' },
    { label: 'Workflows', path: '/desk/workflows', icon: Activity, group: 'Navigation' },
    { label: 'Playbooks', path: '/desk/playbooks', icon: FileText, group: 'Navigation' },
    { label: 'SLA Alerts', path: '/desk/sla-alerts', icon: AlertTriangle, group: 'Navigation' },
    { label: 'Incidents', path: '/desk/incidents', icon: AlertTriangle, group: 'Navigation' },
    { label: 'Audit Log', path: '/desk/audit', icon: FileText, group: 'Navigation' },
    { label: 'AI Analytics', path: '/desk/ai/analytics', icon: Cpu, group: 'AI' },
    { label: 'AI Agent Assist', path: '/desk/ai/assist', icon: Cpu, group: 'AI' },
    { label: 'AI SLA Prediction', path: '/desk/ai/sla', icon: Cpu, group: 'AI' },
    { label: 'Admin Dashboard', path: '/desk/admin/dashboard', icon: Settings, group: 'Admin' },
    { label: 'Security', path: '/desk/admin/security', icon: Shield, group: 'Admin' },
    { label: 'Policies', path: '/desk/admin/policies', icon: Shield, group: 'Admin' },
    { label: 'Monitoring', path: '/desk/monitoring', icon: Activity, group: 'Admin' },
]

export default function CommandPalette() {
    const [open, setOpen] = useState(false)
    const [query, setQuery] = useState('')
    const [selected, setSelected] = useState(0)
    const inputRef = useRef(null)
    const navigate = useNavigate()

    // Ctrl+K listener
    useEffect(() => {
        const handler = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault()
                setOpen(prev => !prev)
                setQuery('')
                setSelected(0)
            }
            if (e.key === 'Escape') setOpen(false)
        }
        window.addEventListener('keydown', handler)
        return () => window.removeEventListener('keydown', handler)
    }, [])

    useEffect(() => {
        if (open && inputRef.current) inputRef.current.focus()
    }, [open])

    const filtered = useMemo(() => {
        if (!query) return ALL_COMMANDS
        const q = query.toLowerCase()
        return ALL_COMMANDS.filter(c => c.label.toLowerCase().includes(q) || c.group.toLowerCase().includes(q))
    }, [query])

    const execute = (cmd) => {
        navigate(cmd.path)
        setOpen(false)
        setQuery('')
    }

    const handleKeyDown = (e) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault()
            setSelected(s => Math.min(s + 1, filtered.length - 1))
        } else if (e.key === 'ArrowUp') {
            e.preventDefault()
            setSelected(s => Math.max(s - 1, 0))
        } else if (e.key === 'Enter' && filtered[selected]) {
            execute(filtered[selected])
        }
    }

    if (!open) return null

    // Group results
    const groups = {}
    filtered.forEach(c => {
        if (!groups[c.group]) groups[c.group] = []
        groups[c.group].push(c)
    })

    let flatIndex = -1

    return (
        <div className="fixed inset-0 z-[9999] flex items-start justify-center pt-[15vh]" onClick={() => setOpen(false)}>
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

            {/* Palette */}
            <div
                className="relative w-full max-w-lg mx-4 bg-[var(--atum-bg-2)] border border-[var(--atum-border)] rounded-xl shadow-2xl overflow-hidden animate-in"
                onClick={e => e.stopPropagation()}
            >
                {/* Search Input */}
                <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--atum-border)]">
                    <Search size={18} className="text-[var(--atum-text-dim)]" />
                    <input
                        ref={inputRef}
                        value={query}
                        onChange={e => { setQuery(e.target.value); setSelected(0) }}
                        onKeyDown={handleKeyDown}
                        placeholder="Search pages, actions..."
                        className="flex-1 bg-transparent text-sm text-white outline-none placeholder:text-[var(--atum-text-dim)]"
                    />
                    <kbd className="hidden sm:flex items-center gap-1 px-2 py-0.5 rounded bg-[var(--atum-surface)] border border-[var(--atum-border)] text-[10px] text-[var(--atum-text-dim)] font-mono">
                        ESC
                    </kbd>
                </div>

                {/* Results */}
                <div className="max-h-[50vh] overflow-y-auto py-2">
                    {filtered.length === 0 && (
                        <div className="px-4 py-8 text-center text-sm text-[var(--atum-text-dim)]">No results found.</div>
                    )}
                    {Object.entries(groups).map(([group, commands]) => (
                        <div key={group}>
                            <div className="px-4 py-1.5 text-[10px] font-semibold text-[var(--atum-text-dim)] uppercase tracking-widest">
                                {group}
                            </div>
                            {commands.map(cmd => {
                                flatIndex++
                                const idx = flatIndex
                                return (
                                    <button
                                        key={cmd.path}
                                        onClick={() => execute(cmd)}
                                        className={`w-full flex items-center gap-3 px-4 py-2.5 text-left text-sm transition-colors ${idx === selected
                                                ? 'bg-[var(--atum-surface)] text-white'
                                                : 'text-[var(--atum-text-muted)] hover:bg-[var(--atum-surface)] hover:text-white'
                                            }`}
                                    >
                                        <cmd.icon size={16} className={idx === selected ? 'text-[var(--atum-accent-gold)]' : ''} />
                                        <span className="flex-1">{cmd.label}</span>
                                        <ArrowRight size={12} className="opacity-0 group-hover:opacity-100" />
                                    </button>
                                )
                            })}
                        </div>
                    ))}
                </div>

                {/* Footer hint */}
                <div className="px-4 py-2 border-t border-[var(--atum-border)] flex items-center gap-4 text-[10px] text-[var(--atum-text-dim)]">
                    <span>↑↓ Navigate</span>
                    <span>↵ Open</span>
                    <span>ESC Close</span>
                </div>
            </div>
        </div>
    )
}
