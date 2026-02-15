import React from 'react'
import LandingShell from '../../components/Landing/LandingShell'
import SecurityComplianceBlock from '../../components/Landing/sections/SecurityComplianceBlock'
import FinalCTA from '../../components/Landing/sections/FinalCTA'
import { Shield, Lock, Fingerprint, Eye, FileSearch, Server, Database, Key } from 'lucide-react'

const DEEP_FEATURES = [
    {
        icon: Database,
        title: 'Row-Level Security (RLS)',
        details: [
            'Every PostgreSQL query enforced through org_id predicates',
            'No cross-tenant data leakage possible at the DB layer',
            'Verified through automated integration tests',
        ],
    },
    {
        icon: Lock,
        title: 'Tamper-Proof Audit Chain',
        details: [
            'Each audit log entry contains prev_hash of the previous entry',
            'SHA-256 hash chain prevents silent record modification',
            'Breakage detection on read — instant integrity alerts',
        ],
    },
    {
        icon: Key,
        title: 'TOTP Two-Factor Authentication',
        details: [
            'RFC 6238 compliant TOTP with QR provisioning',
            'Backup codes generated at enrollment',
            'Org-level enforcement via policy engine',
        ],
    },
    {
        icon: Eye,
        title: 'Rate Limiting & IP Restrictions',
        details: [
            'Per-endpoint rate limiting with configurable thresholds',
            'Admin-managed IP allow/deny lists per organization',
            'Brute-force protection on auth endpoints',
        ],
    },
    {
        icon: FileSearch,
        title: 'Attachment Security',
        details: [
            'File type validation (MIME + extension)',
            'Configurable size limits per organization',
            'Stored outside web root with signed access URLs',
        ],
    },
    {
        icon: Server,
        title: 'On-Prem Air-Gap Ready',
        details: [
            'No external API calls required for core functionality',
            'AI Copilot runs on local Ollama — zero data exfiltration',
            'Complete deployment within private networks',
        ],
    },
]

export default function SecurityPage() {
    return (
        <LandingShell>
            {/* Hero */}
            <section className="py-24 lg:py-28 text-center relative overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-[radial-gradient(circle,rgba(217,181,90,0.06)_0%,transparent_70%)] pointer-events-none" />
                <div className="section-container relative z-10">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--atum-surface-2)] border border-[var(--atum-border)] text-xs font-medium text-[var(--atum-accent-gold)] mb-6">
                        <Shield size={12} /> Security Architecture
                    </div>
                    <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-6 tracking-tight">
                        Security is Not a <span className="text-[var(--atum-accent-gold)]">Feature</span>.<br />
                        It's the Foundation.
                    </h1>
                    <p className="text-lg text-[var(--atum-text-muted)] max-w-2xl mx-auto">
                        ATUM Nexus is hardened from the database layer up — RLS, audit chains, 2FA, and on-prem isolation by default.
                    </p>
                </div>
            </section>

            {/* Deep Dive Feature Cards */}
            <section className="pb-24">
                <div className="section-container">
                    <div className="grid md:grid-cols-2 gap-6">
                        {DEEP_FEATURES.map(f => (
                            <div key={f.title} className="glass-card glow-edge p-6">
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="w-10 h-10 rounded-lg bg-[var(--atum-surface-2)] border border-[var(--atum-border)] flex items-center justify-center">
                                        <f.icon size={18} className="text-[var(--atum-accent-gold)]" />
                                    </div>
                                    <h3 className="text-sm font-semibold text-white">{f.title}</h3>
                                </div>
                                <ul className="space-y-2">
                                    {f.details.map((d, i) => (
                                        <li key={i} className="flex items-start gap-2 text-xs text-[var(--atum-text-muted)] leading-relaxed">
                                            <span className="w-1.5 h-1.5 rounded-full bg-[var(--atum-accent-gold)] mt-1.5 flex-shrink-0" />
                                            {d}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <SecurityComplianceBlock />
            <FinalCTA />
        </LandingShell>
    )
}
