/*
 * ATUM DESK Design System - Brand Tokens
 * Single source of truth for all styling
 */

export const tokens = {
  // Colors
  colors: {
    // Backgrounds
    bg0: '#050505',
    bg1: '#0a0a0a', 
    bg2: '#121212',
    card: 'rgba(18, 18, 18, 0.8)',
    
    // Text
    text0: '#ffffff',
    text1: '#a1a1aa',
    text2: '#71717a',
    textMuted: '#71717a',
    
    // Accent (Gold)
    accentGold: '#d4af37',
    accentGoldHover: '#e5c14b',
    accentGoldMuted: 'rgba(212, 175, 55, 0.15)',
    
    // Status Colors
    statusNew: '#3b82f6',
    statusOpen: '#f59e0b',
    statusProgress: '#8b5cf6',
    statusResolved: '#10b981',
    statusClosed: '#6b7280',
    
    // Priority
    priorityLow: '#6b7280',
    priorityMedium: '#3b82f6',
    priorityHigh: '#f59e0b',
    priorityUrgent: '#ef4444',
    
    // Borders
    border: 'rgba(255, 255, 255, 0.08)',
    borderHover: 'rgba(212, 175, 55, 0.3)',
    
    // Glass
    glass: 'rgba(10, 10, 12, 0.7)',
    glassBorder: 'rgba(212, 175, 55, 0.15)',
    glassHighlight: 'rgba(255, 255, 255, 0.03)',
  },
  
  // Gradients
  gradients: {
    goldGlow: 'radial-gradient(circle, rgba(212,175,55,0.12) 0%, transparent 70%)',
    purpleGlow: 'radial-gradient(circle, rgba(124,58,237,0.08) 0%, transparent 40%)',
    hero: 'linear-gradient(180deg, rgba(212,175,55,0.05) 0%, transparent 60%)',
  },
  
  // Typography
  typography: {
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
    fontFamilyDisplay: "'Cinzel', serif",
    
    // Sizes
    textXs: '0.75rem',    // 12px
    textSm: '0.875rem',   // 14px
    textBase: '1rem',     // 16px
    textLg: '1.125rem',   // 18px
    textXl: '1.25rem',    // 20px
    text2xl: '1.5rem',    // 24px
    text3xl: '1.875rem',  // 30px
    text4xl: '2.25rem',   // 36px
    text5xl: '3rem',      // 48px
    
    // Weights
    fontNormal: 400,
    fontMedium: 500,
    fontSemibold: 600,
    fontBold: 700,
    fontBlack: 900,
    
    // Tracking
    trackingTight: '-0.025em',
    trackingNormal: '0',
    trackingWide: '0.025em',
    trackingWidest: '0.1em',
  },
  
  // Spacing
  spacing: {
    px: '1px',
    0: '0',
    1: '0.25rem',  
    2 // 4px: '0.5rem',    // 8px
    3: '0.75rem',   // 12px
    4: '1rem',      // 16px
    5: '1.25rem',   // 20px
    6: '1.5rem',    // 24px
    8: '2rem',      // 32px
    10: '2.5rem',   // 40px
    12: '3rem',     // 48px
    16: '4rem',     // 64px
  },
  
  // Border Radius
  radius: {
    none: '0',
    sm: '0.25rem',   // 4px
    DEFAULT: '0.375rem', // 6px
    md: '0.5rem',    // 8px
    lg: '0.75rem',   // 12px
    xl: '1rem',      // 16px
    '2xl': '1.5rem', // 24px
    full: '9999px',
  },
  
  // Shadows
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    DEFAULT: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    glow: '0 0 30px rgba(212, 175, 55, 0.3)',
    glowSm: '0 0 15px rgba(212, 175, 55, 0.2)',
  },
  
  // Transitions
  transitions: {
    fast: '150ms',
    DEFAULT: '200ms',
    slow: '300ms',
  },
  
  // Z-Index
  zIndex: {
    0: 0,
    10: 10,
    20: 20,
    30: 30,
    40: 40,
    50: 50,
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modalBackdrop: 1040,
    modal: 1050,
    popover: 1060,
    tooltip: 1070,
  },
}

// CSS Variables (for use in style attribute)
export const cssVars = Object.entries(tokens).reduce((acc, [category, values]) => {
  if (typeof values === 'object' && values !== null) {
    Object.entries(values).forEach(([key, value]) => {
      acc[`--${category}-${key}`] = value
    })
  }
  return acc
}, {})

export default tokens
