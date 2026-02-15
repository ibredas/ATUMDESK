import React from 'react'

/*
 * ATUM DESK Design System - Badge Component
 */

export function Badge({ 
  children, 
  variant = 'default',
  size = 'md',
  className = '' 
}) {
  const variants = {
    default: 'bg-[var(--atum-bg-2)] text-[var(--atum-text-1)] border border-[var(--atum-border)]',
    // Status
    new: 'bg-blue-900/40 text-blue-400 border border-blue-700',
    open: 'bg-amber-900/40 text-amber-400 border border-amber-700',
    in_progress: 'bg-purple-900/40 text-purple-400 border border-purple-700',
    resolved: 'bg-emerald-900/40 text-emerald-400 border border-emerald-700',
    closed: 'bg-gray-800/40 text-gray-400 border border-gray-700',
    accepted: 'bg-cyan-900/40 text-cyan-400 border border-cyan-700',
    waiting_customer: 'bg-orange-900/40 text-orange-400 border border-orange-700',
    // Priority
    low: 'bg-gray-800/40 text-gray-400 border border-gray-700',
    medium: 'bg-blue-900/40 text-blue-400 border border-blue-700',
    high: 'bg-amber-900/40 text-amber-400 border border-amber-700',
    urgent: 'bg-red-900/40 text-red-400 border border-red-700',
    // Semantic
    success: 'bg-green-900/40 text-green-400 border border-green-700',
    warning: 'bg-amber-900/40 text-amber-400 border border-amber-700',
    error: 'bg-red-900/40 text-red-400 border border-red-700',
    info: 'bg-blue-900/40 text-blue-400 border border-blue-700',
    gold: 'bg-[var(--accent-gold-muted)] text-[var(--atum-accent-gold)] border border-[var(--atum-accent-gold)]/30',
  }
  
  const sizes = {
    sm: 'px-1.5 py-0.5 text-[10px]',
    md: 'px-2 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm',
  }
  
  return (
    <span 
      className={`inline-flex items-center rounded-full font-medium uppercase tracking-wide ${variants[variant]} ${sizes[size]} ${className}`}
    >
      {children}
    </span>
  )
}

export default Badge
