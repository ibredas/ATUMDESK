import React from 'react'
import { Link } from 'react-router-dom'

const FOOTER_LINKS = {
    Product: [
        { label: 'Overview', href: '/overview' },
        { label: 'Features', href: '/#features' },
        { label: 'Pricing', href: '/pricing' },
        { label: 'Security', href: '/security' },
        { label: 'AI Copilot', href: '/ai' },
    ],
    Company: [
        { label: 'About', href: '#' },
        { label: 'Careers', href: '#' },
        { label: 'Blog', href: '#' },
        { label: 'Contact', href: '/demo' },
    ],
    Resources: [
        { label: 'Documentation', href: '#' },
        { label: 'API Reference', href: '#' },
        { label: 'Status', href: '#' },
        { label: 'Changelog', href: '#' },
    ],
    Legal: [
        { label: 'Privacy', href: '#' },
        { label: 'Terms', href: '#' },
        { label: 'SLA', href: '#' },
        { label: 'DPA', href: '#' },
    ],
}

export default function Footer() {
    return (
        <footer className="border-t border-[var(--atum-border)] bg-[var(--atum-bg-2)]">
            <div className="section-container py-16">
                {/* Top Section */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-10 mb-12">
                    {/* Brand Column */}
                    <div className="col-span-2 md:col-span-1">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-8 h-8 rounded-lg bg-[var(--atum-accent-gold)] flex items-center justify-center">
                                <span className="text-black font-bold text-sm">A</span>
                            </div>
                            <span className="font-bold text-white tracking-tight">ATUM NEXUS</span>
                        </div>
                        <p className="text-sm text-[var(--atum-text-muted)] leading-relaxed">
                            Enterprise-grade service management. On-prem, secure, AI-powered.
                        </p>
                    </div>

                    {/* Link Columns */}
                    {Object.entries(FOOTER_LINKS).map(([title, links]) => (
                        <div key={title}>
                            <h4 className="text-xs font-semibold text-[var(--atum-text-dim)] uppercase tracking-widest mb-4">
                                {title}
                            </h4>
                            <ul className="space-y-2.5">
                                {links.map(link => (
                                    <li key={link.label}>
                                        <Link
                                            to={link.href}
                                            className="text-sm text-[var(--atum-text-muted)] hover:text-white transition-colors"
                                        >
                                            {link.label}
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                {/* Bottom Bar */}
                <div className="pt-8 border-t border-[var(--atum-border)] flex flex-col md:flex-row items-center justify-between gap-4">
                    <p className="text-xs text-[var(--atum-text-dim)]">
                        © {new Date().getFullYear()} ATUM Technologies. All rights reserved.
                    </p>
                    <div className="flex items-center gap-6">
                        <span className="text-xs text-[var(--atum-text-dim)]">SOC2 Compliant</span>
                        <span className="text-xs text-[var(--atum-text-dim)]">ISO 27001</span>
                        <span className="text-xs text-[var(--atum-text-dim)]">GDPR Ready</span>
                    </div>
                </div>
            </div>
        </footer>
    )
}
