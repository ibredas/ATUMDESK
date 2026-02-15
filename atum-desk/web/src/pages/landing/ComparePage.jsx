import React from 'react'
import LandingShell from '../../components/Landing/LandingShell'
import FeatureComparisonGrid from '../../components/Landing/sections/FeatureComparisonGrid'
import OutcomeCaseStudies from '../../components/Landing/sections/OutcomeCaseStudies'
import ReasonsNumbered from '../../components/Landing/sections/ReasonsNumbered'
import FinalCTA from '../../components/Landing/sections/FinalCTA'

export default function ComparePage() {
    return (
        <LandingShell>
            {/* Hero */}
            <section className="py-24 lg:py-28 text-center">
                <div className="section-container">
                    <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-6 tracking-tight">
                        ATUM Nexus vs <span className="text-[var(--atum-text-muted)]">Legacy ITSM</span>
                    </h1>
                    <p className="text-lg text-[var(--atum-text-muted)] max-w-2xl mx-auto">
                        See why teams are migrating from traditional ITSM platforms to a modern, on-prem, AI-powered alternative.
                    </p>
                </div>
            </section>

            <FeatureComparisonGrid />

            {/* Customer Quote */}
            <section className="py-16">
                <div className="section-container max-w-3xl text-center">
                    <blockquote className="glass-card p-8">
                        <p className="text-lg text-[var(--atum-text-1)] italic leading-relaxed mb-4">
                            "We evaluated ServiceNow, Jira SM, and Freshservice. ATUM Nexus gave us enterprise features with full data sovereignty. The migration took 2 days."
                        </p>
                        <div className="text-sm text-[var(--atum-text-muted)]">
                            — IT Director, Enterprise Financial Group
                        </div>
                    </blockquote>
                </div>
            </section>

            <OutcomeCaseStudies />
            <ReasonsNumbered />
            <FinalCTA />
        </LandingShell>
    )
}
