---
name: build-environment-compatibility
description: Design and verify reproducible cross-platform development and runtime environments. Use for Windows/WSL/Linux/ChromeOS, Docker, browsers, devices, CI parity, local AI runtimes, dependency compatibility, accessibility, performance, and environment troubleshooting.
---

# Build Environment & Compatibility

## Targets

When relevant, account for Windows, WSL2/Ubuntu/Linux, ChromeOS/Crostini, Docker/CI, Chrome/Edge/Firefox/Safari, desktop/mobile responsive widths from 360px+, keyboard/touch, and Android/iOS/iPadOS where the product targets them.

## Workflow

1. Inspect actual runtime/tool versions.
2. Identify required and optional capabilities.
3. Pin reproducible dependencies and package-manager versions.
4. Verify clean install.
5. Run lint/typecheck/tests/build.
6. Verify Docker where relevant.
7. Verify browser/device behavior.
8. Check accessibility and reduced-motion behavior.
9. Provide progressive fallbacks for unsupported capabilities.
10. Record PASS / FAIL / UNTESTED per target.

Never claim compatibility for an untested target.
