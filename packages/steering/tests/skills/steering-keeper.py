"""packages/steering/skills/pp-steering -- the keeper of the TWO DICTIONARIES, played in-process
on one instance: steps and threads each by an id without semantics, minted per series at the
member's counters, an owner on each; a thread LISTS ids in its order; done and amend written
once for every lister; the key verified through the engine and unique at the dictionary; a
crossing that opens its copy under the source's id and owner; a step that keeps the thread it
was born in (`thread`) and moves from one list to another unchanged, its text a complement
under the budget, its name what designates it; `worked_at` moved by the work alone; the
verifier of `steering-thread:` and the guardian's no at close; every guard proven red; the
budget read at the settings; the round-trip byte-stable; the former shapes refused."""
from __future__ import annotations

import contextlib
import io
import json
import sys

from conductor import events, instance
from tests.harness import load_script, support

K = support(__file__, "keeper")


def scenario(bench) -> int:
    root = bench.env("steering", ("steering",), pin=False).made
    threads = load_script(K.script_of(root))
    spool = root / ".sys" / "records" / "threads.json"
    member = root.resolve().parent.name          # what the ids carry for their uniqueness, what `owner` says

    def record() -> dict:
        return K.record(root)

    def thread(name: str) -> tuple[str, dict]:
        return next((tid, one) for tid, one in record()["threads"].items() if one["name"] == name)

    def fid(name: str) -> str:
        """-> the ID of the thread wearing a name: every verb but `open` takes the id."""
        return thread(name)[0]

    def closed_id(name: str) -> str:
        """-> the id of the latest closure wearing a name, read at the history."""
        return next(one["id"] for one in reversed(K.graves(root)) if one["name"] == name)

    def s(n: int) -> str:
        return f"{member}.s.{n}"

    def f(n: int) -> str:
        return f"{member}.f.{n}"

    def said(sid: str) -> tuple[str, str]:
        """-> (name, text) of a step, at the record."""
        step = record()["steps"][sid]
        return step["name"], step["text"]

    # --- the dictionaries: open, attach, the order, the ledger --------------------------------
    with K.case(bench, "open births the thread", "a thread id `<member>.f.1` and step ids `<member>.s.<n>` "
                "minted at the member's counters, each with its owner and the thread it was born in; the "
                "thread lists its steps in order, the next move on the first; the steps live at their own "
                "dictionary") as check:
        threads.open_thread(root, "le-fil-un", "premiere-etape-du-fil | premiere etape du fil\n"
                                               "seconde-etape-du-fil | seconde etape du fil\n")
        state = record()
        check(state["counters"] == {"s": 2, "f": 1} and list(state["threads"]) == [f(1)], f"counters {state['counters']}")
        one = state["threads"][f(1)]
        check(one["name"] == "le-fil-un" and one["owner"] == member, "the thread's name and owner")
        check(one["steps"] == [s(1), s(2)] and one["next"] == s(1), "the list and the next move")
        check(state["steps"] == {
            s(1): {"owner": member, "name": "premiere-etape-du-fil", "thread": f(1), "text": "premiere etape du fil", "status": "open"},
            s(2): {"owner": member, "name": "seconde-etape-du-fil", "thread": f(1), "text": "seconde etape du fil", "status": "open"}},
            "the step dictionary")

    with K.case(bench, "attach, reorder, renext live", "attach mints the id and lists it, reorder ranks the "
                "id in the list, the next move follows the word") as check:
        threads.attach(root, fid("le-fil-un"), "troisieme etape du fil", "troisieme-etape-du-fil")
        threads.reorder(root, fid("le-fil-un"), s(3), "1")
        threads.renext(root, fid("le-fil-un"), s(2))
        one = thread("le-fil-un")[1]
        check(one["steps"] == [s(3), s(1), s(2)] and one["next"] == s(2), f"list {one['steps']} next {one['next']}")
        check(record()["counters"]["s"] == 3, "the step counter")

    with K.case(bench, "rename, the ledger and the front", "the name changes, the id stays and the date of the "
                "work does not move; `--all` is the ledger (the arrow on the next move, the ids, the NAME of "
                "each step, the owner said); `status` is the front the NEXT pastes -- no id in it: one table "
                "row with the thread's bare name, its progress bar, its age and the NAME of its pointed step, "
                "no rank, no rest line, no text; every step carries the thread it was born in") as check:
        stamped = thread("le-fil-un")[1]["worked_at"]
        threads.rename(root, fid("le-fil-un"), "le-fil-renomme")
        block = K.ledger(threads.status(root, None, everything=True)).get("le-fil-renomme")
        check(block and (block.id, block.owner) == (f(1), member), "the ledger's head: name, id, owner")
        lines = block.steps if block else {}
        check(s(2) in lines and lines[s(2)].mark == "->" and (lines[s(2)].name, lines[s(2)].text) == said(s(2)),
              "the next move's line: arrow, name, text")
        check(s(3) in lines and lines[s(3)].mark == "" and (lines[s(3)].name, lines[s(3)].text) == said(s(3)),
              "an open step's line")
        shown = threads.status(root, None)
        seen = K.front(shown)
        check(seen.header == K.HEADER and "| threads | shipped |" not in shown, f"the header {seen.header}")
        row = seen.row("le-fil-renomme")
        check(len(seen.rows) == 1 and row and (row.flag, row.note, row.bar, row.done, row.total, row.redo, row.age)
              == ("", "—", "▱▱▱▱▱", 0, 3, 0, "now"), f"the row {row}")
        check(row and row.actions == [("seconde-etape-du-fil", ""), ("troisieme-etape-du-fil", ""),
                                      ("premiere-etape-du-fil", "")] and not row.more, "the actions by name")
        check("| #" not in shown and "le-fil-renomme :" not in shown and said(s(2))[1] not in shown,
              "no rank, no rest line, no text")
        check(".s." not in shown and ".f." not in shown, "no id at the front")
        tid, one = thread("le-fil-renomme")
        check(tid == f(1) and one["worked_at"] >= one["opened_at"] and one["worked_at"] == stamped,
              "the id and the date of the work kept")
        check(all(record()["steps"][x]["thread"] == f(1) for x in (s(1), s(2), s(3))), "the thread of birth")

    with K.case(bench, "done, amend and reopen", "a delivered step keeps its id and its rank, the pointer moves "
                "to the next open step, the text alone amends; pointed again, a delivered step reopens as "
                "`redo` -- counted apart, marked at the head -- and delivers again; a step is named by its id, "
                "never a rank") as check:
        threads.done(root, fid("le-fil-renomme"), s(2))
        state = record()
        check([state["steps"][x]["status"] for x in (s(3), s(1), s(2))] == ["open", "open", "done"], "the statuses")
        check(state["threads"][f(1)]["next"] == s(3), "the walk wraps")      # the chain is 3 1 2: after 2, 3
        threads.amend(root, fid("le-fil-renomme"), s(1), "premiere etape, dite autrement")
        lines = K.ledger(threads.status(root, None, everything=True))["le-fil-renomme"].steps
        check(lines[s(2)].mark == "✓" and (lines[s(2)].name, lines[s(2)].text) == said(s(2)), "the delivered line")
        check(lines[s(1)].text == said(s(1))[1] == "premiere etape, dite autrement", "the amended text")
        threads.renext(root, fid("le-fil-renomme"), s(2))                  # a delivered step pointed again REOPENS
        state = record()
        check(state["steps"][s(2)]["status"] == "redo" and state["threads"][f(1)]["next"] == s(2), "the reopening")
        row = K.front(threads.status(root, None)).row("le-fil-renomme")
        check(row and (row.bar, row.done, row.total, row.redo, row.age) == ("▱▱▱▱▱", 0, 3, 1, "now"),
              f"the progress counts the reopened apart {row}")
        check(row and row.actions == [("seconde-etape-du-fil", "🔄"), ("troisieme-etape-du-fil", ""),
                                      ("premiere-etape-du-fil", "")], "the reopened marked at the head")
        threads.done(root, fid("le-fil-renomme"), s(2))
        check(record()["steps"][s(2)]["status"] == "done", "delivered again")
        bench.expect_exit("step-unknown", lambda: threads.done(root, fid("le-fil-renomme"), s(9)))
        bench.expect_exit("step-invalid", lambda: threads.done(root, fid("le-fil-renomme"), "9"))

    with K.case(bench, "the round-trip is byte-stable", "load then save changes nothing -- no drift, no loss") as check:
        before = spool.read_bytes()
        threads.save(root, threads.load(root))
        check(spool.read_bytes() == before, "the bytes moved")

    with K.case(bench, "close ends the lifecycle", "the thread leaves the state with its ids to the history; "
                "the steps stay at the dictionary") as check:
        threads.close(root, fid("le-fil-renomme"))
        state = record()
        closed = K.graves(root)[-1]
        check(state["threads"] == {} and len(state["steps"]) == 3, "the state after the close")
        check(closed["name"] == "le-fil-renomme" and closed["id"] == f(1) and closed["owner"] == member, "the closure")
        check(closed["steps"] == [s(3), s(1), s(2)] and closed["opened_at"] and closed["closed_at"], "the closure's ids")

    with K.case(bench, "the refusals hold", "thread-taken, thread-unknown, step-invalid, step-unknown (an id "
                "the thread does not list), name-invalid, budget") as check:
        threads.open_thread(root, "le-fil-deux", "une-etape | une etape\n")
        bench.expect_exit("thread-taken", lambda: threads.open_thread(root, "le-fil-deux", "une-etape | une etape\n"))
        bench.expect_exit("thread-unknown", lambda: threads.attach(root, "le-fil-fantome", "une etape", "une-etape"))
        bench.expect_exit("step-invalid", lambda: threads.reorder(root, fid("le-fil-deux"), s(4), "9"))
        bench.expect_exit("step-unknown", lambda: threads.renext(root, fid("le-fil-deux"), s(1)))
        bench.expect_exit("name-invalid", lambda: threads.open_thread(root, "Pas_Kebab", "une-etape | une etape\n"))
        bench.expect_exit("budget", lambda: threads.attach(root, fid("le-fil-deux"), "x" * 101, "un-pas-trop-long"))
        bench.expect_exit("step-invalid", lambda: threads.open_thread(root, "le-fil-vide", ""))

    # --- the key: the work's vector, verified by its family, unique at the DICTIONARY ----------
    with K.case(bench, "the key holds the unicity at the dictionary", "a vector the family verifies, one step "
                "per key: step-taken in double wherever the second is minted, key-invalid off the grammar, the "
                "verifier's no relayed (vector-unverified, family-unknown); a work already keyed is LISTED by a "
                "braid, never minted again") as check:
        deux = f"steering-thread:{f(2)}"                         # le-fil-deux: the second thread minted here
        threads.attach(root, fid("le-fil-deux"), "un pas qui vise le fil deux", "un-pas-qui-vise", key=deux)
        check(record()["steps"][s(5)].get("key") == deux, "the key at the step")
        bench.expect_exit("step-taken", lambda: threads.attach(root, fid("le-fil-deux"), "le meme travail", "le-meme-travail", key=deux))
        bench.expect_exit("key-invalid", lambda: threads.attach(root, fid("le-fil-deux"), "sans famille", "sans-famille", key="pas-un-vecteur"))
        bench.expect_exit("vector-unverified", lambda: threads.attach(root, fid("le-fil-deux"), "un fil clos", "un-fil-clos", key=f"steering-thread:{f(1)}"))
        bench.expect_exit("family-unknown", lambda: threads.attach(root, fid("le-fil-deux"), "une famille de nulle part", "une-famille-de-nulle", key="zorg:x"))
        threads.open_thread(root, "le-fil-cle", "une-etape-libre | une etape libre\n")
        bench.expect_exit("step-taken", lambda: threads.open_thread(root, "le-fil-cle-bis", f"le-meme-travail-encore | {deux} | le meme travail encore\n"))
        check(record()["threads"][f(3)]["steps"] == [s(6)], "nothing minted by the refused open")

    # --- a crossing births its copy under the source's id and owner ----------------------------
    came = "[voisin] un pas venu d'ailleurs"
    with K.case(bench, "a crossing births its copy under the source's id and owner", "attach <thread id> "
                "--from --owner --name births the thread under that id, that owner and that name (the keeper "
                "derives nothing), the arrival minted HERE with its `from`, pointed; every step delivered "
                "leaves no next move, and the next arrival is pointed; a name where the id is due refuses; a "
                "source crosses once; --from without --owner refuses, and an id no thread carries without "
                "--name too") as check:
        threads.attach(root, "voisin.f.7", came, "le-pas-venu-du-voisin", source="voisin.s.4", owner="voisin",
                       born_as="le-fil-venu")
        state = record()
        venu = state["threads"]["voisin.f.7"]
        check(venu["name"] == "le-fil-venu" and venu["owner"] == "voisin" and venu["steps"] == [s(7)], "the copy's thread")
        check(state["steps"][s(7)] == {"owner": member, "name": "le-pas-venu-du-voisin", "thread": "voisin.f.7",
                                       "text": came, "status": "open", "from": "voisin.s.4"},
              "the arrival's record: the call's own name, text and source")
        check(venu["next"] == s(7) and state["counters"]["f"] == 3, "pointed, the id inherited, never minted")
        threads.done(root, fid("le-fil-venu"), s(7))
        check(record()["threads"]["voisin.f.7"]["next"] is None, "no next move once all is delivered")
        threads.attach(root, fid("le-fil-venu"), "la suite", "la-suite")
        check(record()["threads"]["voisin.f.7"]["next"] == s(8), "the next arrival pointed")
        bench.expect_exit("thread-unknown", lambda: threads.attach(root, "le-fil-jamais", "sans provenance", "sans-provenance"))
        bench.expect_exit("step-taken", lambda: threads.attach(root, "voisin.f.7", "[voisin] le meme pas venu deux fois", "le-meme-pas-deux-fois",
                                                              source="voisin.s.4", owner="voisin", born_as="le-fil-venu"))
        bench.expect_exit("step-invalid", lambda: threads.attach(root, "voisin.f.7", "[w] sans fil", "w-sans-fil", source="w.s.1"))
        bench.expect_exit("step-invalid", lambda: threads.attach(root, "w.f.2", "[w] sans nom de naissance",
                                                                 source="w.s.2", owner="w"))

    # --- the identity holds through a rename: a later crossing lands by id, never by name ------
    with K.case(bench, "the id survives the rename", "a renamed copy still receives the crossings of its id; "
                "a crossing whose id stands under no name refuses thread-taken when its name is another "
                "thread's; a key of the former shape is no id") as check:
        threads.rename(root, fid("le-fil-venu"), "le-fil-arrive")
        threads.attach(root, "voisin.f.7", "[voisin] la suite venue d'ailleurs", "voisin-la-suite-venue",
                       source="voisin.s.5", owner="voisin")
        state = record()
        check(state["threads"]["voisin.f.7"]["name"] == "le-fil-arrive"
              and state["threads"]["voisin.f.7"]["steps"] == [s(7), s(8), s(9)], "the crossing landed by id")
        check(state["steps"][s(9)]["from"] == "voisin.s.5", "its source")
        bench.expect_exit("thread-taken", lambda: threads.attach(root, "w.f.1", "[w] un autre fil du meme nom",
                                                                "w-un-autre-fil", source="w.s.1", owner="w",
                                                                born_as="le-fil-deux"))
        bench.expect_exit("step-invalid", lambda: threads.attach(root, "w.f.1", "[w] une cle d'avant", "w-une-cle-d",
                                                                 source="w#w-1#1", owner="w", born_as="le-fil-x"))

    # --- a crossing's text is cut to the budget, said -- the whole stays at its source ---------
    with K.case(bench, "a crossing's text is cut to the budget", "a copy born of a crossing keeps the "
                "neighbour's sentence up to the budget and says the cut -- the whole text stays readable at "
                "its source; the copy is born in the thread of the crossing") as check:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            threads.attach(root, "voisin.f.7", "[voisin] " + "y" * 150, "voisin-la-longue", source="voisin.s.6", owner="voisin")
        cut = record()["steps"][s(10)]
        check(len(cut["text"]) == 100 and cut["text"].startswith("[voisin] yyy") and cut["from"] == "voisin.s.6", "the cut text")
        check(cut["thread"] == "voisin.f.7" and "text cut to 100" in out.getvalue(), "the cut said, the thread of birth")

    with K.case(bench, "a chain past twenty steps stands", "no ceiling on the steps -- a thread is as long as "
                "its work") as check:
        threads.open_thread(root, "le-fil-long", "".join(f"etape-numero-{rank} | etape numero {rank}\n" for rank in range(1, 26)))
        threads.attach(root, fid("le-fil-long"), "la vingt-sixieme etape", "la-vingt-sixieme-etape")
        check(len(thread("le-fil-long")[1]["steps"]) == 26, "26 steps listed")
        check("le-fil-long" in K.ledger(threads.status(root, None, everything=True)), "the ledger shows it")

    # --- the text is a COMPLEMENT: optional, under the budget (100 by default) ------------------
    with K.case(bench, "the text is a complement", "100 characters pass at the default budget and 101 "
                "refuse, a blocking reason too; `attach` takes an empty text -- the name says the work") as check:
        threads.attach(root, fid("le-fil-long"), "x" * 100, "le-pas-a-cent")
        bench.expect_exit("budget", lambda: threads.attach(root, fid("le-fil-long"), "x" * 101, "le-pas-a-cent-un"))
        bench.expect_exit("budget", lambda: threads.block(root, fid("le-fil-long"), thread("le-fil-long")[1]["steps"][0], "x" * 101))
        dated = thread("le-fil-long")[1]["worked_at"]
        threads.attach(root, fid("le-fil-long"), "", "un-pas-sans-texte")
        check(record()["steps"][thread("le-fil-long")[1]["steps"][-1]]["text"] == "", "the empty text")
        check(thread("le-fil-long")[1]["worked_at"] > dated, "a step added is work")

    with K.case(bench, "the step budget is a setting", "steering_step_budget rules -- 40 passes, 41 refuses") as check:
        K.set_to(root, "steering_step_budget", 40)
        threads.attach(root, fid("le-fil-long"), "x" * 40, "le-pas-au-budget")
        check(record()["steps"][thread("le-fil-long")[1]["steps"][-1]]["name"] == "le-pas-au-budget", "40 passes")
        bench.expect_exit("budget", lambda: threads.attach(root, fid("le-fil-long"), "x" * 41, "le-pas-hors-budget"))

    # --- the verifier: `steering-thread:` is this package's family, an OPEN thread is a node ---
    @contextlib.contextmanager
    def fed(text: str):
        spot, sys.stdin = sys.stdin, io.StringIO(text)
        try:
            yield
        finally:
            sys.stdin = spot

    with K.case(bench, "the verifier answers for steering-thread:", "a vector names a thread's id: an open "
                "thread passes; a closed one, an unknown one refuse thread-unknown -- the keeper's own "
                "refusal; a foreign family refuses family-foreign; an argument says the usage -- read-only, "
                "the vector on stdin") as check:
        threads.open_thread(root, "le-fil-clos", "une-etape-qui-finit | une etape qui finit\n")
        threads.close(root, fid("le-fil-clos"))
        with fed(f"steering-thread:{f(4)}\n"):                   # le-fil-long
            check(threads.main(["verify"]) == 0, "an open thread passes")
        with fed(f"steering-thread:{f(5)}\n"):                   # le-fil-clos, closed
            bench.expect_exit("thread-unknown", lambda: threads.main(["verify"]))
        with fed("steering-thread:jamais.f.9\n"):
            bench.expect_exit("thread-unknown", lambda: threads.main(["verify"]))
        with fed("plan:piscine\n"):
            bench.expect_exit("family-foreign", lambda: threads.main(["verify"]))
        with contextlib.redirect_stdout(io.StringIO()):
            check(threads.main(["verify", "le-fil-long"]) == 2, "an argument: the usage, rc 2")

    with K.case(bench, "a closed thread drops from the serve", "the family is registered at the manifest "
                "(`verify: pp-steering`); the engine's service asks the record -- the open thread's line "
                "rides, through a rename, the closed ones' fall, no broom of their own") as check:
        latched = [{"source": "steering", "signal": "held-on", "vector": f"steering-thread:{f(4)}",
                    "sector": "protocol", "n": 1},
                   {"source": "steering", "signal": "held-on", "vector": f"steering-thread:{f(5)}",
                    "sector": "protocol", "n": 1}]
        served = [one["vector"] for one in events.standing(root, latched)]
        threads.rename(root, fid("le-fil-long"), "le-fil-tres-long")            # a rename keeps the line riding
        still = [one["vector"] for one in events.standing(root, latched)]
        threads.close(root, fid("le-fil-tres-long"))
        after = [one["vector"] for one in events.standing(root, latched)]
        check(served == [f"steering-thread:{f(4)}"] and still == served and after == [],
              f"served {served} {still} {after}")

    # --- a GUARDED close: the family's guardian says no ----------------------------------------
    with K.case(bench, "a guarded close relays the guardian's no", "the engine asks the family's guardian "
                "before the thread retires: a held thread stays with the reason, a free one closes, and "
                "without a guardian nothing is asked") as check:
        keeper = root / ".sys" / "vendor" / "keeper@0.0.1"
        keep = keeper / "skills" / "pp-keeper"
        keep.mkdir(parents=True)
        (keeper / "package.yaml").write_text("name: keeper\nversion: 0.0.1\ndescription: guards the threads it does not own\n"
                                             "requires: [steering]\ncontributes:\n  events:\n    vectors:\n"
                                             "      steering-thread: {guard: pp-keeper}\n", encoding="utf-8")
        (keep / "SKILL.md").write_text("---\nname: pp-keeper\ndescription: the keeper\n---\n\npp-keeper\n", encoding="utf-8")
        (keep / "pp-keeper.py").write_text("#!/usr/bin/env python3\nimport sys\nident = sys.stdin.read().strip().split(':', 1)[-1]\n"
                                           f"if ident == '{f(6)}':\n    print(f'pp-keeper: `{{ident}}` is still held by a neighbour', file=sys.stderr)\n"
                                           "    raise SystemExit(2)\nraise SystemExit(0)\n", encoding="utf-8")
        pins = instance.read(root)
        pins["packages"]["keeper"] = "0.0.1"
        instance.write(root, pins)
        threads.open_thread(root, "le-fil-tenu", "un-pas-que-le | un pas que le voisin tient encore\n")
        threads.open_thread(root, "le-fil-libre", "un-pas-a-nous | un pas a nous seuls\n")
        bench.expect_exit("thread-guarded", lambda: threads.close(root, fid("le-fil-tenu")))
        threads.close(root, fid("le-fil-libre"))
        names = [one["name"] for one in threads.load(root)["threads"].values()]
        check("le-fil-tenu" in names and "le-fil-libre" not in names, "the held stays, the free closes")
        del pins["packages"]["keeper"]
        instance.write(root, pins)
        threads.close(root, fid("le-fil-tenu"))
        check("le-fil-tenu" not in [one["name"] for one in record()["threads"].values()], "no guardian, no question")

    # --- the cycle completes: block, drop, move, amend --key, reopen, closed_as ----------------
    with K.case(bench, "block, drop and the marks", "a blocked step waits with its reason (the pointer moves "
                "on, the step and its reason at the ⏸ line) and renext releases it; a dropped step leaves the "
                "front and the counts, stays at --all (🗑️); done writes no date") as check:
        threads.open_thread(root, "le-fil-cycle", "premier-pas | premier pas\nsecond-pas | second pas\ntroisieme-pas | troisieme pas\n")
        c1, c2, c3 = thread("le-fil-cycle")[1]["steps"]
        dated = record()["threads"][fid("le-fil-cycle")]["worked_at"]
        threads.block(root, fid("le-fil-cycle"), c1, "attend la machine")
        state = record()
        check(state["threads"][fid("le-fil-cycle")]["worked_at"] > dated, "a block is work")
        check(state["steps"][c1]["status"] == "blocked" and state["steps"][c1]["reason"] == "attend la machine", "the reason kept")
        check(thread("le-fil-cycle")[1]["next"] == c2, "the pointer moves on")
        seen = K.front(threads.status(root, fid("le-fil-cycle")))
        row = seen.row("le-fil-cycle")
        check(row and (row.note, row.bar, row.done, row.total, row.age) == ("—", "▱▱▱▱▱", 0, 3, "now"), f"the row {row}")
        check(row and row.actions == [("second-pas", ""), ("troisieme-pas", "")], "the blocked step out of the actions")
        check(seen.waiting == [("le-fil-cycle", said(c1)[0], state["steps"][c1]["reason"])], f"the ⏸ line {seen.waiting}")
        threads.renext(root, fid("le-fil-cycle"), c1)
        state = record()
        check(state["steps"][c1]["status"] == "open" and "reason" not in state["steps"][c1]
              and thread("le-fil-cycle")[1]["next"] == c1, "renext releases")
        dated = record()["threads"][fid("le-fil-cycle")]["worked_at"]
        threads.drop(root, fid("le-fil-cycle"), c3)
        check(record()["threads"][fid("le-fil-cycle")]["worked_at"] > dated, "a drop is work")
        shown = threads.status(root, fid("le-fil-cycle"))
        row = K.front(shown).row("le-fil-cycle")
        check("troisieme" not in shown and row and (row.done, row.total) == (0, 2), "the dropped out of the front")
        line = K.ledger(threads.status(root, fid("le-fil-cycle"), everything=True))["le-fil-cycle"].steps.get(c3)
        check(line and line.mark == "🗑️" and (line.name, line.text) == said(c3), "the dropped at --all")
        threads.done(root, fid("le-fil-cycle"), c1)
        state = record()
        check(state["steps"][c1]["status"] == "done" and "done_at" not in state["steps"][c1], "done writes no date")
        check(thread("le-fil-cycle")[1]["next"] == c2, "the pointer after done")

    with K.case(bench, "amend poses, changes and removes a key", "--key after the fact, verified and unique at "
                "the dictionary; `-` takes it away; the text may change in the same call; nothing to amend "
                "refuses") as check:
        cycle_key = f"steering-thread:{fid('le-fil-cycle')}"
        threads.amend(root, fid("le-fil-cycle"), c2, None, key=cycle_key)
        check(record()["steps"][c2].get("key") == cycle_key, "the key posed")
        bench.expect_exit("step-taken", lambda: threads.attach(root, fid("le-fil-cycle"), "la meme cle", "la-meme-cle", key=cycle_key))
        threads.amend(root, fid("le-fil-cycle"), c2, "second pas, dit autrement", key="-")
        step2 = record()["steps"][c2]
        check("key" not in step2 and step2["text"] == "second pas, dit autrement", "the key removed, the text changed")
        bench.expect_exit("step-invalid", lambda: threads.amend(root, fid("le-fil-cycle"), c2, None, None))

    with K.case(bench, "a step moves and comes back unchanged", "`move` takes the step to the end of another "
                "thread and back; `thread` keeps where it was born, a crossed one included; the pointer "
                "follows the step") as check:
        threads.open_thread(root, "le-fil-cible", "un-pas-cible | un pas cible\n")
        born_in = record()["steps"][c2]
        with contextlib.redirect_stdout(io.StringIO()):
            check(threads.main(["move", fid("le-fil-cycle"), c2, fid("le-fil-cible")]) == 0, "move there")
        check(c2 not in thread("le-fil-cycle")[1]["steps"] and thread("le-fil-cible")[1]["steps"][-1] == c2, "the lists")
        check(thread("le-fil-cycle")[1]["next"] is None and record()["steps"][c2] == born_in, "the step unchanged")
        with contextlib.redirect_stdout(io.StringIO()):
            check(threads.main(["move", fid("le-fil-cible"), c2, fid("le-fil-cycle")]) == 0, "move back")
        threads.reorder(root, fid("le-fil-cycle"), c2, "2")
        check(thread("le-fil-cycle")[1]["steps"] == [c1, c2, c3] and thread("le-fil-cycle")[1]["next"] == c2, "back in place")
        check(record()["steps"][c2]["thread"] == fid("le-fil-cycle") and record()["steps"][s(9)]["thread"] == "voisin.f.7",
              "the thread of birth, a crossed one included")
        threads.done(root, fid("le-fil-cycle"), c2)

    with K.case(bench, "close says what it delivered, reopen brings a thread back", "closed_as delivered when "
                "every step of the dictionary it lists is done or dropped, dropped otherwise; reopen restores "
                "the id, the owner and the ids as they were, the history entry stays and says reopened_at; a "
                "name still open or never closed refuses") as check:
        threads.close(root, fid("le-fil-cycle"))
        closed = K.graves(root)[-1]
        check(closed["name"] == "le-fil-cycle" and closed["closed_as"] == "delivered" and closed["steps"] == [c1, c2, c3],
              "delivered")
        check(closed["worked_at"] >= closed["opened_at"] and "touched_at" not in closed, "the closure's dates")
        threads.open_thread(root, "le-fil-abandon", "un-pas-laisse-la | un pas laisse la\n")
        threads.close(root, fid("le-fil-abandon"))
        check(K.graves(root)[-1]["closed_as"] == "dropped", "dropped")
        threads.reopen(root, closed_id("le-fil-cycle"))
        tid, cycle = thread("le-fil-cycle")
        check(tid == closed["id"] and cycle["steps"] == [c1, c2, c3] and cycle["next"] is None
              and cycle["worked_at"] > closed["worked_at"], "the thread restored")
        check(any(one["name"] == "le-fil-cycle" and one.get("reopened_at") for one in K.graves(root)), "reopened_at")
        bench.expect_exit("thread-taken", lambda: threads.reopen(root, closed_id("le-fil-cycle")))
        bench.expect_exit("thread-unknown", lambda: threads.reopen(root, "jamais-clos"))

    with K.case(bench, "the date says the work", "`worked_at` moves with the work alone -- a step reordered, "
                "pointed again, delivered, blocked, dropped, added, a thread closed or reopened -- and never "
                "with an amend of the text, the name or the key, nor with a rename") as check:
        stable = record()["threads"][fid("le-fil-cycle")]["worked_at"]
        threads.amend(root, fid("le-fil-cycle"), c2, None, name="le-pas-renomme")
        check(record()["steps"][c2]["name"] == "le-pas-renomme", "the name amended")
        threads.amend(root, fid("le-fil-cycle"), c2, "le meme pas, dit autrement")
        threads.amend(root, fid("le-fil-cycle"), c2, None, key=f"steering-thread:{fid('le-fil-cycle')}")
        threads.rename(root, fid("le-fil-cycle"), "le-fil-cycle-bis")
        threads.rename(root, fid("le-fil-cycle-bis"), "le-fil-cycle")
        check(record()["threads"][fid("le-fil-cycle")]["worked_at"] == stable, "amend and rename leave the date")
        threads.reorder(root, fid("le-fil-cycle"), c2, "1")
        ranked = record()["threads"][fid("le-fil-cycle")]["worked_at"]
        check(ranked > stable, "a reorder is work")
        threads.renext(root, fid("le-fil-cycle"), c2)
        check(record()["threads"][fid("le-fil-cycle")]["worked_at"] > ranked, "a renext is work")

    # --- an id this dictionary does not hold is listed nowhere: a record carrying one is refused
    with K.case(bench, "an id the dictionary does not hold is refused at the read", "a braid too: a record "
                "whose open thread lists such an id, or that is a braid, refuses state-legacy at every read "
                "-- load, status, a write; a closure of the history listing one refuses state-legacy at "
                "reopen, nothing reopened; the record restored reads again") as check:
        kept_record = threads.load(root)
        deux_id = fid("le-fil-deux")
        former_listing = json.loads(json.dumps(kept_record))
        former_listing["threads"][deux_id]["steps"].append("voisin.s.2")
        threads.save(root, former_listing)
        bench.expect_exit("state-legacy", lambda: threads.load(root))
        bench.expect_exit("state-legacy", lambda: threads.status(root, None))
        bench.expect_exit("state-legacy", lambda: threads.done(root, deux_id, "voisin.s.2"))
        braided = json.loads(json.dumps(kept_record))
        braided["threads"][deux_id]["braid"] = True
        threads.save(root, braided)
        bench.expect_exit("state-legacy", lambda: threads.load(root))       # a braid is a former shape
        threads.save(root, kept_record)
        tombs = root / ".sys" / "records" / "threads-closed.jsonl"
        tombs_before = tombs.read_text(encoding="utf-8")
        tombs.write_text(tombs_before + json.dumps(
            {"id": f(99), "name": "le-fil-etranger", "owner": member, "steps": ["voisin.s.9"],
             "opened_at": "2026-09-01T00:00:00+00:00", "worked_at": "2026-09-01T00:00:00+00:00",
             "closed_at": "2026-09-02T00:00:00+00:00", "closed_as": "dropped"}) + "\n", encoding="utf-8")
        bench.expect_exit("state-legacy", lambda: threads.reopen(root, f(99)))
        check(f(99) not in record()["threads"], "nothing reopened")
        tombs.write_text(tombs_before, encoding="utf-8")
        check(deux_id in threads.load(root)["threads"], "the record restored reads")

    # --- the former shape of the record is refused ---------------------------------------------
    with K.case(bench, "the former shape is refused", "a record of a former shape -- threads keyed by name, "
                "steps inside them -- refuses state-legacy; the keeper guesses nothing") as check:
        former = bench.temp() / ".pp"
        (former / ".sys" / "records").mkdir(parents=True)
        keeper_of = former.resolve().parent.name
        (former / ".sys" / "records" / "threads.json").write_text(json.dumps(
            {"vieux": {"id": f"{keeper_of}-4", "steps": [{"id": f"{keeper_of}#{keeper_of}-4#1", "text": "a", "status": "done"},
                                                        {"id": f"{keeper_of}#{keeper_of}-4#2", "text": "b", "status": "open"},
                                                        {"from": f"{keeper_of}#{keeper_of}-4#1"}],
                       "next": f"{keeper_of}#{keeper_of}-4#2", "last": 2, "opened_at": "2026-09-01T00:00:00+00:00",
                       "touched_at": "2026-09-01T00:00:00+00:00"}}), encoding="utf-8")
        bench.expect_exit("state-legacy", lambda: threads.load(former))

    # --- the NAME of a step: what designates it while its text is prose ------------------------
    with K.case(bench, "a step wears a NAME", "the name designates the step while the text stays prose: a "
                "rewritten text leaves the name alone, `--as` renames without touching the id or the status, "
                "a step minted without a name refuses, a name that is not kebab-case refuses, a name already "
                "worn in THIS thread refuses -- and the same name lives freely in another thread") as check:
        threads.open_thread(root, "le-fil-nomme", "le-pas-nomme | un texte a reecrire\n")
        nomme = fid("le-fil-nomme")
        premier = record()["threads"][nomme]["steps"][0]
        check(record()["steps"][premier]["name"] == "le-pas-nomme", "the name minted")
        threads.amend(root, nomme, premier, "un tout autre texte")
        check(record()["steps"][premier]["name"] == "le-pas-nomme", "a rewritten text leaves the name")
        threads.amend(root, nomme, premier, None, name="le-pas-renomme")
        check(record()["steps"][premier]["name"] == "le-pas-renomme" and record()["steps"][premier]["status"] == "open",
              "renamed, the status kept")
        bench.expect_exit("step-invalid", lambda: threads.attach(root, nomme, "un pas sans nom"))
        bench.expect_exit("name-invalid", lambda: threads.attach(root, nomme, "un nom qui crie", "Le Pas"))
        bench.expect_exit("name-taken", lambda: threads.attach(root, nomme, "le meme nom", "le-pas-renomme"))
        bench.expect_exit("step-invalid", lambda: threads.open_thread(root, "le-fil-sans-nom", "un pas sans son nom\n"))
        threads.open_thread(root, "le-fil-homonyme", "le-pas-renomme | le meme nom ailleurs\n")
        check("le-fil-homonyme" in [one["name"] for one in record()["threads"].values()], "the same name elsewhere")

    # --- a step is born by its name alone: `<name>` and `<name> | <key>` at `open` ---------------
    with K.case(bench, "a step is born by its name alone", "`open` takes `<name>` and `<name> | <key>` as well "
                "as the forms with a text; the front's action cell says the name") as check:
        threads.open_thread(root, "le-fil-nu", f"un-pas-nu\nun-pas-cle | steering-thread:{nomme}\n")
        nu_tid = fid("le-fil-nu")
        nu_a, nu_b = record()["threads"][nu_tid]["steps"]
        check(record()["steps"][nu_a]["text"] == "" and record()["steps"][nu_b]["text"] == "", "no text")
        check(record()["steps"][nu_b].get("key") == f"steering-thread:{nomme}" and record()["steps"][nu_a]["thread"] == nu_tid,
              "the key and the thread of birth")
        row = K.front(threads.status(root, nu_tid)).row("le-fil-nu")
        check(row and row.actions == [("un-pas-nu", ""), ("un-pas-cle", "")], f"the action cell {row}")

    with K.case(bench, "the keeper reads one shape", "a step without a name or without its thread, a thread "
                "without `worked_at` refuse state-legacy; `unnamed` is no verb any more") as check:
        threads.attach(root, nomme, "le pas que la tete montrera", "le-second-du-fil")
        threads.renext(root, nomme, record()["threads"][nomme]["steps"][1])
        whole = record()
        for broken in ("name", "thread", "worked_at"):
            forged = json.loads(json.dumps(whole))
            if broken == "worked_at":
                forged["threads"][nomme]["touched_at"] = forged["threads"][nomme].pop("worked_at")
            else:
                forged["steps"][premier].pop(broken)
            spool.write_text(json.dumps(forged, indent=1, ensure_ascii=False), encoding="utf-8")
            bench.expect_exit("state-legacy", lambda: threads.load(root))
        spool.write_text(json.dumps(whole, indent=1, ensure_ascii=False), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            check(threads.main(["unnamed"]) == 2, "`unnamed` answers the usage")

    with K.case(bench, "a step stands in one open thread at most", "after every move of the case, no step is "
                "listed by two open threads, and each keeps the thread it was born in") as check:
        wrong = K.one_open_thread(root)
        check(not wrong, " ".join(wrong))

    return 0
