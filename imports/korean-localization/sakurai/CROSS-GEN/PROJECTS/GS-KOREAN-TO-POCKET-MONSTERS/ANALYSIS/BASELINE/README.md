# ROM baseline survey

This survey was generated directly from the supplied read-only ROM files.
No ROM bytes or extracted copyrighted payloads are included.

## Scope

- ROM files scanned: 23
- 16 KiB banks scanned: 1760
- Valid header checksums: 23/23
- Valid global checksums: 23/23
- Same-title revision comparisons: 11

## Outputs

- `rom_manifest.csv/json`: identities, cryptographic hashes, cartridge header fields, and checksum validation
- `bank_inventory.csv/json`: one record per 16 KiB bank with hashes and structural statistics
- `revision_diffs.csv/json`: compact summaries of same-title revision comparisons
- `revision_bank_diffs.csv/json`: per-bank changed-byte and changed-range counts

## Reproduction

```bash
python3 rom_baseline_scan.py /path/to/project_sources /path/to/output
```

The filenames are classification inputs; SHA-1/SHA-256 values are the durable identities.
