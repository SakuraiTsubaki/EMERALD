#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

UPSTREAM = "https://github.com/rh-hideout/pokeemerald-expansion.git"
REF = "75b806a3ab57a81ff1eb6179288981f0b3cc3050"

ROOT = Path(__file__).resolve().parents[1]
PATCH_DIR = ROOT / "patches" / "pokeemerald-expansion"
VERIFY = ROOT / "tools" / "verify_regional_forms.py"


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

    run(sys.executable, str(VERIFY), str(target))
    print(f"expanded regional-form source prepared at {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
