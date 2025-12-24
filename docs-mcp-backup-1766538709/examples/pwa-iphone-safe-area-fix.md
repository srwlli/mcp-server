# PWA iPhone Safe Area / Notch Fix

## Problem

On iPhones with notches (iPhone X and later) or Dynamic Island, PWA content bleeds into the safe area zones when scrolling. Users see the page body content visible through the notch/status bar area.

## Root Cause

Three things must work together for proper safe area handling in PWAs:

1. **viewport-fit=cover** - Tells the browser to extend content to screen edges
2. **Safe area CSS insets** - Pads content away from notch/home indicator
3. **overflow-x: hidden** - Prevents horizontal scroll bleed

Missing any of these causes content to appear in the notch area.

## Solution

### 1. Viewport Configuration (Next.js)

In `src/app/layout.tsx`:

```typescript
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",  // Required for safe area to work
  themeColor: "#0a0a0a",
};
```

### 2. Safe Area Insets for Fixed Headers

For fixed headers that sit at the top of the viewport:

```tsx
<header
  className="fixed top-0 left-0 right-0 z-50 bg-background"
  style={{ paddingTop: 'env(safe-area-inset-top)' }}
>
  {/* header content */}
</header>
```

### 3. Content Offset Below Fixed Header

The content wrapper must account for both header height AND safe area:

```tsx
<div
  style={{ paddingTop: 'calc(3.5rem + env(safe-area-inset-top))' }}
>
  {children}
</div>
```

Where `3.5rem` = header height (h-14 in Tailwind = 56px).

### 4. Prevent Horizontal Scroll Bleed

In `globals.css`:

```css
@layer base {
  html {
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
    overflow-x: hidden;  /* Prevents notch bleed */
  }
  body {
    overflow-x: hidden;  /* Prevents notch bleed */
  }
}
```

## Why overflow-x: hidden Matters

Even with proper safe area padding, horizontal overflow can cause content to "peek" into the notch area during scroll momentum or elastic bounce effects. Setting `overflow-x: hidden` on both html and body prevents this edge case.

## Complete Checklist

- [ ] `viewportFit: "cover"` in Next.js viewport config
- [ ] `paddingTop: 'env(safe-area-inset-top)'` on fixed header
- [ ] `paddingTop: 'calc(headerHeight + env(safe-area-inset-top))'` on content wrapper
- [ ] `overflow-x: hidden` on html element
- [ ] `overflow-x: hidden` on body element
- [ ] PWA manifest with `"display": "standalone"`
- [ ] Apple meta tag: `<meta name="apple-mobile-web-app-capable" content="yes">`

## Testing

1. Add PWA to iPhone home screen
2. Open app and scroll up/down vigorously
3. Check that notch area remains solid (no content visible)
4. Test on both notch devices (iPhone X-14) and Dynamic Island (iPhone 14 Pro+)

## Related CSS Environment Variables

```css
env(safe-area-inset-top)    /* Notch/Dynamic Island */
env(safe-area-inset-bottom) /* Home indicator */
env(safe-area-inset-left)   /* Landscape left */
env(safe-area-inset-right)  /* Landscape right */
```

## Framework: Next.js 15 + Tailwind CSS 4
