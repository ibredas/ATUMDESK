import React from 'react'

export function PageShell({ title, subtitle, actions, children }) {
    return (
        <div className="animate-in pb-12">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-white tracking-tight">{title}</h1>
                    {subtitle && <p className="text-[var(--atum-text-muted)] mt-1">{subtitle}</p>}
                </div>
                {actions && (
                    <div className="flex items-center gap-3">
                        {actions}
                    </div>
                )}
            </div>
            {children}
        </div>
    )
}

export function GlassCard({ children, className = '', title, actions }) {
    return (
        <div className={`glass-card p-6 ${className}`}>
            {(title || actions) && (
                <div className="flex items-center justify-between mb-5">
                    {title && <h3 className="text-sm font-semibold text-white uppercase tracking-wider">{title}</h3>}
                    {actions && <div className="flex gap-2">{actions}</div>}
                </div>
            )}
            {children}
        </div>
    )
}
