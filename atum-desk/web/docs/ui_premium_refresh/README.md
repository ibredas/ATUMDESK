# ATUM DESK - Premium UI Design System
**Version:** 2.0.0 (Dark Glass Enterprise)

## Overview
This UI overhaul transitions ATUM DESK to a "Dark Glass" aesthetic inspired by modern enterprise tools (Linear, ServiceNow).
It uses a Token-based CSS system for consistency and a new Component Library for rapid development.

## 1. Design Tokens
All colors and spacing are defined in `index.css` via CSS variables.

### Key Colors
| Token | Value | Usage |
| :--- | :--- | :--- |
| `--atum-bg` | `#070A10` | Main application background (Deep Navy) |
| `--atum-surface` | `rgba(255,255,255,0.04)` | Card background, input background |
| `--atum-accent-gold` | `#D9B55A` | Primary Actions, Brand Color, Focus States |
| `--atum-border` | `rgba(255,255,255,0.10)` | Subtle borders for separation |

### Glassmorphism
Use the `.glass-card` or `.glass-panel` classes to apply the standard blur/border/shadow combination.
```css
.glass-card {
  background: var(--atum-surface-2);
  backdrop-filter: blur(10px);
  border: 1px solid var(--atum-border);
}
```

## 2. Components
Located in `src/components/Premium` and `src/components/Layout`.

### `DeskLayout`
The main shell for the staff interface.
- **Collapsible Sidebar**: Persists state to localStorage.
- **Grouped Navigation**: Organized by Desk, Operations, AI, Admin.
- **Quick Actions**: Hover over nav items to see contextual buttons (New, Refresh).

### `PageShell`
Wrapper for every page content area.
```jsx
<PageShell 
  title="My Page" 
  actions={<button className="btn-gold">Create</button>}
>
  {/* Content */}
</PageShell>
```

### `GlassCard`
Standard container for data.
```jsx
<GlassCard title="Stats">
  <div>Content</div>
</GlassCard>
```

## 3. Migration Guide
To update a legacy page:
1.  Remove `<DeskSidebar />` import and usage (Layout handles it now).
2.  Wrap content in `<PageShell>`.
3.  Replace `<div>` cards with `<GlassCard>`.
4.  Replace `<button>` with `<button className="btn-gold">` or `lucide-react` icons.
5.  Remove hardcoded colors (use `var(--atum-text-muted)`, etc).

## 4. Icons
We exclusively use `lucide-react`. Do not import from `react-icons` or other libraries.
