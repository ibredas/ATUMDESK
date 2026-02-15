import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Sparkles } from 'lucide-react'

export default function HeroSplitCTA() {
    return (
        <section className="relative overflow-hidden py-24 lg:py-32">
            {/* Background Glow */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-[radial-gradient(circle,rgba(217,181,90,0.08)_0%,transparent_70%)] pointer-events-none" />
            <div className="absolute top-1/4 right-0 w-[400px] h-[400px] bg-[radial-gradient(circle,rgba(59,130,246,0.04)_0%,transparent_60%)] pointer-events-none" />

            <div className="section-container relative z-10">
                <div className="grid lg:grid-cols-2 gap-16 items-center">
                    {/* Left: Copy */}
                    <div className="animate-in-up">
                        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--atum-surface-2)] border border-[var(--atum-border)] text-xs font-medium text-[var(--atum-accent-gold)] mb-6">
                            <Sparkles size={12} />
                            <span>Enterprise Service Management</span>
                        </div>
                        <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white leading-[1.1] mb-6 tracking-tight">
                            Service Desk,<br />
                            <span className="text-[var(--atum-accent-gold)]">Reimagined.</span>
                        </h1>
                        <p className="text-lg text-[var(--atum-text-muted)] leading-relaxed max-w-xl mb-8">
                            ATUM Nexus is the enterprise ITSM platform built for teams who need
                            full control — on-prem deployment, AI copilot, zero-trust security,
                            and no vendor lock-in.
                        </p>
                        <div className="flex flex-wrap gap-4">
                            <Link to="/demo" className="btn-gold text-base py-3 px-6">
                                Book Demo <ArrowRight size={16} />
                            </Link>
                            <Link to="/overview" className="btn-outline text-base py-3 px-6">
                                Product Tour
                            </Link>
                        </div>
                    </div>

                    {/* Right: Abstract Visual */}
                    <div className="hidden lg:flex justify-center animate-in-up" style={{ animationDelay: '0.15s' }}>
                        <div className="relative w-[420px] h-[340px]">
                            {/* Glass Dashboard Preview */}
                            <div className="absolute inset-0 rounded-2xl bg-[var(--atum-surface-2)] border border-[var(--atum-border)] backdrop-blur-sm overflow-hidden shadow-2xl">
                                {/* Title bar */}
                                <div className="h-10 border-b border-[var(--atum-border)] flex items-center px-4 gap-2">
                                    <div className="w-3 h-3 rounded-full bg-red-500/40" />
                                    <div className="w-3 h-3 rounded-full bg-yellow-500/40" />
                                    <div className="w-3 h-3 rounded-full bg-green-500/40" />
                                    <span className="ml-4 text-[10px] text-[var(--atum-text-dim)] font-mono">atum-nexus — dashboard</span>
                                </div>
                                {/* Mock content */}
                                <div className="p-4 space-y-3">
                                    <div className="grid grid-cols-3 gap-3">
                                        {[
                                            { label: 'Open', val: '24', color: '#FBBF24' },
                                            { label: 'Resolved', val: '156', color: '#34D399' },
                                            { label: 'SLA Met', val: '98%', color: '#60A5FA' },
                                        ].map(s => (
                                            <div key={s.label} className="rounded-lg bg-[var(--atum-surface)] border border-[var(--atum-border)] p-3 text-center">
                                                <div className="text-xl font-bold" style={{ color: s.color }}>{s.val}</div>
                                                <div className="text-[10px] text-[var(--atum-text-dim)]">{s.label}</div>
                                            </div>
                                        ))}
                                    </div>
                                    {/* Mock rows */}
                                    {[1, 2, 3, 4].map(i => (
                                        <div key={i} className="flex items-center gap-3 py-2 border-b border-[var(--atum-border)] last:border-0">
                                            <div className="w-2 h-2 rounded-full bg-[var(--atum-accent-gold)]" />
                                            <div className="flex-1 h-2.5 rounded bg-[var(--atum-surface-3)]" style={{ width: `${60 + i * 8}%` }} />
                                            <div className="w-12 h-2.5 rounded bg-[var(--atum-surface-2)]" />
                                        </div>
                                    ))}
                                </div>
                            </div>
                            {/* Floating badge */}
                            <div className="absolute -bottom-4 -right-4 px-4 py-2 rounded-xl bg-[var(--atum-bg-2)] border border-[var(--atum-border-gold)] shadow-xl text-xs font-medium text-[var(--atum-accent-gold)] animate-pulse-gold">
                                <Sparkles size={12} className="inline mr-1.5" />AI Copilot Active
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
}
