import React from 'react'
import { TrendingUp, Building2, Headphones, Server, Award, BarChart3 } from 'lucide-react'

const CASES = [
    {
        icon: Building2,
        industry: 'Financial Services',
        title: '73% faster resolution',
        body: 'A major banking group migrated from ServiceNow to ATUM Nexus, cutting mean-time-to-resolve from 4.2 hours to 1.1 hours with AI-assisted triage.',
        metric: '73%',
        metricLabel: 'Faster MTTR',
    },
    {
        icon: Server,
        industry: 'Technology',
        title: 'Zero-downtime SLA compliance',
        body: 'A SaaS provider achieved 99.95% SLA compliance across 12,000 monthly tickets using automated escalation and predictive breach alerts.',
        metric: '99.95%',
        metricLabel: 'SLA Compliance',
    },
    {
        icon: Headphones,
        industry: 'Healthcare',
        title: 'On-prem + HIPAA compliant',
        body: 'A hospital network deployed ATUM Nexus on-prem with full audit chain, achieving HIPAA compliance without any cloud dependency.',
        metric: '100%',
        metricLabel: 'On-Prem Control',
    },
    {
        icon: BarChart3,
        industry: 'Government',
        title: '60% reduction in manual workload',
        body: 'A federal agency automated 60% of ticket classification using ATUM AI Copilot, freeing agents for complex incidents.',
        metric: '60%',
        metricLabel: 'Automation Rate',
    },
]

export default function OutcomeCaseStudies() {
    return (
        <section className="py-24">
            <div className="section-container">
                <div className="text-center mb-14">
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                        Proven <span className="text-[var(--atum-accent-gold)]">Outcomes</span>
                    </h2>
                    <p className="text-[var(--atum-text-muted)] max-w-2xl mx-auto">
                        Organizations across industries trust ATUM Nexus to transform their service operations.
                    </p>
                </div>

                <div className="grid md:grid-cols-2 gap-6 stagger">
                    {CASES.map(c => (
                        <div
                            key={c.title}
                            className="glass-card glow-edge p-6 flex flex-col animate-in-up"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-[var(--atum-surface-2)] border border-[var(--atum-border)] flex items-center justify-center">
                                        <c.icon size={18} className="text-[var(--atum-accent-gold)]" />
                                    </div>
                                    <span className="text-[10px] font-semibold text-[var(--atum-text-dim)] uppercase tracking-widest">
                                        {c.industry}
                                    </span>
                                </div>
                                <div className="text-right">
                                    <div className="text-xl font-bold text-[var(--atum-accent-gold)]">{c.metric}</div>
                                    <div className="text-[10px] text-[var(--atum-text-dim)]">{c.metricLabel}</div>
                                </div>
                            </div>
                            <h3 className="text-base font-semibold text-white mb-2">{c.title}</h3>
                            <p className="text-sm text-[var(--atum-text-muted)] leading-relaxed flex-1">{c.body}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}
