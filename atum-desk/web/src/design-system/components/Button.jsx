import React from 'react'

/*
 * ATUM DESK Design System - Button Component
 */

const baseStyles = "inline-flex items-center justify-center font-semibold tracking-wide text-xs uppercase transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[var(--bg-0)] disabled:opacity-50 disabled:cursor-not-allowed"

const variants = {
  primary: "bg-[var(--accent-gold)] text-black hover:brightness-110 focus:ring-[var(--accent-gold)] shadow-lg hover:shadow-[0_0_20px_rgba(212,175,55,0.3)]",
  secondary: "bg-[var(--bg-2)] text-[var(--text-0)] border border-[var(--border)] hover:border-[var(--accent-gold)] hover:text-[var(--accent-gold)]",
  ghost: "text-[var(--text-1)] hover:text-[var(--accent-gold)] hover:bg-[var(--glass)]",
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
