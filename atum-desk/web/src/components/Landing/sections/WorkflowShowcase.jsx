import React from 'react'
import { Send, Cpu, Route, CheckCircle, ArrowDown } from 'lucide-react'

const STEPS = [
    { icon: Send, title: 'Ticket Created', desc: 'Customer submits via portal, email, or API.' },
    { icon: Cpu, title: 'AI Auto-Triage', desc: 'Copilot classifies priority, category, and sentiment.' },
    { icon: Route, title: 'Smart Routing', desc: 'Rules engine assigns to the right team automatically.' },
    { icon: CheckCircle, title: 'Resolved + Indexed', desc: 'Resolution stored in KB via GraphRAG for future suggestions.' },
]

export default function WorkflowShowcase() {
    return (
        <section id="workflows" className="py-24 bg-[var(--atum-bg-2)]/40">
            <div className="section-container">
                <div className="text-center mb-14">
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                        Intelligent <span className="text-[var(--atum-accent-gold)]">Workflow</span>
                    </h2>
                    <p className="text-[var(--atum-text-muted)] max-w-2xl mx-auto">
                        From ticket creation to resolution — every step automated, observed, and optimized.
                    </p>
                </div>

                <div className="max-w-lg mx-auto space-y-0">
                    {STEPS.map((s, i) => (
                        <div key={i}>
                            <div className="flex items-start gap-5 group">
                                {/* Left: number + icon */}
                                <div className="flex flex-col items-center">
                                    <div className="w-12 h-12 rounded-xl bg-[var(--atum-surface-2)] border border-[var(--atum-border)] flex items-center justify-center group-hover:border-[var(--atum-accent-gold)] transition-colors">
                                        <s.icon size={20} className="text-[var(--atum-accent-gold)]" />
                                    </div>
                                </div>
                                {/* Right: content */}
                                <div className="pb-2">
                                    <div className="text-[10px] text-[var(--atum-text-dim)] font-semibold uppercase tracking-widest mb-1">Step {i + 1}</div>
                                    <h3 className="text-base font-semibold text-white mb-1">{s.title}</h3>
                                    <p className="text-sm text-[var(--atum-text-muted)]">{s.desc}</p>
                                </div>
                            </div>
                            {i < STEPS.length - 1 && (
                                <div className="flex items-center ml-6 my-2">
                                    <div className="w-px h-8 bg-[var(--atum-border)]" />
                                    <ArrowDown size={12} className="text-[var(--atum-text-dim)] -ml-[6px]" />
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}
