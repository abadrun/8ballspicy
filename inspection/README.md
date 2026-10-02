# inspection/

Read-only inspection tools for the repository's existing IPA.

| Item | Description |
|---|---|
| `inspect_ipa.py` | Container identity, host plist, main Mach-O, encryption flag, signature coverage, framework list, and overlay markers. |
| `inspect_overlay.py` | Detailed overlay bundle metadata, linked libraries, named UI classes, localization keys, state fields, feature markers, URLs, and explicit unknowns. |
| `inventory_existing_ipa.py` | Hashes and classifies every ZIP member as ORIGINAL_GAME, EXISTING_OVERLAY, or UNKNOWN without extracting or modifying the archive. |
| `INSPECTION_OUTPUT.txt` | Captured baseline output from `inspect_ipa.py`. |
| `OVERLAY_INVENTORY.json` | Generated detailed overlay inventory. |
| `../ExistingIPAWorkspace/Inventory/IPA_FILE_INVENTORY.json` | Generated complete 3,505-entry archive inventory. |
| `extracted/` | Optional full extraction, Gitignored; not required by the inventory tools. |

Run:

```bash
python3 inspection/inspect_ipa.py
python3 inspection/inspect_overlay.py > inspection/OVERLAY_INVENTORY.json
python3 inspection/inventory_existing_ipa.py > ExistingIPAWorkspace/Inventory/IPA_FILE_INVENTORY.json
bash ExistingIPAWorkspace/Preservation/verify_original.sh
```

All scripts open the IPA read-only. Findings and interpretation are in `analysis/` and `ExistingIPAWorkspace/`.
