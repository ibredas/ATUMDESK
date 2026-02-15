import React from 'react'

/*
 * ATUM DESK Design System - Card Component
 */

export function Card({ 
  children, 
  className = '',
  variant = 'default',
  padding = 'md',
  ...props 
}) {
  const variants = {
    default: 'bg-[var(--atum-surface)] border border-[var(--atum-border)] rounded-xl',
    glass: 'glass-panel rounded-xl',
    elevated: 'bg-[var(--bg-1)] border border-[var(--atum-border)] rounded-xl shadow-xl',
  }
  
  const paddings = {
    none: '',
    sm: 'p-3',
    md: 'p-5',
    lg: 'p-6',
    xl: 'p-8',
  }
  
  return (
    <div 
      className={`${variants[variant]} ${paddings[padding]} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({ children, className = '' }) {
  return (
    <div className={`mb-4 pb-3 border-b border-[var(--atum-border)] ${className}`}>
      {children}
    </div>
  )
}

export function CardTitle({ children, className = '' }) {
  return (
    <h3 className={`text-sm font-bold uppercase tracking-widest text-[var(--atum-text-muted)] ${className}`}>
      {children}
    </h3>
  )
}

export function CardContent({ children, className = '' }) {
  return <div className={className}>{children}</div>
}

export default Card
