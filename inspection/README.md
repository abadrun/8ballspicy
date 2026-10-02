# inspection/

Read-only inspection tools for the repository's existing IPA.

| Item | Description |
|---|---|
| `inspect_ipa.py` | Container identity, safe optional extraction, host plist, main Mach-O, encryption flag, signature coverage, framework list, and overlay/i3rby markers. |
| `inspect_overlay.py` | Detailed overlay bundle metadata, linked libraries, named UI classes, localization keys, state fields, feature markers, URLs, and explicit unknowns. |
| `inventory_existing_ipa.py` | Hashes/classifies every ZIP member and records all bundle IDs, frameworks, dylibs, Mach-O slices, resource types, Info.plist metadata, and exact i3rby attribution evidence without extracting or modifying the archive. |
| `INSPECTION_OUTPUT.txt` | Captured baseline output from `inspect_ipa.py`. |
| `OVERLAY_INVENTORY.json` | Generated detailed overlay inventory. |
| `../ExistingIPAWorkspace/Inventory/IPA_FILE_INVENTORY.json` | Generated schema-v2, complete 3,505-entry archive inventory. |
| `extracted/` | Optional full extraction, Gitignored; temporary system extraction is preferred. |

Run:

```bash
sha256sum 8-ball-pool-i3rby-IPAOMTK.COM.ipa
work="$(mktemp -d /tmp/8ballspicy-baseline.XXXXXX)"
python3 inspection/inspect_ipa.py --extract-to "$work"
rm -rf "$work"
python3 inspection/inspect_overlay.py > inspection/OVERLAY_INVENTORY.json
python3 inspection/inventory_existing_ipa.py > ExistingIPAWorkspace/Inventory/IPA_FILE_INVENTORY.json
bash ExistingIPAWorkspace/Preservation/verify_original.sh
```

The extraction path is explicit and guarded against absolute/parent-traversal ZIP members. All tools open the IPA itself read-only. Findings and interpretation are in `analysis/` and `ExistingIPAWorkspace/`.
