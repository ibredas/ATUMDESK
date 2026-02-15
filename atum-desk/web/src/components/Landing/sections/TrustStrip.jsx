import React, { useState, useEffect, useRef } from 'react'
import { Ticket, Clock, Shield, Zap, Users, Globe } from 'lucide-react'

const METRICS = [
    { icon: Ticket, value: 50000, suffix: '+', label: 'Tickets Resolved', format: true },
    { icon: Clock, value: 99.9, suffix: '%', label: 'Uptime SLA', format: false },
    { icon: Shield, value: 0, suffix: ' Breaches', label: 'Security Record', format: false },
    { icon: Zap, value: 2.1, suffix: 's', label: 'Avg Response', format: false },
]

const TRUST = [
    { icon: Users, label: 'SOC2 Type II' },
    { icon: Globe, label: 'ISO 27001' },
    { icon: Shield, label: 'GDPR Ready' },
    { icon: Zap, label: 'On-Prem / Cloud' },
]

function AnimatedNumber({ value, suffix, format }) {
    const [display, setDisplay] = useState(0)
    const ref = useRef(null)
    const started = useRef(false)

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting && !started.current) {
                    started.current = true
                    const duration = 1500
                    const steps = 40
                    const increment = value / steps
                    let current = 0
                    let step = 0
                    const timer = setInterval(() => {
                        step++
                        current = Math.min(value, increment * step)
                        setDisplay(current)
                        if (step >= steps) clearInterval(timer)
                    }, duration / steps)
                }
            },
            { threshold: 0.3 }
        )
        if (ref.current) observer.observe(ref.current)
        return () => observer.disconnect()
    }, [value])

    const formatted = format
        ? Math.round(display).toLocaleString()
        : Number.isInteger(value)
            ? Math.round(display)
            : display.toFixed(1)

    return (
        <span ref={ref} className="text-2xl md:text-3xl font-bold text-white tabular-nums">
            {formatted}{suffix}
        </span>
    )
}

export default function TrustStrip() {
    return (
        <section className="py-16 border-y border-[var(--atum-border)] bg-[var(--atum-bg-2)]/50">
            <div className="section-container">
                {/* Metrics Row */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-10">
                    {METRICS.map(m => (
                        <div key={m.label} className="text-center">
                            <m.icon size={18} className="mx-auto mb-2 text-[var(--atum-accent-gold)]" />
                            <AnimatedNumber value={m.value} suffix={m.suffix} format={m.format} />
                            <div className="text-xs text-[var(--atum-text-muted)] mt-1">{m.label}</div>
                        </div>
                    ))}
                </div>

                {/* Trust Badges */}
                <div className="flex flex-wrap justify-center gap-6">
                    {TRUST.map(t => (
                        <div
                            key={t.label}
                            className="flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--atum-surface)] border border-[var(--atum-border)] text-xs font-medium text-[var(--atum-text-muted)]"
                        >
                            <t.icon size={14} className="text-[var(--atum-accent-gold)]" />
                            {t.label}
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}
