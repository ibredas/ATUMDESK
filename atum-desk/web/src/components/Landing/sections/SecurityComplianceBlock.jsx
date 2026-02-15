import React from 'react'
import { Shield, Lock, FileSearch, Fingerprint, Eye, Server } from 'lucide-react'

const FEATURES = [
    { icon: Shield, title: 'Row-Level Security', desc: 'Every database query enforces tenant isolation at the PostgreSQL level.' },
    { icon: Lock, title: 'Tamper-Proof Audit Chain', desc: 'Hash-chained audit log entries with prev_hash verification — immutable record.' },
    { icon: Fingerprint, title: 'TOTP Two-Factor Auth', desc: 'RFC 6238 compliant TOTP with backup codes. Org-level enforcement available.' },
    { icon: FileSearch, title: 'Attachment Scanning', desc: 'File type validation, size limits, and malware signature check on upload.' },
    { icon: Eye, title: 'Rate Limiting & IP Restrictions', desc: 'Per-endpoint rate limiting and admin-configurable IP allow/deny lists.' },
    { icon: Server, title: 'On-Prem Isolation', desc: 'Full deployment on your network. No external API calls. Air-gapped capable.' },
]

export default function SecurityComplianceBlock() {
    return (
        <section className="py-24">
            <div className="section-container">
                <div className="text-center mb-14">
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                        Security-First <span className="text-[var(--atum-accent-gold)]">Architecture</span>
                    </h2>
                    <p className="text-[var(--atum-text-muted)] max-w-2xl mx-auto">
                        Built from the ground up for environments where security is non-negotiable.
                    </p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5 stagger">
                    {FEATURES.map(f => (
                        <div key={f.title} className="glass-card glow-edge p-5 animate-in-up">
                            <div className="w-10 h-10 rounded-lg bg-[var(--atum-surface-2)] border border-[var(--atum-border)] flex items-center justify-center mb-4">
                                <f.icon size={18} className="text-[var(--atum-accent-gold)]" />
                            </div>
                            <h3 className="text-sm font-semibold text-white mb-1.5">{f.title}</h3>
                            <p className="text-xs text-[var(--atum-text-muted)] leading-relaxed">{f.body || f.desc}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}
