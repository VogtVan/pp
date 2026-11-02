#!/usr/bin/env python3
"""The motor witness's skill: `verify` reads the vector on stdin and accepts every slug;
`decide <name>` prints the successor it names."""
import sys

if sys.argv[1:2] == ["decide"]:
    print(sys.argv[2] if len(sys.argv) > 2 else "")
    raise SystemExit(0)
sys.stdin.read()
raise SystemExit(0)
