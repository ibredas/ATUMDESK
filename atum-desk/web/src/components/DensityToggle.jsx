import React from 'react'
import { AlignJustify, AlignLeft } from 'lucide-react'

/**
 * DensityToggle — compact/default density toggle for tables.
 * 
 * Usage:
 *   <DensityToggle value={density} onChange={setDensity} />
 * 
 * Then apply density to tables:
 *   <table className={`glass-table ${density === 'compact' ? 'density-compact' : ''}`}>
 */
export default function DensityToggle({ value = 'default', onChange, className = '' }) {
    return (
        <div className={`inline-flex bg-[var(--atum-surface-2)] rounded-lg border border-[var(--atum-border)] p-0.5 ${className}`}>
            <button
                onClick={() => onChange?.('default')}
                className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-all flex items-center gap-1.5 ${value === 'default'
                        ? 'bg-[var(--atum-accent-gold)] text-black shadow-sm'
                        : 'text-[var(--atum-text-muted)] hover:text-white'
                    }`}
                title="Default density"
            >
                <AlignJustify size={12} /> Default
            </button>
            <button
                onClick={() => onChange?.('compact')}
                className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-all flex items-center gap-1.5 ${value === 'compact'
                        ? 'bg-[var(--atum-accent-gold)] text-black shadow-sm'
                        : 'text-[var(--atum-text-muted)] hover:text-white'
                    }`}
                title="Compact density"
            >
                <AlignLeft size={12} /> Compact
            </button>
        </div>
    )
}
