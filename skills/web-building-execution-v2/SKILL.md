---
name: web-building-execution-v2
description: Execute implementation-ready websites, web apps, SaaS, ecommerce, internal tools, and digital products from an existing brief or handoff. Use when the user wants autonomous implementation with design, accessibility, SEO, security, performance, compatibility, analytics, and launch evidence.
---

# Web Building Execution v2

The project handoff defines what to build. This skill defines how to execute it.

## Workflow

INTAKE -> INSPECT -> PLAN -> BUILD -> VISUAL_QA -> RESPONSIVE_A11Y_QA -> FIX -> VERIFY -> PREVIEW_APPROVAL -> PRODUCTION_CUTOVER.

## Core rules

- Inspect repository/branch and preserve existing work before coding.
- Do not re-plan approved product direction without a material conflict.
- Use locked reproducible installs.
- Run lint, typecheck, tests, production build, and browser checks appropriate to the stack.
- Mobile-first and responsive from 360px+ unless product requirements differ.
- Target WCAG 2.2 AA behavior where applicable.
- Keep crawlable SEO and Core Web Vitals in mind.
- Treat advanced 3D/WebGL as progressive enhancement with functional static fallback unless it is core product functionality.
- Use design-system/component governance rather than ad-hoc styling.
- Include trust, claims/evidence, analytics, search/discovery, lifecycle content, and CRO only where relevant to the product.
- Never fabricate claims, enforcement, platform capabilities, data, or test results.
- Isolate changes on branch/PR when appropriate.
- Continue autonomously until a genuine owner blocker.

## Definition of Done

Functional, tested, visually reviewed, responsive, accessible, performant, secure, SEO-compatible where relevant, browser-compatible for claimed targets, analytics-ready where required, documented, integrated, deployed when authorized, and production-verified.
