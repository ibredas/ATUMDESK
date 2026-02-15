import React from 'react'

/*
 * ATUM DESK Design System - Button Component
 */

const baseStyles = "inline-flex items-center justify-center font-semibold tracking-wide text-xs uppercase transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[var(--atum-bg)] disabled:opacity-50 disabled:cursor-not-allowed"

const variants = {
  primary: "bg-[var(--atum-accent-gold)] text-black hover:brightness-110 focus:ring-[var(--atum-accent-gold)] shadow-lg hover:shadow-[0_0_20px_rgba(212,175,55,0.3)]",
  secondary: "bg-[var(--atum-bg-2)] text-[var(--atum-text)] border border-[var(--atum-border)] hover:border-[var(--atum-accent-gold)] hover:text-[var(--atum-accent-gold)]",
  ghost: "text-[var(--atum-text-1)] hover:text-[var(--atum-accent-gold)] hover:bg-[var(--atum-glass)]",
  danger: "bg-red-600 text-white hover:bg-red-500 focus:ring-red-500",
}

const sizes = {
  sm: "px-3 py-1.5 rounded text-[10px]",
  md: "px-4 py-2 rounded-md",
  lg: "px-6 py-3 rounded-lg text-sm",
}

export function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  className = '',
  disabled,
  ...props 
}) {
  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
}

export default Button
