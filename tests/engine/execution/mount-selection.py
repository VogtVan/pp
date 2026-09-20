"""Scenario `mount-selection` -- 7 case(s) (plan core, phase l-execution):
- a mount entry's `body` may be a LIST of selections: each one is served alone, titled
  `<document>[<selection>]`, the rest of the body left out -- stacked
- the same entry nested: the parts sit under the segment's heading
- each part is a reading of the one reader: spared at a second mount, its hash apart
- the selection stands at the slot and comes back after a declared compaction
- a start tag found on no line: `missing`, said, `serve-stale` pushed
- a badly written selection refuses `mount-invalid`, the slot's bytes untouched
- the block's weight tells the effect: the whole body against the selection
"""
from __future__ import annotations

import json

from conductor import persistence, reading

NODE = """---
name: NODE
kind: doc
---

# NODE

## Alpha
a1 -- the ground nobody asked for
a2
## Beta
b1
b2
## Gamma
g1
## Delta
d1
"""
PARTS = ["## Beta..## Gamma", "## Delta.."]
FLOOR = "---\nname: FLOOR\nkind: proc\ndescription: a floor\ncycle: true\nproc: |\n  INFER\n---\n\nthe floor\n"


def _lines(made, kind: str) -> list[dict]:
    return [one for log in sorted((made / ".sys" / "state").glob("session-*.jsonl"))
            for one in map(json.loads, filter(str.strip, log.read_text(encoding="utf-8").splitlines()))
            if one.get("kind") == kind]


def _ledger(made) -> list[dict]:
    return [line for block in _lines(made, "block") for line in (block.get("served") or [])]


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("msel")
    settings = env.made / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8").replace(
        "proc_body_serve: always", "proc_body_serve: once"), encoding="utf-8")
    env.write("NODE.md", NODE)
    env.write("FLOOR.md", FLOOR)
    titles = [f"NODE[{part}]" for part in PARTS]

    def opened(key: str):
        runner = env.conductor(key)
        runner.forget()
        runner.start(env.made / "FLOOR.md")
        return lambda: env.conductor(key)

    # --- (1) stacked: the asked parts alone, each under its own title -----------------------
    stacked = opened("s")
    said = stacked().mount([{"doc": "NODE.md", "body": PARTS}])
    if (all(f"INFORMATION — {title}\n" in said for title in titles)
            and "## Beta\nb1\nb2" in said and "## Delta\nd1" in said
            and "a1 -- the ground" not in said and "g1" not in said):
        held("a stacked entry serves its parts", "two readings under `NODE[<selection>]`, the "
             "rest of the body left out")
    else:
        failures.append(f"  ✗ the stacked parts           {said[-500:]!r}")

    # --- (3) a second mount of the same parts is spared; a part's hash is its own ------------
    again = env.conductor("s").mount([{"doc": "NODE.md", "body": PARTS, "constraints": False}])
    states = [(line["subject"], line["state"], line.get("origin")) for line in _ledger(env.made)
              if line["subject"].startswith("NODE[")]
    path = env.made / "NODE.md"
    hashes = {reading.served(path)[1], *(reading.spanned(path, reading.ranged(f"x[{part}]")[1].span)[1]
                                         for part in PARTS)}
    if (states.count((titles[0], "served", "mount")) == 1
            and states.count((titles[0], "spared", "mount")) == 1
            and "b1" not in again and len(hashes) == 3):
        held("a part is proven and spared", "served once, `spared` at the second mount, origin "
             "`mount`; the hash of a part is not the body's")
    else:
        failures.append(f"  ✗ the spared parts            {states} {len(hashes)} hashes")

    # --- (4) the selection stands at the slot and comes back after a compaction -------------
    kept = persistence.mounted_of(env.session())
    back = {subject for subject, _ in env.conductor("s").compacted().payloads}
    reserved = [line["subject"] for line in _ledger(env.made) if line.get("state") == "reserved"]
    if kept and kept[0]["body"] == PARTS and set(titles) <= back and set(titles) <= set(reserved):
        held("the selection comes back", "the list stands at the slot; after `-compacted` the "
             "same parts are served again, `reserved`")
    else:
        failures.append(f"  ✗ the re-serve                {kept!r} {sorted(back)} {reserved}")

    # --- (2) nested: the same parts under the segment's heading -----------------------------
    nested = opened("n")
    said = nested().mount([{"doc": "NODE.md", "scope": "nested", "body": PARTS}])
    returned = {subject for subject, _ in env.conductor("n").compacted().payloads}
    if ("▸ NODE" in said and all(f"INFORMATION — {title}\n" in said for title in titles)
            and "## Beta\nb1\nb2" in said and "a1 -- the ground" not in said
            and set(titles) <= returned):
        held("a nested entry serves its parts", "the same two readings under the segment's "
             "heading, and back after `-compacted`")
    else:
        failures.append(f"  ✗ the nested parts            {said[-500:]!r}")

    # --- (5) a start tag found on no line ---------------------------------------------------
    absent = opened("a")
    before = len([one for one in _lines(env.made, "signal") if one.get("signal") == "serve-stale"])
    said = absent().mount([{"doc": "NODE.md", "body": ["## Nowhere..## Gamma", "## Delta.."]}])
    stale = len([one for one in _lines(env.made, "signal") if one.get("signal") == "serve-stale"])
    missing = [line["subject"] for line in _ledger(env.made) if line.get("state") == "missing"]
    if "NODE[## Nowhere..## Gamma]" in missing and stale == before + 1 and "## Delta\nd1" in said:
        held("an absent tag is said", "`missing` for that part, `serve-stale` pushed, the other "
             "part served")
    else:
        failures.append(f"  ✗ the absent tag              {missing} {stale - before} signal(s)")

    # --- (6) a badly written selection refuses, nothing written ------------------------------
    torn = opened("t")
    slot = persistence.slot_of(env.made, "t")
    bytes_before = slot.read_bytes()
    for body in ([".."], ["a..b..c"], [], [3]):
        expect("mount-invalid", lambda body=body: torn().mount([{"doc": "NODE.md", "body": body}]))
    if slot.read_bytes() == bytes_before:
        held("a refusal writes nothing", "four badly written selections, the slot's bytes untouched")
    else:
        failures.append("  ✗ the slot moved under a refused mount")

    # --- (7) the weight of the block: the whole body against the selection ------------------
    whole = opened("w")
    whole().mount([{"doc": "NODE.md", "body": True}])
    served = [line for line in _ledger(env.made)
              if line.get("origin") == "mount" and line.get("state") == "served"]
    heavy = max((line.get("chars", 0) for line in served if line["subject"] == "NODE"), default=0)
    thin = max((line.get("chars", 0) for line in served if line["subject"] == titles[0]), default=0)
    if 0 < thin < heavy:
        held("the trace tells the effect", f"{heavy} c mounted whole, {thin} c for one selection")
    else:
        failures.append(f"  ✗ the weight                  whole={heavy} selection={thin}")
    return 0
