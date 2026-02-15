import React from 'react'
import { Check, X, Minus } from 'lucide-react'

const FEATURES = [
    {
        category: 'Deployment', features: [
            { name: 'On-Premise Deployment', atum: true, legacy: false },
            { name: 'Cloud / Hybrid Option', atum: true, legacy: true },
            { name: 'Zero Vendor Lock-in', atum: true, legacy: false },
            { name: 'Own Your Data', atum: true, legacy: false },
        ]
    },
    {
        category: 'AI & Automation', features: [
            { name: 'AI Auto-Triage', atum: true, legacy: 'partial' },
            { name: 'Smart Reply Drafts', atum: true, legacy: false },
            { name: 'Local LLM (No External API)', atum: true, legacy: false },
            { name: 'KB Suggestion Engine', atum: true, legacy: 'partial' },
        ]
    },
    {
        category: 'Security', features: [
            { name: 'Row-Level Security', atum: true, legacy: 'partial' },
            { name: 'Tamper-Proof Audit Chain', atum: true, legacy: false },
            { name: 'TOTP / 2FA', atum: true, legacy: true },
            { name: 'IP Restrictions', atum: true, legacy: 'partial' },
        ]
    },
    {
        category: 'Pricing', features: [
            { name: 'Transparent Pricing', atum: true, legacy: false },
            { name: 'No Per-Agent Escalation', atum: true, legacy: false },
            { name: 'Free On-Prem License', atum: true, legacy: false },
        ]
    },
]

function StatusIcon({ value }) {
    if (value === true) return <Check size={16} className="text-[var(--atum-success)]" />
    if (value === false) return <X size={16} className="text-[var(--atum-danger)] opacity-40" />
    return <Minus size={16} className="text-[var(--atum-warning)]" />
}

export default function FeatureComparisonGrid() {
    return (
        <section id="features" className="py-24">
            <div className="section-container">
                <div className="text-center mb-14">
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                        ATUM Nexus vs <span className="text-[var(--atum-text-muted)]">Legacy ITSM</span>
                    </h2>
                    <p className="text-[var(--atum-text-muted)] max-w-2xl mx-auto">
                        See how ATUM Nexus compares feature-by-feature.
                    </p>
                </div>

                <div className="max-w-3xl mx-auto glass-card overflow-hidden">
                    {/* Header */}
                    <div className="grid grid-cols-[1fr_100px_100px] items-center px-6 py-4 border-b border-[var(--atum-border)] bg-[var(--atum-surface)]">
                        <span className="text-xs font-semibold text-[var(--atum-text-dim)] uppercase tracking-widest">Feature</span>
                        <span className="text-xs font-bold text-[var(--atum-accent-gold)] uppercase tracking-widest text-center">ATUM</span>
                        <span className="text-xs font-semibold text-[var(--atum-text-dim)] uppercase tracking-widest text-center">Legacy</span>
                    </div>

                    {FEATURES.map(cat => (
                        <div key={cat.category}>
                            <div className="px-6 py-3 bg-[var(--atum-bg-2)]/60">
                                <span className="text-[11px] font-semibold text-[var(--atum-text-muted)] uppercase tracking-wider">{cat.category}</span>
                            </div>
                            {cat.features.map(f => (
                                <div key={f.name} className="grid grid-cols-[1fr_100px_100px] items-center px-6 py-3 border-b border-[var(--atum-border)] hover:bg-[var(--atum-surface)] transition-colors">
                                    <span className="text-sm text-[var(--atum-text-1)]">{f.name}</span>
                                    <div className="flex justify-center"><StatusIcon value={f.atum} /></div>
                                    <div className="flex justify-center"><StatusIcon value={f.legacy} /></div>
                                </div>
                            ))}
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}
