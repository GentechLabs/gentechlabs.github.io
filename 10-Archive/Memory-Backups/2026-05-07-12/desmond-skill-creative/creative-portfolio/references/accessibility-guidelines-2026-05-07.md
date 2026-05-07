# Portfolio Accessibility Guidelines

**Date:** 2026-05-07  
**Source:** User feedback session — "Lol cant see image where Jordan on left is. roadmap needs to be readable."

## Key Issues Identified

### 1. Logo Visibility
- **Problem:** Thin green strokes on dark background blur at small sizes
- **User feedback:** "can't see image where Jordan on left is"
- **Root cause:** Low contrast ratio between logo outline and page background
- **Solution:** Increase stroke weight (3px+), add shadow/glow, or use solid fill

### 2. Roadmap Metadata
- **Problem:** Dark grey dates on black background are invisible
- **User feedback:** "roadmap needs to be readable"
- **Root cause:** Insufficient contrast (dark grey on near-black)
- **Solution:** Use white or near-white (`#e0e0e0` minimum) for all secondary text

## Contrast Requirements

### WCAG AA Compliance
- **Normal text:** 4.5:1 minimum contrast ratio
- **Large text (18px+):** 3:1 minimum contrast ratio
- **UI components:** 3:1 minimum contrast ratio

### Recommended Colors for Dark Theme
| Element | Minimum | Recommended | Avoid |
|---------|---------|-------------|-------|
| Body text | `#9ca3af` | `#e0e0e0` or `#ffffff` | `#6b7280` or darker |
| Small text / metadata | `#e0e0e0` | `#ffffff` | `#9ca3af` or darker |
| Logo text | 3:1 ratio | Higher is better | Thin outlines |
| Dates / deadlines | `#e0e0e0` | `#ffffff` | `#6b7280` |

## Testing Checklist

1. **Zoom test:** View at 50% viewport width — all text still readable?
2. **Contrast check:** Use WebAIM Contrast Checker (https://webaim.org/resources/contrastchecker/)
3. **Environment test:** View in bright light (sunlight) — secondary text still visible?
4. **Device test:** Check on mobile — logo doesn't blur or disappear?

## Common Mistakes

1. Using dark grey (`#6b7280` or darker) for secondary text on dark backgrounds
2. Logo strokes thinner than 2px on dark backgrounds
3. Small font sizes (under 14px) for metadata
4. Assuming contrast is fine without testing at different zoom levels

## Implementation Notes

- **Logo:** Prefer solid fills over thin outlines for dark themes
- **Roadmap dates:** Always use white or near-white text
- **Status badges:** Bright colors on dark backgrounds work well
- **Test early:** Check contrast during development, not after deployment
