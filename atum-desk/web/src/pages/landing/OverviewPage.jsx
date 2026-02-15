import React from 'react'
import LandingShell from '../../components/Landing/LandingShell'
import HeroSplitCTA from '../../components/Landing/sections/HeroSplitCTA'
import TrustStrip from '../../components/Landing/sections/TrustStrip'
import FeatureComparisonGrid from '../../components/Landing/sections/FeatureComparisonGrid'
import WorkflowShowcase from '../../components/Landing/sections/WorkflowShowcase'
import SecurityComplianceBlock from '../../components/Landing/sections/SecurityComplianceBlock'
import FinalCTA from '../../components/Landing/sections/FinalCTA'
import { Link } from 'react-router-dom'
import {
    Inbox, BarChart3, BookOpen, GitPullRequest, Boxes,
    Activity, FileText, Cpu, Shield, Workflow, AlertTriangle, Users
} from 'lucide-react'

const MODULES = [
    { icon: Inbox, title: 'Ticket Management', desc: 'Multi-channel inbox with SLA tracking, smart triage, and AI-powered auto-classification.' },
    { icon: BarChart3, title: 'Analytics Dashboard', desc: 'Real-time metrics, SLA compliance tracking, agent performance, and trend analysis.' },
    { icon: BookOpen, title: 'Knowledge Base', desc: 'GraphRAG-powered KB with auto-suggestions, version history, and public/internal visibility.' },
    { icon: GitPullRequest, title: 'Change Management', desc: 'ITIL-aligned change requests with approval workflows and risk assessment.' },
    { icon: Boxes, title: 'Asset Management', desc: 'CMDB-lite with asset tracking, relationships, and lifecycle management.' },
    { icon: Activity, title: 'SLA Engine', desc: 'Policy-driven SLA with pause/resume, business hours, and predictive breach alerts.' },
    { icon: FileText, title: 'Playbooks', desc: 'Step-by-step runbooks for incident response with audit trail integration.' },
    { icon: Cpu, title: 'AI Copilot', desc: 'Local LLM-powered triage, smart replies, sentiment analysis, and KB suggestions.' },
    { icon: Shield, title: 'Security Center', desc: 'RLS, 2FA, IP restrictions, audit chain, and attachment scanning — all built in.' },
    { icon: Workflow, title: 'Visual Workflows', desc: 'Drag-drop automation builder for ticket routing, escalation, and notifications.' },
    { icon: AlertTriangle, title: 'Incident Management', desc: 'Incident tracking with postmortem templates, timeline, and root cause analysis.' },
    { icon: Users, title: 'Multi-Tenancy', desc: 'Row-level isolated organizations with per-tenant policies and configurations.' },
]

export default function OverviewPage() {
    return (
        <LandingShell>
            {/* Hero */}
            <section className="py-24 lg:py-32 relative overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-[radial-gradient(circle,rgba(217,181,90,0.07)_0%,transparent_70%)] pointer-events-none" />
                <div className="section-container relative z-10 text-center">
                    <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-6 tracking-tight">
                        The Complete <span className="text-[var(--atum-accent-gold)]">Platform Tour</span>
                    </h1>
                    <p className="text-lg text-[var(--atum-text-muted)] max-w-2xl mx-auto mb-4">
                        Everything you need to run enterprise service operations — from a single, on-prem deployment.
                    </p>
                </div>
            </section>

            {/* Modules Grid */}
            <section className="pb-24">
                <div className="section-container">
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5 stagger">
                        {MODULES.map(m => (
                            <div key={m.title} className="glass-card glow-edge p-6 animate-in-up">
                                <div className="w-10 h-10 rounded-lg bg-[var(--atum-surface-2)] border border-[var(--atum-border)] flex items-center justify-center mb-4">
                                    <m.icon size={18} className="text-[var(--atum-accent-gold)]" />
                                </div>
                                <h3 className="text-sm font-semibold text-white mb-2">{m.title}</h3>
                                <p className="text-xs text-[var(--atum-text-muted)] leading-relaxed">{m.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <WorkflowShowcase />
            <SecurityComplianceBlock />
            <FinalCTA />
        </LandingShell>
    )
}
