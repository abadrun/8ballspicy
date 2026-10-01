# inspection/

Read-only forensic inspection of the supplied IPA.

| Item | Description |
|---|---|
| `inspect_ipa.py` | Dependency-free, reproducible inspector. Reads the IPA directly from the repository root and prints every machine-checkable finding: container identity, host-app Info.plist (incl. tampered keys), Mach-O load commands, FairPlay cryptid, re-signature coverage, framework inventory, cheat-marker strings and mod-menu classes inside `libloader.framework`. |
| `INSPECTION_OUTPUT.txt` | Captured output (the evidence record). |
| `extracted/` | Full 205 MB extraction of the IPA used during manual inspection. **Gitignored** — regenerate anytime with `unzip 8-ball-pool-i3rby-IPAOMTK.COM.ipa -d inspection/extracted`. |

The original IPA is never modified — the script opens it read-only, and the
extraction writes to a separate directory.

Run:

```bash
python3 inspection/inspect_ipa.py
```

Findings and interpretation: `../analysis/INSPECTION_REPORT.md`.
