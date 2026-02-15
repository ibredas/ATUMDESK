import React, { useState } from 'react'
import { ChevronDown } from 'lucide-react'

const QUESTIONS = [
    { q: 'Can ATUM Nexus be deployed fully on-premise?', a: 'Yes. ATUM Nexus is designed for on-prem first. It runs on PostgreSQL + Python (FastAPI), requires no cloud services, and can operate in air-gapped environments.' },
    { q: 'Does the AI Copilot send data to external APIs?', a: 'No. The AI Copilot runs on local Ollama models. All inference happens on your hardware. No data leaves your network.' },
    { q: 'How does ATUM compare to ServiceNow?', a: 'ATUM provides comparable ITSM features (ticketing, SLA, workflows, KB, asset management) at a fraction of the cost, with full data ownership and no per-agent pricing escalation.' },
    { q: 'Is multi-tenancy supported?', a: 'Yes. ATUM Nexus enforces row-level security at the database layer. Each organization\'s data is isolated by default, with no additional configuration needed.' },
    { q: 'What about SOC2 and GDPR compliance?', a: 'ATUM Nexus includes tamper-proof audit logging, data retention policies, encryption at rest (PostgreSQL), and full export capabilities to support compliance requirements.' },
    { q: 'Can I migrate from our current ITSM tool?', a: 'Yes. ATUM provides REST APIs for bulk import and a structured data model that maps to common ITSM schemas. We also offer migration support for enterprise customers.' },
]

export default function FAQAccordion() {
    const [open, setOpen] = useState(null)

    return (
        <section className="py-24 bg-[var(--atum-bg-2)]/40">
            <div className="section-container">
                <div className="text-center mb-14">
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                        Frequently Asked <span className="text-[var(--atum-accent-gold)]">Questions</span>
                    </h2>
                </div>

                <div className="max-w-2xl mx-auto space-y-2">
                    {QUESTIONS.map((item, i) => (
                        <div
                            key={i}
                            className="glass-card overflow-hidden"
                        >
                            <button
                                onClick={() => setOpen(open === i ? null : i)}
                                className="w-full flex items-center justify-between p-5 text-left"
                            >
                                <span className="text-sm font-medium text-white pr-4">{item.q}</span>
                                <ChevronDown
                                    size={18}
                                    className={`text-[var(--atum-text-muted)] transition-transform flex-shrink-0 ${open === i ? 'rotate-180' : ''}`}
                                />
                            </button>
                            <div
                                className={`overflow-hidden transition-all duration-300 ${open === i ? 'max-h-60 opacity-100' : 'max-h-0 opacity-0'}`}
                            >
                                <p className="px-5 pb-5 text-sm text-[var(--atum-text-muted)] leading-relaxed">
                                    {item.a}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}
