import React, { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X } from 'lucide-react'
import { Wordmark } from '../Brand/Wordmark'

const NAV_LINKS = [
    { label: 'Overview', href: '/overview' },
    { label: 'Features', href: '/#features' },
    { label: 'Workflows', href: '/#workflows' },
    { label: 'Security', href: '/security' },
    { label: 'AI', href: '/ai' },
    { label: 'Pricing', href: '/pricing' },
]

export default function TopNav() {
    const [scrolled, setScrolled] = useState(false)
    const [mobileOpen, setMobileOpen] = useState(false)
    const location = useLocation()

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 20)
        window.addEventListener('scroll', onScroll, { passive: true })
        return () => window.removeEventListener('scroll', onScroll)
    }, [])

    return (
        <nav
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled
                ? 'bg-[var(--atum-bg)]/95 backdrop-blur-lg border-b border-[var(--atum-border)]'
                : 'bg-transparent'
                }`}
            style={{ height: 'var(--nav-height)' }}
        >
            <div className="section-container h-full flex items-center justify-between">
                {/* Brand */}
                <Link to="/" className="flex items-center gap-3 group">
                    <Wordmark className="h-8 text-[var(--atum-accent-gold)]" suffix="NEXUS" />
                    <span className="hidden sm:block text-[9px] text-[var(--atum-accent-gold)] tracking-[0.25em] font-semibold -mt-0.5">
                        ENTERPRISE PLATFORM
                    </span>
                </Link>

                {/* Desktop Links */}
                <div className="hidden md:flex items-center gap-1">
                    {NAV_LINKS.map(link => {
                        const isActive = location.pathname === link.href
                        return (
                            <Link
                                key={link.href}
                                to={link.href}
                                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive
                                    ? 'text-[var(--atum-accent-gold)]'
                                    : 'text-[var(--atum-text-muted)] hover:text-white'
                                    }`}
                            >
                                {link.label}
                            </Link>
                        )
                    })}
                </div>

                {/* CTA Buttons */}
                <div className="hidden md:flex items-center gap-3">
                    <Link to="/demo" className="btn-outline text-sm py-2 px-4">Book Demo</Link>
                    <Link to="/desk/login" className="btn-gold text-sm py-2 px-4">Sign In</Link>
                </div>

                {/* Mobile Toggle */}
                <button
                    className="md:hidden text-[var(--atum-text-muted)] hover:text-white p-2"
                    onClick={() => setMobileOpen(!mobileOpen)}
                >
                    {mobileOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            {/* Mobile Menu */}
            {mobileOpen && (
                <div className="md:hidden absolute top-full left-0 right-0 bg-[var(--atum-bg-2)] border-b border-[var(--atum-border)] p-4 space-y-1 animate-in">
                    {NAV_LINKS.map(link => (
                        <Link
                            key={link.href}
                            to={link.href}
                            onClick={() => setMobileOpen(false)}
                            className="block px-4 py-3 rounded-lg text-sm text-[var(--atum-text-muted)] hover:text-white hover:bg-[var(--atum-surface)] transition-colors"
                        >
                            {link.label}
                        </Link>
                    ))}
                    <div className="pt-3 space-y-2 border-t border-[var(--atum-border)] mt-2">
                        <Link to="/demo" className="btn-outline w-full justify-center text-sm">Book Demo</Link>
                        <Link to="/desk/login" className="btn-gold w-full justify-center text-sm">Sign In</Link>
                    </div>
                </div>
            )}
        </nav>
    )
}
