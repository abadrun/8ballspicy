# Original IPA preservation

The repository-root file `8-ball-pool-i3rby-IPAOMTK.COM.ipa` is the reference artifact. It remains byte-for-byte unchanged.

A second 95 MB working-tree duplicate is intentionally not committed. Git already stores the tracked blob independently in the repository object database, providing the untouched recoverable copy without doubling the patchset.

Expected SHA-256:

```text
59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8
```

Verify both the working file and committed Git object:

```bash
bash ExistingIPAWorkspace/Preservation/verify_original.sh
```

Restore a fresh copy without using the working file:

```bash
git cat-file blob HEAD:8-ball-pool-i3rby-IPAOMTK.COM.ipa > /path/to/preserved-copy.ipa
sha256sum /path/to/preserved-copy.ipa
```

`8-ball-pool-i3rby-IPAOMTK.COM.ipa.sha256` is the checksum record. It is not a checksum for a modified IPA.
