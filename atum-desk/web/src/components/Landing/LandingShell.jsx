import React from 'react'
import TopNav from './TopNav'
import Footer from './Footer'

export default function LandingShell({ children }) {
    return (
        <div className="min-h-screen bg-[var(--atum-bg)] text-[var(--atum-text)] font-sans antialiased">
            <TopNav />
            <main className="pt-[var(--nav-height)]">
                {children}
            </main>
            <Footer />
        </div>
    )
}
