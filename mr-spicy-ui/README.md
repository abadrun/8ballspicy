# MR. SPICY — Neutral UI Reference

**What this is:** a standalone, premium "MR. SPICY" control-panel UI
implementation — design system, components, EN/AR localization, RTL mirroring,
responsive layout, accessibility — produced as the legitimate fallback path of
the master specification (Outcome C, §32; decision tree §29).

**What this is NOT:**
- It is **not** a modification of the supplied IPA and contains none of its code.
- It contains **no gameplay, aim-assist, automation, queue, anti-detection or
  entitlement/licensing functionality** — by construction.
- It is **not affiliated with, endorsed by, or connected to** Miniclip,
  8 Ball Pool, or any other game or product.

It is intended to be reused inside **legitimate authorized software**:
settings panels, developer/debug panels, accessibility panels, or an
authorized application's own UI.

## Contents

| Path | Contents |
|---|---|
| `prototype/` | Interactive HTML/CSS/JS prototype — the design system realized and testable in a browser (open `prototype/index.html`, or serve the folder). |
| `swift/` | Equivalent SwiftUI reference implementation (iOS 16+) — tokens, components, overlay state machine. Not compiled here (no Xcode in the Linux sandbox). |
| `validation/` | jsdom-based functional test harness (45 checks) + README. |

## Design system summary

- **Surfaces:** `#0B090D` base, `#1A151B` panel, `#251E27` / `#2C242E` elevated, optional pure-black (AMOLED).
- **Brand:** chili red `#D20D0F` (sampled from the supplied `logo.png` mark), gradient `#FF6A4D → #E5322B → #B00B0D`.
- **Ink:** `#F4EFF2` / `#B9AFB8` / `#8E8390`; lines at 11% / 6% white.
- **4 pt spacing scale;** radii 10/14/20/26; ≥44 pt touch targets; 58 pt feature circles.
- **Type:** 21/16/14.5/12.5/11.5/10.5 pt scale, scaled by the Text-size preference.
- **Motion:** 140/220/320 ms, `cubic-bezier(.32,.72,.28,1)`, fully disabled under Reduce Motion.

All tokens live in exactly two places and mirror each other 1:1:
`prototype/css/spicy.css` (`:root`) and `swift/SpicyTheme.swift` (`SpicyTheme.*`).

## Feature circles

Six navigation concepts — **Home, Tools, Settings, Language, Account, About** —
chosen as *neutral* demonstrations of the circle pattern. The overlay concept
inventory found in the supplied binary (see `../analysis/INSPECTION_REPORT.md` §9)
contained gameplay-automation sections (Aim Mode, Auto Play, Auto Queue, …);
those were **deliberately not implemented** — the specification (§08, §13)
forbids implementing gameplay-manipulation functionality or rebranding it.

## Localization & RTL

- Full EN + AR string tables: `prototype/js/spicy-i18n.js`,
  `swift/SpicyLocalization.swift`.
- RTL is implemented with CSS logical properties / SwiftUI `layoutDirection`
  (real mirroring — icons, chevrons, alignment, direction), **not** string reversal.
- Arabic typography rules applied (no letter-spacing, taller line height).

## Branding asset

`logo.png` (1254×1254, RGB, red mark on solid black) is **preserved unmodified**
at the repository root. Derived assets used by the UI are circular RGBA crops
(`prototype/assets/logo-circle-{64,128,256,512}.png`) generated from it without
stretching or distortion; add the 512 px version to an Xcode asset catalog as
`SpicyLogo` for the SwiftUI target.
