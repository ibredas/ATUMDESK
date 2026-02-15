import React from 'react'
import LandingShell from '../components/Landing/LandingShell'
import HeroSplitCTA from '../components/Landing/sections/HeroSplitCTA'
import TrustStrip from '../components/Landing/sections/TrustStrip'
import OutcomeCaseStudies from '../components/Landing/sections/OutcomeCaseStudies'
import ReasonsNumbered from '../components/Landing/sections/ReasonsNumbered'
import FeatureComparisonGrid from '../components/Landing/sections/FeatureComparisonGrid'
import WorkflowShowcase from '../components/Landing/sections/WorkflowShowcase'
import SecurityComplianceBlock from '../components/Landing/sections/SecurityComplianceBlock'
import FAQAccordion from '../components/Landing/sections/FAQAccordion'
import FinalCTA from '../components/Landing/sections/FinalCTA'
import CustomerQuotes from '../components/Landing/sections/CustomerQuotes'

export default function LandingPage() {
    return (
        <LandingShell>
            <HeroSplitCTA />
            <TrustStrip />
            <FeatureComparisonGrid />
            <WorkflowShowcase />
            <OutcomeCaseStudies />
            <CustomerQuotes />
            <ReasonsNumbered />
            <SecurityComplianceBlock />
            <FAQAccordion />
            <FinalCTA />
        </LandingShell>
    )
}
