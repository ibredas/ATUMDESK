import React from 'react'
import LandingShell from '../../components/Landing/LandingShell'
import FinalCTA from '../../components/Landing/sections/FinalCTA'
import { Cpu, Sparkles, Brain, Shield, MessageSquare, BookOpen, TrendingUp, Lightbulb } from 'lucide-react'

const AI_FEATURES = [
    {
        icon: Sparkles,
        title: 'AI Auto-Triage',
        desc: 'Incoming tickets are automatically classified by priority, category, and sentiment using local LLM inference. No external API calls.',
    },
    {
        icon: MessageSquare,
        title: 'Smart Reply Drafts',
        desc: 'Context-aware response suggestions generated from ticket history, KB articles, and resolution patterns.',
    },
    {
        icon: BookOpen,
        title: 'KB Auto-Suggestions',
        desc: 'When a ticket is created, the copilot surfaces relevant KB articles to both agents and customers — reducing repeat questions.',
    },
    {
        icon: Brain,
        title: 'GraphRAG Integration',
        desc: 'Resolved tickets are indexed into a retrieval-augmented knowledge graph, improving suggestion quality over time.',
    },
    {
        icon: TrendingUp,
        title: 'SLA Breach Prediction',
        desc: 'Proactive alerts when tickets are predicted to breach SLA targets, based on historical resolution patterns.',
    },
    {
        icon: Shield,
        title: 'AI Guardrails',
        desc: 'Output validation, confidence thresholds, and human-in-the-loop review for all AI-generated content.',
    },
]

const WORKFLOW_STEPS = [
    { step: '1', label: 'Ticket arrives via email, portal, or API' },
    { step: '2', label: 'AI classifies priority + category + sentiment' },
    { step: '3', label: 'Smart routing assigns to the right team' },
    { step: '4', label: 'Copilot drafts response from KB + history' },
    { step: '5', label: 'Agent reviews, edits, sends' },
    { step: '6', label: 'Resolution indexed for future RAG retrieval' },
]

export default function AIPage() {
    return (
        <LandingShell>
            {/* Hero */}
            <section className="py-24 lg:py-28 text-center relative overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-[radial-gradient(circle,rgba(217,181,90,0.06)_0%,transparent_70%)] pointer-events-none" />
                <div className="section-container relative z-10">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--atum-surface-2)] border border-[var(--atum-border)] text-xs font-medium text-[var(--atum-accent-gold)] mb-6">
                        <Cpu size={12} /> AI-Powered ITSM
                    </div>
                    <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-6 tracking-tight">
                        Your AI Copilot.<br />
                        <span className="text-[var(--atum-accent-gold)]">Your Data. Your Network.</span>
                    </h1>
                    <p className="text-lg text-[var(--atum-text-muted)] max-w-2xl mx-auto">
                        ATUM Nexus runs AI inference locally via Ollama. No data leaves your infrastructure.
                        Full copilot capabilities with complete privacy.
                    </p>
                </div>
            </section>

            {/* AI Features Grid */}
            <section className="pb-24">
                <div className="section-container">
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5 stagger">
                        {AI_FEATURES.map(f => (
                            <div key={f.title} className="glass-card glow-edge p-6 animate-in-up">
                                <div className="w-10 h-10 rounded-lg bg-[var(--atum-surface-2)] border border-[var(--atum-border)] flex items-center justify-center mb-4">
                                    <f.icon size={18} className="text-[var(--atum-accent-gold)]" />
                                </div>
                                <h3 className="text-sm font-semibold text-white mb-2">{f.title}</h3>
                                <p className="text-xs text-[var(--atum-text-muted)] leading-relaxed">{f.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* AI Workflow Pipeline */}
            <section className="py-20 bg-[var(--atum-bg-2)]/40">
                <div className="section-container">
                    <div className="text-center mb-12">
                        <h2 className="text-3xl font-bold text-white mb-3">
                            How <span className="text-[var(--atum-accent-gold)]">AI Copilot</span> Works
                        </h2>
                        <p className="text-[var(--atum-text-muted)]">End-to-end intelligent ticket lifecycle.</p>
                    </div>
                    <div className="max-w-2xl mx-auto">
                        <div className="space-y-4">
                            {WORKFLOW_STEPS.map((s, i) => (
                                <div key={i} className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-xl bg-[var(--atum-surface-2)] border border-[var(--atum-border)] flex items-center justify-center text-sm font-bold text-[var(--atum-accent-gold)] flex-shrink-0">
                                        {s.step}
                                    </div>
                                    <div className="flex-1 py-3 px-4 rounded-lg bg-[var(--atum-surface)] border border-[var(--atum-border)]">
                                        <span className="text-sm text-[var(--atum-text-1)]">{s.label}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            <FinalCTA />
        </LandingShell>
    )
}
