#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from reference_pins import load_expansion_pin

UPSTREAM = "https://github.com/rh-hideout/pokeemerald-expansion.git"

ROOT = Path(__file__).resolve().parents[1]
REF = load_expansion_pin()
PATCH_DIR = ROOT / "patches" / "pokeemerald-expansion"
VERIFY_REGIONAL = ROOT / "tools" / "verify_regional_forms.py"
VERIFY_FUTURE = ROOT / "tools" / "verify_future_generation_readiness.py"

def run(*args: str, cwd: Path | None = None) -> None:
    print("+", " ".join(args))
    subprocess.run(args, cwd=cwd, check=True)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", type=Path, default=ROOT / "build" / "pokeemerald-expansion")
    args = ap.parse_args()
    target = args.target.resolve()

    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        run("git", "clone", UPSTREAM, str(target))

    if not (target / ".git").exists():
        print(f"target is not a git worktree: {target}", file=sys.stderr)
        return 2

    run("git", "fetch", "--all", "--tags", cwd=target)
    run("git", "checkout", "--detach", REF, cwd=target)
    run("git", "reset", "--hard", REF, cwd=target)
    run("git", "clean", "-fdx", cwd=target)

    for patch in sorted(PATCH_DIR.glob("*.patch")):
        run("git", "apply", "--check", str(patch), cwd=target)
        run("git", "apply", str(patch), cwd=target)

    run(sys.executable, str(VERIFY_FUTURE), str(target))
    run(sys.executable, str(VERIFY_REGIONAL), str(target))
    print(f"expanded EMERALD source prepared at {target}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
