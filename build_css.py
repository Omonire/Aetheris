#!/usr/bin/env python3
"""Compile the FSCSS source into plain CSS.

Usage:
    python build_css.py

Requires the `fscss` executable (pip install fscss) and Node.js 20+ on PATH.
The compiled static/css/main.css is committed, so this is only needed after
editing static/fscss/main.fscss.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "static" / "fscss" / "main.fscss"
OUT = ROOT / "static" / "css" / "main.css"


def main() -> int:
    exe = shutil.which("fscss")
    if not exe:
        print("fscss was not found on PATH.", file=sys.stderr)
        print("Install it with: pip install fscss", file=sys.stderr)
        return 1

    if not SRC.exists():
        print(f"Missing FSCSS source: {SRC}", file=sys.stderr)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"Compiling {SRC.relative_to(ROOT)} -> {OUT.relative_to(ROOT)}")
    result = subprocess.run([exe, str(SRC), str(OUT)])
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
