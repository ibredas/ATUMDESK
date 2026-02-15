import React, { useState } from 'react'
import LandingShell from '../../components/Landing/LandingShell'
import { Send, CheckCircle2, Building2, User, Mail, MessageSquare } from 'lucide-react'

export default function DemoPage() {
    const [submitted, setSubmitted] = useState(false)
    const [form, setForm] = useState({ name: '', email: '', company: '', message: '' })

    const handleSubmit = (e) => {
        e.preventDefault()
        // Local stub — no external APIs
        console.log('[Demo Form] Submitted:', form)
        setSubmitted(true)
    }

    const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

    return (
        <LandingShell>
            <section className="py-24 lg:py-32">
                <div className="section-container max-w-2xl">
                    {submitted ? (
                        <div className="text-center animate-in-up">
                            <div className="w-16 h-16 rounded-full bg-[var(--atum-surface-2)] border border-[var(--atum-border-gold)] flex items-center justify-center mx-auto mb-6">
                                <CheckCircle2 size={28} className="text-[var(--atum-success)]" />
                            </div>
                            <h2 className="text-3xl font-bold text-white mb-4">Thank you!</h2>
                            <p className="text-[var(--atum-text-muted)]">
                                We've received your request. Our team will contact you within 1 business day to schedule your demo.
                            </p>
                        </div>
                    ) : (
                        <>
                            <div className="text-center mb-12">
                                <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-4 tracking-tight">
                                    Book a <span className="text-[var(--atum-accent-gold)]">Demo</span>
                                </h1>
                                <p className="text-[var(--atum-text-muted)] max-w-lg mx-auto">
                                    See ATUM Nexus in action. Fill in your details and our team will schedule a personalized walkthrough.
                                </p>
                            </div>

                            <form onSubmit={handleSubmit} className="glass-card p-8 space-y-5">
                                <div>
                                    <label className="flex items-center gap-2 text-xs font-semibold text-[var(--atum-text-muted)] uppercase tracking-wider mb-2">
                                        <User size={12} /> Full Name
                                    </label>
                                    <input
                                        className="atum-input"
                                        type="text"
                                        placeholder="John Smith"
                                        value={form.name}
                                        onChange={update('name')}
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="flex items-center gap-2 text-xs font-semibold text-[var(--atum-text-muted)] uppercase tracking-wider mb-2">
                                        <Mail size={12} /> Work Email
                                    </label>
                                    <input
                                        className="atum-input"
                                        type="email"
                                        placeholder="john@company.com"
                                        value={form.email}
                                        onChange={update('email')}
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="flex items-center gap-2 text-xs font-semibold text-[var(--atum-text-muted)] uppercase tracking-wider mb-2">
                                        <Building2 size={12} /> Company
                                    </label>
                                    <input
                                        className="atum-input"
                                        type="text"
                                        placeholder="Acme Inc."
                                        value={form.company}
                                        onChange={update('company')}
                                    />
                                </div>
                                <div>
                                    <label className="flex items-center gap-2 text-xs font-semibold text-[var(--atum-text-muted)] uppercase tracking-wider mb-2">
                                        <MessageSquare size={12} /> What are you looking for?
                                    </label>
                                    <textarea
                                        className="atum-input min-h-[100px] resize-none"
                                        placeholder="Tell us about your team size, current tool, and what you're hoping ATUM Nexus can solve..."
                                        value={form.message}
                                        onChange={update('message')}
                                    />
                                </div>
                                <button type="submit" className="btn-gold w-full justify-center py-3">
                                    <Send size={16} /> Request Demo
                                </button>
                                <p className="text-center text-[10px] text-[var(--atum-text-dim)]">
                                    No spam. No external APIs. Your data stays on this server.
                                </p>
                            </form>
                        </>
                    )}
                </div>
            </section>
        </LandingShell>
    )
}
