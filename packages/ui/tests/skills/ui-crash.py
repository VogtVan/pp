"""Scenario `ui-crash` -- a crash of the post leaves its trace (batch la-saisie-et-le-tour), on the bench's `pp-chat`
witness: an exception the bench raises inside the application (`--press crash`) ends the post with exit 1, the
terminal names the file the trace is kept in, and the post's memory (`ui.crash` of the metadata) holds the whole
traceback, the exception's own line last. `ui crash` reads that trace back without a terminal (batch
la-trace-du-crash-lue): `--json` gives `{"crash": null}` before any crash and the kept trace after one, the bare verb
writes the trace itself, both exit 0.
"""
from __future__ import annotations

import json

from conductor.state import metadata
from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-crash")

    # --- nothing kept: the verb reads null, without a terminal ---------------------------------------------------
    before, bare = post.render("crash", "--json"), post.render("crash")
    try:
        empty = json.loads(before.raw)
    except ValueError:
        empty = None
    if before.returncode == 0 and empty == {"crash": None} and bare.returncode == 0 and bare.raw.strip():
        held("ui crash before any crash", f"--json {empty}; the bare verb exit 0, one line")
    else:
        failures.append(f"  ✗ crash read before            rc={before.returncode}/{bare.returncode} "
                        f"out={before.raw[-200:]!r} err={before.stderr[-300:]!r} {bare.stderr[-200:]!r}")

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

    # --- the trace kept is read back, as the metadata holds it ----------------------------------------------------
    read, whole = post.render("crash", "--json", keep=True), post.render("crash", keep=True)
    try:
        said = json.loads(read.raw)
    except ValueError:
        said = None
    if (trace and read.returncode == 0 and said == {"crash": trace} and whole.returncode == 0
            and whole.raw.rstrip("\n") == trace.rstrip("\n")):
        held("ui crash reads the trace kept", f"--json crash equals ui.crash ({len(trace)} chars); the bare verb "
             f"writes it whole, exit 0")
    else:
        failures.append(f"  ✗ crash read after             rc={read.returncode}/{whole.returncode} "
                        f"out={read.raw[-200:]!r} err={read.stderr[-300:]!r} {whole.stderr[-200:]!r}")
    return 0
