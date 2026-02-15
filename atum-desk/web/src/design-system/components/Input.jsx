import React from 'react'

/*
 * ATUM DESK Design System - Input Component
 */

export function Input({ 
  label,
  error,
  className = '',
  ...props 
}) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--atum-text-muted)] mb-2">
          {label}
        </label>
      )}
      <input 
        className={`w-full px-4 py-2.5 bg-[var(--atum-bg-2)] border border-[var(--atum-border)] rounded-lg text-[var(--atum-text)] placeholder-[var(--atum-text-muted)] focus:outline-none focus:border-[var(--atum-accent-gold)] focus:ring-1 focus:ring-[var(--atum-accent-gold)] transition-all ${error ? 'border-red-500' : ''} ${className}`}
        {...props}
      />
      {error && (
        <p className="mt-1 text-xs text-red-400">{error}</p>
      )}
    </div>
  )
}

export function Select({ 
  label,
  options = [],
  error,
  className = '',
  ...props 
}) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--atum-text-muted)] mb-2">
          {label}
        </label>
      )}
      <select 
        className={`w-full px-4 py-2.5 bg-[var(--atum-bg-2)] border border-[var(--atum-border)] rounded-lg text-[var(--atum-text)] focus:outline-none focus:border-[var(--atum-accent-gold)] focus:ring-1 focus:ring-[var(--atum-accent-gold)] transition-all ${error ? 'border-red-500' : ''} ${className}`}
        {...props}
      >
        {options.map(opt => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
      {error && (
        <p className="mt-1 text-xs text-red-400">{error}</p>
      )}
    </div>
  )
}

export function Textarea({ 
  label,
  error,
  className = '',
  rows = 4,
  ...props 
}) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--atum-text-muted)] mb-2">
          {label}
        </label>
      )}
      <textarea 
        rows={rows}
        className={`w-full px-4 py-2.5 bg-[var(--atum-bg-2)] border border-[var(--atum-border)] rounded-lg text-[var(--atum-text)] placeholder-[var(--atum-text-muted)] focus:outline-none focus:border-[var(--atum-accent-gold)] focus:ring-1 focus:ring-[var(--atum-accent-gold)] transition-all resize-none ${error ? 'border-red-500' : ''} ${className}`}
        {...props}
      />
      {error && (
        <p className="mt-1 text-xs text-red-400">{error}</p>
      )}
    </div>
  )
}

export function Toggle({ 
  label,
  checked = false,
  onChange,
  className = '' 
}) {
  return (
    <label className={`flex items-center cursor-pointer ${className}`}>
      <div className="relative">
        <input 
          type="checkbox" 
          className="sr-only"
          checked={checked}
          onChange={onChange}
        />
        <div className={`w-11 h-6 rounded-full transition-colors ${checked ? 'bg-green-600' : 'bg-[var(--atum-bg-2)]'}`}>
          <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${checked ? 'translate-x-5' : 'translate-x-0'}`} />
        </div>
      </div>
      {label && <span className="ml-3 text-sm text-[var(--atum-text-1)]">{label}</span>}
    </label>
  )
}

export default Input
