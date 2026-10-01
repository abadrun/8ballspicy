# Prototype validation

`validate-prototype.mjs` runs the interactive prototype in [jsdom](https://github.com/jsdom/jsdom)
(no browser required) and asserts **45 functional checks**:

- boot without JS errors; initial state (closed, EN/LTR)
- overlay state machine: closed → expanded → minimized → expanded → closed
- section navigation + `aria-current`
- settings interactions (switches, sliders, class application)
- modals: open/close, focus restoration, Escape key
- EN→AR language switch: `lang`/`dir` attributes, string tables, dynamic values
- sign-in / sign-out / reset flows (local demo state only)
- tools logic (log levels, meter switch)
- accessibility invariants (roles, labels, aria-modal, aria-live)

Run:

```bash
npm install jsdom        # once
node validate-prototype.mjs
```

Result at time of writing: **45/45 checks passed.**

NOT validated here: pixel rendering, real browser behavior, real iOS behavior —
no browser/CDN access and no Xcode exist in the Linux sandbox (see
`analysis/FINAL_REPORT.md`, "Validation not performed").
