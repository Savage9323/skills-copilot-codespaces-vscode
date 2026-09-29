---
name: ui-graphics-process
description: Run an iterative visual-quality loop for UI, graphics, responsive layouts, and presentation surfaces. Use when implementation needs visual review, screenshot comparison, responsive correction, accessibility polish, or design-quality verification.
---

# UI & Graphics Process

Core loop:

Build -> Render -> Capture -> Review -> Compare -> Correct -> Re-render -> Repeat.

## Requirements

- Review real rendered output, not code alone.
- Validate the approved design direction rather than silently redesigning it.
- Check hierarchy, spacing, typography, alignment, imagery, states, overflow, and interaction affordances.
- Validate 360px+ responsive behavior where web/mobile responsive applies.
- Validate keyboard focus and touch targets; use 44px targets where appropriate.
- Respect reduced-motion preferences.
- Keep static/progressive fallbacks when advanced graphics or 3D are optional.
- Record findings with severity and reproducible evidence.
- Continue the correction loop until critical/high findings are resolved or explicitly blocked.

Use PASS / FAIL / UNTESTED when evidence is incomplete.
