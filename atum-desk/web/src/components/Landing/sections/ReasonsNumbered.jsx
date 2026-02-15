import React from 'react'

const REASONS = [
    {
        title: 'Full On-Prem Control',
        body: 'Deploy on your own infrastructure. No cloud dependency, no data sovereignty concerns. Your data never leaves your network.',
    },
    {
        title: 'AI Copilot Built In',
        body: 'Local LLM-powered triage, smart replies, and KB suggestions — no external API calls. Runs on Ollama with complete data privacy.',
    },
    {
        title: 'Zero Vendor Lock-in',
        body: 'Open architecture, standard PostgreSQL, no proprietary formats. Export everything, migrate anytime, own your data forever.',
    },
    {
        title: 'Enterprise Security by Default',
        body: 'Row-level security, tamper-proof audit chains, 2FA/TOTP, attachment scanning, rate limiting, and IP restrictions out of the box.',
    },
    {
        title: 'ServiceNow-Class Features, Not Pricing',
        body: 'SLA management, visual workflows, playbooks, asset tracking, knowledge base — enterprise features without enterprise invoices.',
    },
    {
        title: 'True Multi-Tenancy',
        body: 'Isolated tenants sharing one deployment. Every query enforces organization boundaries — no data leaks, no cross-contamination.',
    },
    {
        title: 'Built for Developers',
        body: 'REST API with OpenAPI docs, webhook integrations, job queue architecture, and structured logging. Extend and integrate with anything.',
    },
]

export default function ReasonsNumbered() {
    return (
        <section className="py-24 bg-[var(--atum-bg-2)]/40">
            <div className="section-container">
                <div className="text-center mb-14">
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                        Why <span className="text-[var(--atum-accent-gold)]">ATUM Nexus</span>
                    </h2>
                    <p className="text-[var(--atum-text-muted)] max-w-2xl mx-auto">
                        Seven reasons teams choose ATUM over legacy ITSM solutions.
                    </p>
                </div>

                <div className="max-w-3xl mx-auto space-y-0">
                    {REASONS.map((r, i) => (
                        <div key={i} className="flex gap-6 py-8 border-b border-[var(--atum-border)] last:border-0 group">
                            <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-[var(--atum-surface-2)] border border-[var(--atum-border)] flex items-center justify-center text-lg font-bold text-[var(--atum-accent-gold)] group-hover:bg-[var(--atum-accent-gold)] group-hover:text-black transition-all">
                                {String(i + 1).padStart(2, '0')}
                            </div>
                            <div>
                                <h3 className="text-base font-semibold text-white mb-1">{r.title}</h3>
                                <p className="text-sm text-[var(--atum-text-muted)] leading-relaxed">{r.body}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}
