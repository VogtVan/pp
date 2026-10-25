"""packages/steering/skills/pp-steering -- the keeper of the STEPS, played in process on one
instance: a step minted at the member's counter with its name, its date and its work, both
fixed for good; its comment, status, reason and labels moved by their verbs alone, each move
dating `touched`; a label that orders its steps and dissolves without touching them; a name
unique among the steps still to do; a key verified through the engine and unique at the
dictionary; every refusal exiting before a byte of the record moves; a record of the thread
model refused, never read; `list` and `show` as data, the name and the id on every step; the
clock frozen by `PP_NOW`."""
from __future__ import annotations

import json

from tests.harness import load_script, support

K = support(__file__, "keeper")

T0 = "2026-10-20T08:00:00+00:00"
T1 = "2026-10-21T09:30:00+00:00"


def scenario(bench) -> int:
    root = bench.env("steering", ("steering",), pin=False).made
    keeper = load_script(K.script_of(root))
    spool = K.spool(root)
    member = root.resolve().parent.name

    def step(sid: str) -> dict:
        return K.record(root)["steps"][sid]

    def unmoved(call, code: str) -> bool:
        """A refusal by `code`, the record byte-identical before and after."""
        before = spool.read_bytes() if spool.is_file() else None
        bench.expect_exit(code, call)
        return (spool.read_bytes() if spool.is_file() else None) == before

    # --- a step is born with its name, its date and its work ----------------------------------
    with K.case(bench, "add mints a step", "an id `<member>.s.1` at the member's counter; the name, the "
                "work, `at` and `touched` at the frozen instant, `open`, no comment, no label") as check:
        with K.frozen(T0):
            first = K.minted(keeper, "le-premier-pas", "écrire le premier pas du carnet")
        check(first == f"{member}.s.1" and K.record(root)["counters"] == {"s": 1}, f"the id {first}")
        seen = K.shown(keeper, first)
        check((seen["id"], seen["name"], seen["work"], seen["status"]) == (first, "le-premier-pas",
              "écrire le premier pas du carnet", "open"), f"the step {seen}")
        check(seen["at"] == seen["touched"] and seen["at"].startswith("2026-10-20T08:00:00"), "the date is the clock's")
        check(seen["comment"] == "" and seen["labels"] == [] and seen["archived"] is None, "nothing else")

    # --- the name and the work never move ------------------------------------------------------
    with K.case(bench, "the name and the work are fixed", "comment, wait, open, done, drop, label, note, order "
                "and dissolve played on one step: name and work byte-identical, comment, status, reason and "
                "labels moved by their verb, `touched` moved by the comment and the statuses") as check:
        fixed = (step(first)["name"], step(first)["work"])
        with K.frozen(T1):
            K.said(keeper, "comment", first, "le", "carnet", "est", "ouvert")
        check(step(first)["comment"] == "le carnet est ouvert" and step(first)["touched"].startswith("2026-10-21T09:30"),
              "the comment dates touched")
        K.said(keeper, "wait", first, "attend", "la", "machine")
        check((step(first)["status"], step(first)["reason"]) == ("waiting", "attend la machine"), "waiting, its reason")
        K.said(keeper, "open", first)
        check((step(first)["status"], step(first)["reason"]) == ("open", ""), "open, the reason cleared")
        K.said(keeper, "label", first, "+le-carnet", "+la-refonte")
        K.said(keeper, "note", "le-carnet", "les", "étapes", "du", "carnet")
        K.said(keeper, "order", "le-carnet", first)
        K.said(keeper, "label", first, "-la-refonte")
        check(step(first)["labels"] == ["le-carnet"], f"the labels {step(first)['labels']}")
        K.said(keeper, "done", first)
        check(step(first)["status"] == "done", "done")
        K.said(keeper, "drop", first, "fait", "ailleurs")
        check((step(first)["status"], step(first)["reason"]) == ("dropped", "fait ailleurs"), "dropped, its reason")
        check((step(first)["name"], step(first)["work"]) == fixed and step(first)["at"].startswith("2026-10-20T08:00"),
              "name, work and date never moved")

    # --- a label orders its steps and dissolves without touching them -------------------------
    with K.case(bench, "a label orders and dissolves", "a label born by `label`, its note, its order; "
                "`dissolve` takes it out of the record and of every step, each step keeping its status") as check:
        a = K.minted(keeper, "un-pas-a", "le pas a", "--label", "le-lot")
        b = K.minted(keeper, "un-pas-b", "le pas b", "--label", "le-lot")
        K.said(keeper, "wait", b, "attend", "a")
        check(K.record(root)["labels"]["le-lot"]["order"] == [a, b], "the order of birth")
        K.said(keeper, "order", "le-lot", b, a)
        check(K.record(root)["labels"]["le-lot"]["order"] == [b, a], "the order given")
        statuses = (step(a)["status"], step(b)["status"])
        K.said(keeper, "dissolve", "le-lot")
        check("le-lot" not in K.record(root)["labels"] and step(a)["labels"] == [] == step(b)["labels"],
              "gone from the record and the steps")
        check((step(a)["status"], step(b)["status"]) == statuses, "the statuses kept")

    # --- the name is unique among the steps still to do ---------------------------------------
    with K.case(bench, "a name is unique while its work is due", "a name an open or waiting step wears "
                "refuses `name-taken`; once that step is done, the name is free again") as check:
        check(unmoved(lambda: keeper.main(["add", "un-pas-a", "le meme nom"]), "name-taken"), "open: refused, nothing written")
        check(unmoved(lambda: keeper.main(["add", "un-pas-b", "le meme nom"]), "name-taken"), "waiting: refused")
        K.said(keeper, "done", a)
        again = K.minted(keeper, "un-pas-a", "le meme nom, une autre fois")
        check(step(again)["name"] == "un-pas-a" and again != a, "free once done")
        check(unmoved(lambda: keeper.main(["open", a]), "name-taken"), "reopening a twin refused")

    # --- the key: verified by its family, unique at the dictionary ----------------------------
    with K.case(bench, "the key", "a key the engine refuses is relayed by its code; a key off the grammar "
                "refuses key-invalid; a key already held refuses step-taken -- nothing written") as check:
        check(unmoved(lambda: keeper.main(["add", "sans-famille", "x", "--key", "pas-un-vecteur"]), "key-invalid"),
              "off the grammar")
        check(unmoved(lambda: keeper.main(["add", "famille-inconnue", "x", "--key", "zorg:x"]), "family-unknown"),
              "a family nobody declares")
        forged = K.record(root)
        forged["steps"][again]["key"] = "zorg:held"
        spool.write_text(json.dumps(forged, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        check(unmoved(lambda: keeper.main(["add", "la-meme-cle", "x", "--key", "zorg:held"]), "step-taken"),
              "a key held once")

    # --- every refusal exits before a byte moves ----------------------------------------------
    with K.case(bench, "the refusals write nothing", "step-unknown, status-invalid, name-invalid, budget, "
                "label-unknown, step-invalid (no work, no reason): exit 2, the record byte-identical") as check:
        for code, argv in (("step-unknown", ["done", f"{member}.s.999"]),
                           ("step-invalid", ["done", "pas-un-id"]),
                           ("status-invalid", ["done", a]),
                           ("name-invalid", ["add", "Pas_Kebab", "x"]),
                           ("step-invalid", ["add", "sans-travail"]),
                           ("step-invalid", ["wait", again]),
                           ("budget", ["add", "trop-long", "x" * 101]),
                           ("budget", ["comment", again, "x" * 101]),
                           ("label-unknown", ["note", "aucune", "x"]),
                           ("label-unknown", ["dissolve", "aucune"])):
            check(unmoved(lambda argv=argv: keeper.main(argv), code), f"{code} wrote")

    # --- list and show: data, the name and the id on every step -------------------------------
    with K.case(bench, "list and show as data", "`list --json` returns the steps still to do, freshest "
                "first, each with its name and id; `--all` adds the closed ones; `--label` filters; an "
                "archived step is never listed; `show` returns one step whole") as check:
        K.said(keeper, "label", again, "+le-tri")
        names = [one["name"] for one in K.listed(keeper)]
        check(set(names) == {"un-pas-b", "un-pas-a"} and all(one["id"] for one in K.listed(keeper)), f"to do {names}")
        check({one["name"] for one in K.listed(keeper, "--all")} >= {"le-premier-pas", "un-pas-a", "un-pas-b"},
              "--all adds the closed")
        check([one["id"] for one in K.listed(keeper, "--label", "le-tri")] == [again], "--label filters")
        forged = K.record(root)
        forged["steps"][b]["archived"] = T1
        spool.write_text(json.dumps(forged, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        check(b not in [one["id"] for one in K.listed(keeper, "--all")], "an archived step is not listed")
        check(K.shown(keeper, b)["archived"] == T1, "show still reads it")
        text = K.said(keeper, "list")
        check(all(one["name"] in text and one["id"] in text for one in K.listed(keeper)), "the text names name and id")

    # --- the record: one shape, the thread model refused --------------------------------------
    with K.case(bench, "the record reads one shape", "load then save is byte-stable; a record that is not the "
                "steps with their counter refuses state-malformed; a `threads.json` standing without "
                "`steps.json` refuses state-unmigrated at every verb, nothing written") as check:
        before = spool.read_bytes()
        keeper.save(root, keeper.load(root))
        check(spool.read_bytes() == before, "the round-trip moved bytes")
        spool.write_text(json.dumps({"counters": {"s": 1, "f": 1}, "threads": {}, "steps": {}}), encoding="utf-8")
        bench.expect_exit("state-malformed", lambda: keeper.load(root))
        spool.write_bytes(before)
        other = bench.env("steering-legacy", ("steering",), pin=False).made
        legacy = other / ".sys" / "records" / "threads.json"
        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_text(json.dumps({"counters": {"s": 0, "f": 0}, "threads": {}, "steps": {}}), encoding="utf-8")
        later = load_script(K.script_of(other))
        for argv in (["list"], ["add", "un-pas", "x"]):
            bench.expect_exit("state-unmigrated", lambda argv=argv: later.main(argv))
        check(not K.spool(other).exists(), "no record born")

    with K.case(bench, "the thread verbs are gone", "attach, amend, move, status, data and verify answer the "
                "usage") as check:
        for gone in ("attach", "amend", "move", "status", "data", "verify", "close"):
            check(K.player(K.script_of(root), root.parent)(gone, "x").returncode == 2, f"{gone} still plays")

    return 0
