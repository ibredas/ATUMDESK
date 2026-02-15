import React from 'react'

/**
 * ActivityTimeline — vertical timeline for incidents, postmortems, audit events.
 * 
 * Usage:
 *   <ActivityTimeline items={[{ time: '10:32', title: 'Incident declared', description: 'SEV-2 outage', icon: Siren, color: '#ef4444' }]} />
 */
export default function ActivityTimeline({ items = [], className = '' }) {
    if (items.length === 0) {
        return (
            <div className={`text-center py-8 text-[var(--atum-text-muted)] ${className}`}>
                No activity to display
            </div>
        )
    }

    return (
        <div className={`relative ${className}`}>
            {/* Vertical line */}
            <div className="absolute left-4 top-0 bottom-0 w-px bg-[var(--atum-border)]" />

            <div className="space-y-6">
                {items.map((item, idx) => {
                    const Icon = item.icon
                    return (
                        <div key={idx} className="relative flex gap-4 pl-10">
                            {/* Dot / Icon */}
                            <div
                                className="absolute left-0 w-8 h-8 rounded-full flex items-center justify-center border-2 bg-[var(--atum-bg)]"
                                style={{ borderColor: item.color || 'var(--atum-accent-gold)' }}
                            >
                                {Icon ? (
                                    <Icon size={14} style={{ color: item.color || 'var(--atum-accent-gold)' }} />
                                ) : (
                                    <div className="w-2.5 h-2.5 rounded-full" style={{ background: item.color || 'var(--atum-accent-gold)' }} />
                                )}
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-0.5">
                                    <span className="font-medium text-sm">{item.title}</span>
                                    {item.badge && (
                                        <span className="badge text-xs" style={{ background: (item.color || '#d4af37') + '20', color: item.color || '#d4af37' }}>
                                            {item.badge}
                                        </span>
                                    )}
                                </div>
                                {item.description && (
                                    <p className="text-sm text-[var(--atum-text-muted)]">{item.description}</p>
                                )}
                                <span className="text-xs text-[var(--atum-text-muted)] mt-1 block">{item.time}</span>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
