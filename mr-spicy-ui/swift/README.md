# MR. SPICY — SwiftUI reference implementation

iOS 16+ / SwiftUI. Equivalent to `../prototype` (same tokens, components,
states, localization, RTL).

## Files

| File | Role |
|---|---|
| `SpicyTheme.swift` | All design tokens (colors, spacing, radii, type, motion, metrics) + panel chrome + button styles |
| `SpicyLocalization.swift` | `SpicyLanguage` (en/ar) + EN/AR string tables + RTL `layoutDirection` |
| `SpicyComponents.swift` | Row primitives: group, toggle row, slider row, navigation row, segmented row, meter row, key-value row, chip |
| `SpicyFeatureCircle.swift` | Circular feature control (active/inactive/disabled) + circles row |
| `SpicyHeaderView.swift` | Panel header: logo, wordmark, subtitle, settings/minimize/close controls |
| `SpicyModalView.swift` | Consistent modal container: scrim, card, actions, reduce-motion-aware transitions |
| `SpicyHomeView.swift` | Home section + neutral Tools (developer-tool) section |
| `SpicySettingsView.swift` | Settings section (appearance / motion / general) |
| `SpicyAccountView.swift` | Honest demo Account section + About section |
| `SpicyOverlayView.swift` | Overlay state machine (closed → minimized → expanded), modals, toast, demo backdrop |
| `SpicyDemoApp.swift` | Minimal demo host app |

## Integration into Xcode

1. Create an iOS app target (SwiftUI lifecycle), deployment target iOS 16+.
2. Add every `.swift` file in this folder to the target.
3. Copy `../prototype/assets/logo-circle-512.png` into `Assets.xcassets` as an
   image set named **`SpicyLogo`** (single universal scale is fine).
4. Build & run `SpicyDemoApp`.

The overlay component itself is `SpicyOverlayView`; embed it in any legitimate
authorized host. Its public state (`SpicyOverlayState`, `SpicySection`,
`SpicyModal`, `SpicySettings`) is intentionally small and UI-only — it contains
no gameplay hooks because it has no gameplay functionality.

## Compile status

**NOT compiled in this environment** — the sandbox is Linux with no Xcode/Swift
toolchain. The files were written against stable iOS 16-era SwiftUI APIs and
structurally checked (brace/paren balance, memberwise-init argument order,
SF Symbol names), but a compile pass in Xcode is still required before use.
See `../../analysis/FINAL_REPORT.md` for the exact validation boundary.
