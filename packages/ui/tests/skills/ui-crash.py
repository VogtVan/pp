"""Scenario `ui-crash` -- a crash of the post leaves its trace (batch la-saisie-et-le-tour), on the bench's `pp-chat`
witness: an exception the bench raises inside the application (`--press crash`) ends the post with exit 1, the
terminal names the file the trace is kept in, and the post's memory (`ui.crash` of the metadata) holds the whole
traceback, the exception's own line last.
"""
from __future__ import annotations

import json

from conductor.state import metadata
from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-crash")

    # --- a crash leaves its trace -------------------------------------------------------------------------------
    crashed = post.render("ag1", "--render", "dialogue", "--size", "100x30", "--press", "crash")
    path = metadata.path_of(post.made)
    kept = json.loads(path.read_text(encoding="utf-8") or "{}") if path.is_file() else {}
    trace = str((kept.get("ui") or {}).get("crash") or "")
    if (crashed.returncode == 1 and str(path) in crashed.stderr and "RuntimeError" in trace
            and trace.rstrip().splitlines()[-1].startswith("RuntimeError") and "Traceback" in trace):
        held("a crash leaves its trace", f"exit 1; the terminal names {path.name}; ui.crash holds {len(trace)} chars, "
             f"last line {trace.rstrip().splitlines()[-1][:50]!r}")
    else:
        failures.append(f"  ✗ crash trace                 rc={crashed.returncode} kept={sorted(kept.get('ui') or {})} "
                        f"trace={trace[-200:]!r} {crashed.stderr[-400:]!r}")
    return 0
