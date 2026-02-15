import React from 'react'
import LandingShell from '../../components/Landing/LandingShell'
import FinalCTA from '../../components/Landing/sections/FinalCTA'
import { Check, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

const PLANS = [
    {
        name: 'Community',
        price: 'Free',
        period: 'forever',
        desc: 'For small teams getting started with modern ITSM.',
        features: [
            'Up to 3 agents',
            'Ticket management',
            'Knowledge base',
            'Email integration',
            'Community support',
        ],
        cta: 'Get Started',
        highlight: false,
    },
    {
        name: 'Enterprise',
        price: 'Contact Us',
        period: '',
        desc: 'Full platform with AI, automation, and enterprise security.',
        features: [
            'Unlimited agents',
            'AI Copilot (local LLM)',
            'Visual workflows & playbooks',
            'SLA engine with breach prediction',
            'Audit chain & RLS',
            'Multi-tenancy',
            'Asset management',
            'Priority support + SLA',
            'Custom integrations',
        ],
        cta: 'Contact Sales',
        highlight: true,
    },
    {
        name: 'Managed Cloud',
        price: 'Contact Us',
        period: '',
        desc: 'ATUM-hosted with full SLA and managed infrastructure.',
        features: [
            'Everything in Enterprise',
            'ATUM-managed hosting',
            '99.95% uptime SLA',
            'Automated backups',
            'SOC2 compliance',
            'Dedicated support engineer',
        ],
        cta: 'Contact Sales',
        highlight: false,
    },
]

export default function PricingPage() {
    return (
        <LandingShell>
            {/* Hero */}
            <section className="py-24 lg:py-28 text-center">
                <div className="section-container">
                    <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-6 tracking-tight">
                        Simple, <span className="text-[var(--atum-accent-gold)]">Transparent</span> Pricing
                    </h1>
                    <p className="text-lg text-[var(--atum-text-muted)] max-w-2xl mx-auto">
                        No per-agent escalation. No surprise invoices. Free for small teams, enterprise pricing for enterprise needs.
                    </p>
                </div>
            </section>

            {/* Pricing Cards */}
            <section className="pb-24">
                <div className="section-container">
                    <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                        {PLANS.map(plan => (
                            <div
                                key={plan.name}
                                className={`glass-card p-6 flex flex-col relative ${plan.highlight ? 'border-[var(--atum-border-gold)] ring-1 ring-[var(--atum-accent-glow)]' : ''
                                    }`}
                            >
                                {plan.highlight && (
                                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-[var(--atum-accent-gold)] text-black text-[10px] font-bold uppercase tracking-wider">
                                        Most Popular
                                    </div>
                                )}
                                <h3 className="text-lg font-bold text-white mb-1">{plan.name}</h3>
                                <div className="mb-2">
                                    <span className="text-2xl font-extrabold text-white">{plan.price}</span>
                                    {plan.period && <span className="text-sm text-[var(--atum-text-muted)] ml-1">/{plan.period}</span>}
                                </div>
                                <p className="text-xs text-[var(--atum-text-muted)] mb-6">{plan.desc}</p>
                                <ul className="space-y-2.5 mb-8 flex-1">
                                    {plan.features.map(f => (
                                        <li key={f} className="flex items-start gap-2 text-sm text-[var(--atum-text-1)]">
                                            <Check size={14} className="text-[var(--atum-success)] mt-0.5 flex-shrink-0" />
                                            {f}
                                        </li>
                                    ))}
                                </ul>
                                <Link
                                    to={plan.price === 'Free' ? '/desk/login' : '/demo'}
                                    className={plan.highlight ? 'btn-gold w-full justify-center' : 'btn-outline w-full justify-center'}
                                >
                                    {plan.cta} <ArrowRight size={14} />
                                </Link>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <FinalCTA />
        </LandingShell>
    )
}
