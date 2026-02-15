import React from 'react'
import { Quote } from 'lucide-react'

const DEFAULT_QUOTES = [
    {
        quote: "ATUM Desk reduced our average resolution time by 60%. The AI suggestions are genuinely useful — they've transformed how our agents work.",
        author: "Sarah Chen",
        role: "VP of Customer Success",
        company: "TechCorp Inc."
    },
    {
        quote: "We switched from Zendesk and saw immediate improvements. The SLA tracking alone is worth the switch — no more missed deadlines.",
        author: "Marcus Johnson",
        role: "Head of IT Operations",
        company: "GlobalServe Ltd."
    },
    {
        quote: "The knowledge base deflection feature saves us 200+ tickets per month. Our customers find answers before they even submit a request.",
        author: "Amira Patel",
        role: "Director of Support",
        company: "CloudBase Systems"
    }
]

/**
 * CustomerQuotes — landing page testimonials section.
 * 
 * Usage:
 *   <CustomerQuotes />
 *   <CustomerQuotes quotes={[{ quote, author, role, company }]} />
 */
export default function CustomerQuotes({ quotes = DEFAULT_QUOTES, className = '' }) {
    return (
        <section className={`py-20 px-6 ${className}`}>
            <div className="max-w-6xl mx-auto">
                <h2 className="text-3xl font-bold text-center mb-4">
                    Trusted by <span className="text-[var(--atum-accent-gold)]">Support Teams</span> Worldwide
                </h2>
                <p className="text-center text-[var(--atum-text-muted)] mb-12 max-w-2xl mx-auto">
                    See what teams are saying about their experience with ATUM Desk
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {quotes.map((q, idx) => (
                        <div
                            key={idx}
                            className="glass-panel p-6 rounded-xl border border-[var(--atum-border)] hover:border-[var(--atum-accent-gold)] transition-colors"
                        >
                            <Quote size={24} className="text-[var(--atum-accent-gold)] mb-4 opacity-50" />
                            <p className="text-sm leading-relaxed mb-6 text-[var(--atum-text)]">
                                "{q.quote}"
                            </p>
                            <div className="border-t border-[var(--atum-border)] pt-4">
                                <div className="font-semibold text-sm">{q.author}</div>
                                <div className="text-xs text-[var(--atum-text-muted)]">
                                    {q.role}, {q.company}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}
