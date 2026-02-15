import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Download } from 'lucide-react'

export default function FinalCTA() {
    return (
        <section className="py-24 relative overflow-hidden">
            {/* Background gradient */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(217,181,90,0.06)_0%,transparent_70%)] pointer-events-none" />

            <div className="section-container relative z-10 text-center">
                <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                    Ready to upgrade your service desk?
                </h2>
                <p className="text-[var(--atum-text-muted)] max-w-xl mx-auto mb-10">
                    Deploy ATUM Nexus on your infrastructure in under an hour.
                    Full enterprise features, zero vendor lock-in.
                </p>
                <div className="flex flex-wrap justify-center gap-4">
                    <Link to="/demo" className="btn-gold text-base py-3 px-8">
                        Book Demo <ArrowRight size={16} />
                    </Link>
                    <a href="#" className="btn-outline text-base py-3 px-8">
                        <Download size={16} /> Download On-Prem
                    </a>
                </div>
                <p className="text-xs text-[var(--atum-text-dim)] mt-6">
                    No credit card required · Free for small teams · Enterprise support available
                </p>
            </div>
        </section>
    )
}
