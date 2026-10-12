"""Scenario `agent-documents` -- 4 case(s) (batch les-fichiers-sous-l-equipe, 2026-10-10): `--documents
<dir>` gives a run its root of documents, carried by `PP_DOCUMENTS` on the house's `-new` alone.
- (a) an opening under `--documents`: the run resolves from the directory (a door it alone carries), the
  slot keeps the absolute path; a path relative to the house is made absolute
- (b) nothing inherits it: the harness's environment carries no `PP_DOCUMENTS`
- (c) a resume keeps its root: `--run <key> --documents <another>` refuses `documents-fixed` before any
  launch, the records unchanged; the same root, or none, plays
- (d) the conversation says it: `chat --json --documents <dir>` opens its flow on `ready` with `documents`
"""
from __future__ import annotations

import json

from conductor import persistence
from tests.harness import support

A = support(__file__, "agent")
ROOTED = "---\nname: ROOTED\nkind: proc\ndescription: a door the root alone carries\nproc: |\n  WORK\n---\n\nThe root's door.\n"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    root = h.ws / "teams" / "alpha"
    root.mkdir(parents=True)
    (root / "ROOTED.md").write_text(ROOTED, encoding="utf-8")
    other = h.ws / "teams" / "beta"
    other.mkdir(parents=True)

    # --- (a) an opening under --documents resolves from the directory ----------------------------------
    opened = h.wake("first ask", "play", "--documents", "teams/alpha", "--door", "ROOTED.md")
    key = h.keys()[0] if h.keys() else ""
    slot = persistence.slot_of(h.agent_meta, key) if key else None
    kept = persistence.documents_of(slot) if slot is not None and hasattr(persistence, "documents_of") else ""
    doors = [one.get("document") for one in h.trace(key) if one.get("kind") == "door"] if key else []
    if opened.returncode == 0 and kept == str(root) and doors == ["ROOTED.md"]:
        held("(a) an opening under --documents", f"run {key}: the door ROOTED.md of teams/alpha opens; the slot "
             "keeps the absolute path")
    else:
        failures.append(f"  ✗ (a) the opening               rc={opened.returncode} kept={kept!r} doors={doors} "
                        f"{opened.stderr[-300:]!r}")

    # --- (b) the harness inherits nothing -----------------------------------------------------------
    seen = h.environment()
    if opened.returncode == 0 and seen and "PP_DOCUMENTS" not in seen:
        held("(b) the harness inherits nothing", "the witness's environment carries no PP_DOCUMENTS")
    else:
        failures.append(f"  ✗ (b) the harness's environment rc={opened.returncode} "
                        f"documents={seen.get('PP_DOCUMENTS')!r} keys={len(seen)}")

    # --- (c) a resume keeps its root -------------------------------------------------------------------
    before = h.counted()
    moved = h.call("agent", "run", "agents/ag1", "--run", key, "--message", "later", "--documents", str(other),
                   *h.harnessed("play")) if key else None
    after_moved = h.counted()
    same = h.call("agent", "run", "agents/ag1", "--run", key, "--message", "again", "--documents", str(root),
                  *h.harnessed("play")) if key else None
    bare = h.call("agent", "run", "agents/ag1", "--run", key, "--message", "once more",
                  *h.harnessed("play")) if key else None
    if (moved is not None and moved.returncode == 2 and "documents-fixed" in moved.stderr
            and after_moved == before and same.returncode == 0 and bare.returncode == 0):
        bench.refusals += 1
        held("(c) a resume keeps its root", "another root: documents-fixed before any launch, the records "
             "unchanged; the same root and none play")
    else:
        failures.append(f"  ✗ (c) documents-fixed           moved={moved and moved.returncode} "
                        f"same={same and same.returncode} bare={bare and bare.returncode} "
                        f"records={before}->{after_moved} {(moved.stderr if moved else '')[-200:]!r}")

    # --- (d) the conversation says its root ------------------------------------------------------------
    chat = h.call("agent", "chat", "agents/ag1", "--json", "--documents", "teams/alpha",
                  *h.harnessed("play"), stdin="")
    ready = {}
    for line in chat.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("kind") == "ready":
            ready = event
            break
    if chat.returncode == 0 and ready.get("documents") == str(root):
        held("(d) the conversation says its root", "chat --json --documents teams/alpha: `ready` says the "
             "absolute directory")
    else:
        failures.append(f"  ✗ (d) ready                     rc={chat.returncode} ready={ready} {chat.stderr[-200:]!r}")
    return 0
