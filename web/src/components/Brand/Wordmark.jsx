import React from 'react'

export function Wordmark({ className = "h-6", color = "currentColor", suffix = "" }) {
    return (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <svg viewBox="0 0 140 32" fill="none" xmlns="http://www.w3.org/2000/svg" className={className} aria-label="ATUM">
                <g fill={color}>
                    {/* Λ (The Glyph) */}
                    <path d="M4 28L14 4H18L8 28H4Z" />
                    <path d="M26 28L16 4H20L30 28H26Z" />
                    <circle cx="17" cy="12" r="2.5" style={{ color: 'var(--accent-gold, #d4af37)' }} fill="currentColor" fillOpacity="0.9" />
                    {/* T */}
                    <path d="M42 4H62V8H54V28H50V8H42V4Z" />
                    {/* U */}
                    <path d="M70 4V22C70 26 72 28 76 28H84C88 28 90 26 90 22V4H86V22C86 24 85.5 24.5 84 24.5H76C74.5 24.5 74 24 74 22V4H70Z" />
                    {/* M */}
                    <path d="M98 28V4H102.5L110 18L117.5 4H122V28H118V10L111.5 22H108.5L102 10V28H98Z" />
                </g>
            </svg>
            {suffix && (
                <span style={{
                    fontSize: '11px',
                    fontWeight: 800,
                    letterSpacing: '0.15em',
                    textTransform: 'uppercase',
                    color: 'var(--text-2, #71717a)',
                    borderLeft: '1px solid var(--glass-border, rgba(212,175,55,0.15))',
                    paddingLeft: '8px',
                    lineHeight: 1,
                }}>
                    {suffix}
                </span>
            )}
        </span>
    )
}
