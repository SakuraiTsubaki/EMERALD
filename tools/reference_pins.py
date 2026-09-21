#!/usr/bin/env python3
"""Read pinned upstream revisions from EMERALD manifests."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def _require_sha(value: str, source: Path) -> str:
    if not re.fullmatch(r"[0-9a-fA-F]{40}", value):
        raise ValueError(f"invalid 40-character git SHA in {source}: {value!r}")
    return value.lower()

def load_pkhex_pin() -> str:
    path = ROOT / "manifests" / "pkhex-source-pin.yml"
    text = _read(path)
    match = re.search(r"(?m)^\s*commit:\s*([0-9a-fA-F]{40})\s*$", text)
    if not match:
        raise ValueError(f"PKHeX commit not found in {path}")
    return _require_sha(match.group(1), path)

def load_expansion_pin() -> str:
    path = ROOT / "manifests" / "engine-base.yml"
    text = _read(path)
    match = re.search(
        r"(?ms)^  expanded:\s*\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\s*$|\Z)",
        text,
    )
    if not match:
        raise ValueError(f"expanded profile not found in {path}")
    ref = re.search(r"(?m)^    ref:\s*([0-9a-fA-F]{40})\s*$", match.group("body"))
    if not ref:
        raise ValueError(f"expanded profile ref not found in {path}")
    return _require_sha(ref.group(1), path)
