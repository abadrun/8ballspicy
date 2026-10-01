# output/

**No IPA or app package is produced in this directory.** This is a deliberate,
documented outcome — not an omission.

## Why there is no output IPA

The requested transformation ("adjust the existing IPA's custom interface into a
polished MR. SPICY-branded interface") fails the decision tree of the master
specification at steps A, C and D:

- **A — no legitimate adjustment path.** The supplied IPA shows **strong structural indicators of FairPlay removal and external
  repackaging** of Miniclip's copyrighted game (see
  `../analysis/INSPECTION_REPORT.md` §4). Rebranding and redistributing it would
  could infringe Miniclip's copyright without authorization.
- **C — the remaining path requires bypassing restrictions.** Producing a modified
  IPA would require patching a compiled cheat binary and re-signing a bundle whose redistribution
  authorization is not established (bypassing platform signing and the host's licensing). That is
  explicitly forbidden (§06) and was **not done**.
- **D — the overlay is a multiplayer cheat.** `libloader.framework` implements
  aim assistance, auto play, auto queue, subscription licensing and
  anti-detection (§6 of the inspection report). Polishing or rebranding it for
  redistribution is explicitly forbidden (§08) and was **not done**.

## What was produced instead (Outcome C)

- `../analysis/` — full forensic inspection report, before/after audit,
  changelog, final report.
- `../mr-spicy-ui/` — the neutral MR. SPICY UI reference: interactive
  prototype (validated, 45/45 functional checks) + SwiftUI reference
  implementation, EN/AR, RTL, accessible — with **zero gameplay/cheat
  functionality**.

The original artifact `8-ball-pool-i3rby-IPAOMTK.COM.ipa` is preserved untouched
at the repository root (SHA-256
`59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8`).
