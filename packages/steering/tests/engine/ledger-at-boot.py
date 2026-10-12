"""Scenario `ledger-at-boot` -- the open threads reach the agent ONCE (batch steering / le-skill /
les-fils-du-moment): steering's `LEDGER` document, mounted at `boot.ready`, serves
`steering-ledger` -- each open thread with its id, name and note, its steps still to do --
at the session's first block; the exchange after serves it no more; a declared compaction
serves it again. A delivered step is not in it.
"""
from __future__ import annotations

from conductor import render
from tests.harness import load_script, na_proof

TOKEN = "steering-ledger"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("ledger", packages=("steering",))
    keeper = load_script(next((env.made / ".sys" / "vendor").glob("steering@*")) / "skills" / "pp-steering" / "pp-steering.py")
    keeper.open_thread(env.made, "le-fil-du-registre", "une-etape-faite\nune-etape-a-faire | le travail qui reste\n",
                       note="le pourquoi du fil")
    tid = next(iter(keeper.load(env.made)["threads"]))
    first = keeper.load(env.made)["threads"][tid]["steps"][0]
    keeper.done(env.made, tid, first)

    booted = env.conductor("t").start(env.conductor("t").boot("BOOT.md"))
    served = dict(booted.payloads) if booted is not None else {}
    ledger = served.get(TOKEN, "")
    if (f"~ le-fil-du-registre [{tid}]" in ledger and "le pourquoi du fil" in ledger
            and "une-etape-a-faire" in ledger and "une-etape-faite" not in ledger):
        held("the boot serves the ledger", "the first block carries `steering-ledger`: the open thread with its "
             "id and note, its step still to do -- the delivered one left out")
    else:
        failures.append(f"  ✗ ledger at boot              {sorted(served)} {ledger[:160]!r}")

    after = []
    for message in ("", "the operator's next message"):         # the rest of the boot exchange, then one more
        pending = env.conductor("t").submit(message)
        for _ in range(8):
            if pending is None:
                break
            after.append(pending)
            if "INFER proof" in render(pending):
                env.conductor("t").submit(na_proof(pending))
                break
            if "FINAL" in (pending.next_call or ""):
                break
            pending = env.conductor("t").submit("")
    seen_later = [block for block in after if TOKEN in dict(block.payloads)]
    if not seen_later:
        held("the next exchange does not re-read it", "the blocks after the boot carry no `steering-ledger`: the "
             "session works from what it did")
    else:
        failures.append("  ✗ ledger re-served            a later block carries the ledger again")

    # the compaction by the console, as the agent declares it: a run of its own, its boot drained first
    opened = env.cli("-new")
    key = opened.stdout.split("run ", 1)[1].split()[0]
    shown = opened.stdout
    while "a reading continues" in shown:
        shown = env.cli(key).stdout
    declared, whole = env.cli(key, "-compacted").stdout, ""
    whole = declared
    while "a reading continues" in declared:
        declared = env.cli(key).stdout
        whole += declared
    if f"INFORMATION — {TOKEN}" in whole and f"~ le-fil-du-registre [{tid}]" in whole:
        held("a compaction serves it back", "`-compacted` by the console re-serves the boot's documents, the "
             "ledger among them")
    else:
        failures.append(f"  ✗ ledger after compaction     {whole[-240:]!r}")
    return 0
