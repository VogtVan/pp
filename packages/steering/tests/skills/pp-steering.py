"""packages/steering/skills/pp-steering -- the full cycle lived on a real instance, on the TWO
DICTIONARIES: steps and threads each by an id without semantics, minted per series at the
member's counters, an owner on each; a thread HOSTS ids in the order of its list; done and
amend written once for every host; the key verified through the engine and unique at the
dictionary; a crossing that opens its copy under the source's id and owner; no braid any more
(0.6.0); a step that keeps the thread it was born in (`thread`) and moves from one list to
another unchanged, its text a complement under the budget, the thread's note, the thread's
`worked_at` moved by the work alone; the front of the moment without an id -- the note, up to
three actions, the ⏸ line, five rows before the footer -- the ledger with the ids and the
names, its open form served at boot; every guard proven red; the budgets read at the settings;
the round-trip byte-stable; the former shapes refused."""
from __future__ import annotations

import json
import os
import re

from conductor import instance, persistence
from tests.harness import SOURCE, load_script


def scenario(bench) -> int:
    root = bench.env("steering", ("steering",), pin=False).made
    # the VENDORED copy, not the source: the skill reaches the engine through its bootstrap,
    # and the bootstrap only finds one from inside an installed instance
    vendored = next((root / ".sys" / "vendor").glob("steering@*"))
    threads = load_script(vendored / "skills" / "pp-steering" / "pp-steering.py")
    spool = root / ".sys" / "records" / "threads.json"
    member = root.resolve().parent.name          # what the ids carry for their uniqueness, what `owner` says

    def record() -> dict:
        return json.loads(spool.read_text(encoding="utf-8"))

    def thread(name: str) -> tuple[str, dict]:
        return next((tid, one) for tid, one in record()["threads"].items() if one["name"] == name)

    def fid(name: str) -> str:
        """-> the ID of the thread wearing a name -- what every verb but `open` takes since
        la-mutation-par-id: the bench says the name it knows, the keeper is given the id."""
        return thread(name)[0]

    def closed_id(name: str) -> str:
        """-> the id of the latest closure wearing a name, read at the history."""
        graves = (root / ".sys" / "records" / "threads-closed.jsonl").read_text(encoding="utf-8").splitlines()
        return next(json.loads(one)["id"] for one in reversed(graves) if one.strip() and json.loads(one)["name"] == name)

    def s(n: int) -> str:
        return f"{member}.s.{n}"

    def f(n: int) -> str:
        return f"{member}.f.{n}"

    threads.open_thread(root, "le-fil-un", "premiere-etape-du-fil | premiere etape du fil\nseconde-etape-du-fil | seconde etape du fil\n")
    state = record()
    assert state["counters"] == {"s": 2, "f": 1} and list(state["threads"]) == [f(1)]
    assert state["threads"][f(1)]["name"] == "le-fil-un" and state["threads"][f(1)]["owner"] == member
    assert state["threads"][f(1)]["steps"] == [s(1), s(2)] and state["threads"][f(1)]["next"] == s(1)
    assert state["steps"] == {
        s(1): {"owner": member, "name": "premiere-etape-du-fil", "thread": f(1), "text": "premiere etape du fil", "status": "open"},
        s(2): {"owner": member, "name": "seconde-etape-du-fil", "thread": f(1), "text": "seconde etape du fil", "status": "open"}}
    bench.held("open births the thread", "a thread id `<member>.f.1` and step ids `<member>.s.<n>` minted at "
               "the member's counters, each with its owner and the thread it was born in; the thread lists "
               "its steps in order, the next move on the first; the steps live at their own dictionary")

    threads.attach(root, fid("le-fil-un"), "troisieme etape du fil", "troisieme-etape-du-fil")
    threads.reorder(root, fid("le-fil-un"), s(3), "1")
    threads.renext(root, fid("le-fil-un"), s(2))
    tid, one = thread("le-fil-un")
    assert one["steps"] == [s(3), s(1), s(2)] and one["next"] == s(2) and record()["counters"]["s"] == 3
    bench.held("attach, reorder, renext live", "attach mints the id and lists it, reorder ranks the id in the "
               "list, the next move follows the word")

    stamped = thread("le-fil-un")[1]["worked_at"]
    threads.rename(root, fid("le-fil-un"), "le-fil-renomme")
    render = threads.status(root, None, everything=True)
    assert f"~ le-fil-renomme [{f(1)}] ({member})" in render and f" -> {s(2)} seconde-etape-du-fil — seconde etape du fil" in render
    assert f"    {s(3)} troisieme-etape-du-fil — troisieme" in render
    front = threads.status(root, None)
    assert "| initiative | note | progress | age | next action(s) |" in front and "| threads | shipped |" not in front
    assert ("| le-fil-renomme | — | ▱▱▱▱▱ 0/3 | now | `seconde-etape-du-fil` · `troisieme-etape-du-fil` · "
            "`premiere-etape-du-fil` |") in front and "| #" not in front
    assert "le-fil-renomme :" not in front and "seconde etape du fil" not in front
    assert ".s." not in front and ".f." not in front
    tid, one = thread("le-fil-renomme")
    assert tid == f(1) and one["worked_at"] >= one["opened_at"] and one["worked_at"] == stamped
    assert all(record()["steps"][x]["thread"] == f(1) for x in (s(1), s(2), s(3)))
    bench.held("rename, the ledger and the front", "the name changes, the id stays and the date of the work "
               "does not move; `--all` is the ledger (the arrow on the next move, the ids, the NAME of each "
               "step, the owner said); `status` is the front the NEXT pastes -- no id in it: one table row "
               "with the thread's bare name, its progress bar, its age and the NAME of its pointed step, no "
               "rank, no rest line, no text; every step carries the thread it was born in")

    threads.done(root, fid("le-fil-renomme"), s(2))
    state = record()
    assert [state["steps"][x]["status"] for x in (s(3), s(1), s(2))] == ["open", "open", "done"]
    assert state["threads"][f(1)]["next"] == s(3)        # the chain is 3 1 2: after 2 the walk wraps to 3
    threads.amend(root, fid("le-fil-renomme"), s(1), "premiere etape, dite autrement")
    render = threads.status(root, None, everything=True)
    assert f" ✓  {s(2)} seconde-etape-du-fil — seconde etape du fil" in render and "premiere etape, dite autrement" in render
    threads.renext(root, fid("le-fil-renomme"), s(2))                       # a delivered step pointed again REOPENS
    state = record()
    assert state["steps"][s(2)]["status"] == "redo" and state["threads"][f(1)]["next"] == s(2)
    front = threads.status(root, None)
    assert "| le-fil-renomme | — | ▱▱▱▱▱ 0/3 🔄1 | now | `seconde-etape-du-fil`🔄 · `troisieme-etape-du-fil` · `premiere-etape-du-fil` |" in front
    threads.done(root, fid("le-fil-renomme"), s(2))
    assert record()["steps"][s(2)]["status"] == "done"
    bench.expect_exit("step-unknown", lambda: threads.done(root, fid("le-fil-renomme"), s(9)))
    bench.expect_exit("step-invalid", lambda: threads.done(root, fid("le-fil-renomme"), "9"))
    bench.held("done, amend and reopen", "a delivered step keeps its id and its rank, the pointer moves to the "
               "next open step, the text alone amends; pointed again, a delivered step reopens as `redo` -- "
               "counted apart, marked at the head -- and delivers again; a step is named by its id, never a rank")

    before = spool.read_bytes()
    threads.save(root, threads.load(root))
    assert spool.read_bytes() == before
    bench.held("the round-trip is byte-stable", "load then save changes nothing -- no drift, no loss")

    threads.close(root, fid("le-fil-renomme"))
    state = record()
    history = (root / ".sys" / "records" / "threads-closed.jsonl").read_text(encoding="utf-8")
    closed = json.loads(history.splitlines()[-1])
    assert state["threads"] == {} and len(state["steps"]) == 3
    assert closed["name"] == "le-fil-renomme" and closed["id"] == f(1) and closed["owner"] == member
    assert closed["steps"] == [s(3), s(1), s(2)] and closed["opened_at"] and closed["closed_at"]
    bench.held("close ends the lifecycle", "the thread leaves the state with its ids to the history; the steps "
               "stay at the dictionary")

    threads.open_thread(root, "le-fil-deux", "une-etape | une etape\n")
    bench.expect_exit("thread-taken", lambda: threads.open_thread(root, "le-fil-deux", "une-etape | une etape\n"))
    bench.expect_exit("thread-unknown", lambda: threads.attach(root, "le-fil-fantome", "une etape", "une-etape"))
    bench.expect_exit("step-invalid", lambda: threads.reorder(root, fid("le-fil-deux"), s(4), "9"))
    bench.expect_exit("step-unknown", lambda: threads.renext(root, fid("le-fil-deux"), s(1)))
    bench.expect_exit("name-invalid", lambda: threads.open_thread(root, "Pas_Kebab", "une-etape | une etape\n"))
    bench.expect_exit("budget", lambda: threads.attach(root, fid("le-fil-deux"), "x" * 101, "un-pas-trop-long"))
    bench.expect_exit("step-invalid", lambda: threads.open_thread(root, "le-fil-vide", ""))
    bench.held("the refusals hold", "thread-taken, thread-unknown, step-invalid, step-unknown (an id the thread "
               "does not list), name-invalid, budget")

    # --- the key: the work's vector, verified by its family, unique at the DICTIONARY ------
    deux = f"steering-thread:{f(2)}"                         # le-fil-deux: the second thread minted here
    threads.attach(root, fid("le-fil-deux"), "un pas qui vise le fil deux", "un-pas-qui-vise", key=deux)
    assert record()["steps"][s(5)]["key"] == deux
    bench.expect_exit("step-taken", lambda: threads.attach(root, fid("le-fil-deux"), "le meme travail", "le-meme-travail", key=deux))
    bench.expect_exit("key-invalid", lambda: threads.attach(root, fid("le-fil-deux"), "sans famille", "sans-famille", key="pas-un-vecteur"))
    bench.expect_exit("vector-unverified", lambda: threads.attach(root, fid("le-fil-deux"), "un fil clos", "un-fil-clos", key=f"steering-thread:{f(1)}"))
    bench.expect_exit("family-unknown", lambda: threads.attach(root, fid("le-fil-deux"), "une famille de nulle part", "une-famille-de-nulle", key="zorg:x"))
    threads.open_thread(root, "le-fil-cle", "une-etape-libre | une etape libre\n")
    bench.expect_exit("step-taken", lambda: threads.open_thread(root, "le-fil-cle-bis", f"le-meme-travail-encore | {deux} | le meme travail encore\n"))
    assert record()["threads"][f(3)]["steps"] == [s(6)]
    bench.held("the key holds the unicity at the dictionary", "a vector the family verifies, one step per key: "
               "step-taken in double wherever the second is minted, key-invalid off the grammar, the verifier's "
               "no relayed (vector-unverified, family-unknown); a work already keyed is LISTED by a braid, "
               "never minted again")

    # --- a crossing births its copy under the source's id and owner ------------------------
    threads.attach(root, "voisin.f.7", "[voisin] un pas venu d'ailleurs -- awaits the operator's GO",
                   "le-pas-venu-du-voisin", source="voisin.s.4", owner="voisin", born_as="le-fil-venu")
    state = record()
    venu = state["threads"]["voisin.f.7"]
    assert venu["name"] == "le-fil-venu" and venu["owner"] == "voisin" and venu["steps"] == [s(7)]
    assert state["steps"][s(7)] == {"owner": member, "name": "le-pas-venu-du-voisin", "thread": "voisin.f.7",
                                    "text": "[voisin] un pas venu d'ailleurs -- awaits the operator's GO",
                                    "status": "open", "from": "voisin.s.4"}
    assert venu["next"] == s(7) and state["counters"]["f"] == 3     # a copy's id is inherited, never minted
    threads.done(root, fid("le-fil-venu"), s(7))
    assert record()["threads"]["voisin.f.7"]["next"] is None
    threads.attach(root, fid("le-fil-venu"), "la suite", "la-suite")
    assert record()["threads"]["voisin.f.7"]["next"] == s(8)
    bench.expect_exit("thread-unknown", lambda: threads.attach(root, "le-fil-jamais", "sans provenance", "sans-provenance"))
    bench.expect_exit("step-taken", lambda: threads.attach(root, "voisin.f.7", "[voisin] le meme pas venu deux fois", "le-meme-pas-deux-fois",
                                                          source="voisin.s.4", owner="voisin", born_as="le-fil-venu"))
    bench.expect_exit("step-invalid", lambda: threads.attach(root, "voisin.f.7", "[w] sans fil", "w-sans-fil", source="w.s.1"))
    bench.expect_exit("step-invalid", lambda: threads.attach(root, "w.f.2", "[w] sans nom de naissance",
                                                             source="w.s.2", owner="w"))
    bench.held("a crossing births its copy under the source's id and owner", "attach <thread id> --from --owner "
               "--name births the thread under that id, that owner and that name (the keeper derives nothing), "
               "the arrival minted HERE with its `from`, pointed; every step delivered leaves no next move, and "
               "the next arrival is pointed; a name where the id is due refuses; a source crosses once; --from "
               "without --owner refuses, and an id no thread carries without --name too")

    # --- the identity holds through a rename: a later crossing lands by id, never by name ----
    threads.rename(root, fid("le-fil-venu"), "le-fil-arrive")
    threads.attach(root, "voisin.f.7", "[voisin] la suite venue d'ailleurs", "voisin-la-suite-venue", source="voisin.s.5", owner="voisin")
    state = record()
    assert state["threads"]["voisin.f.7"]["name"] == "le-fil-arrive" and state["threads"]["voisin.f.7"]["steps"] == [s(7), s(8), s(9)]
    assert state["steps"][s(9)]["from"] == "voisin.s.5"
    bench.expect_exit("thread-taken", lambda: threads.attach(root, "w.f.1", "[w] un autre fil du meme nom",
                                                            "w-un-autre-fil", source="w.s.1", owner="w",
                                                            born_as="le-fil-deux"))
    bench.expect_exit("step-invalid", lambda: threads.attach(root, "w.f.1", "[w] une cle d'avant", "w-une-cle-d", source="w#w-1#1", owner="w", born_as="le-fil-x"))
    bench.held("the id survives the rename", "a renamed copy still receives the crossings of its id; "
               "a crossing whose id stands under no name refuses thread-taken when its name is another "
               "thread's; a key of the former shape is no id")

    # --- a crossing's text is cut to the budget, said -- the whole stays at its source ---------
    import contextlib as _ctx, io as _io
    said = _io.StringIO()
    with _ctx.redirect_stdout(said):
        threads.attach(root, "voisin.f.7", "[voisin] " + "y" * 150, "voisin-la-longue", source="voisin.s.6", owner="voisin")
    cut = record()["steps"][s(10)]
    assert len(cut["text"]) == 100 and cut["text"].startswith("[voisin] yyy") and cut["from"] == "voisin.s.6"
    assert cut["thread"] == "voisin.f.7" and "text cut to 100" in said.getvalue()
    bench.held("a crossing's text is cut to the budget", "a copy born of a crossing keeps the neighbour's "
               "sentence up to the budget and says the cut -- the whole text stays readable at its source; "
               "the copy is born in the thread of the crossing")

    import subprocess, sys as _sys

    long_chain = "".join(f"etape-numero-{rank} | etape numero {rank}\n" for rank in range(1, 26))
    threads.open_thread(root, "le-fil-long", long_chain)
    threads.attach(root, fid("le-fil-long"), "la vingt-sixieme etape", "la-vingt-sixieme-etape")
    assert len(thread("le-fil-long")[1]["steps"]) == 26
    assert "~ le-fil-long" in threads.status(root, None, everything=True)
    bench.held("a chain past twenty steps stands", "no ceiling on the steps -- a thread is as long as its work")

    # --- the text is a COMPLEMENT: optional, under the budget (100 by default) ------------------
    threads.attach(root, fid("le-fil-long"), "x" * 100, "le-pas-a-cent")
    bench.expect_exit("budget", lambda: threads.attach(root, fid("le-fil-long"), "x" * 101, "le-pas-a-cent-un"))
    bench.expect_exit("budget", lambda: threads.block(root, fid("le-fil-long"), thread("le-fil-long")[1]["steps"][0], "x" * 101))
    dated = thread("le-fil-long")[1]["worked_at"]
    threads.attach(root, fid("le-fil-long"), "", "un-pas-sans-texte")
    assert record()["steps"][thread("le-fil-long")[1]["steps"][-1]]["text"] == ""
    assert thread("le-fil-long")[1]["worked_at"] > dated                                 # a step added is work
    bench.held("the text is a complement", "100 characters pass at the default budget and 101 refuse, a "
               "blocking reason too; `attach` takes an empty text -- the name says the work")

    settings = root / "SETTINGS.md"
    settings.write_text(re.sub(r"^steering_step_budget:.*$", "steering_step_budget: 40",
                               settings.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
    threads.attach(root, fid("le-fil-long"), "x" * 40, "le-pas-au-budget")
    bench.expect_exit("budget", lambda: threads.attach(root, fid("le-fil-long"), "x" * 41, "le-pas-hors-budget"))
    bench.held("the step budget is a setting", "steering_step_budget rules -- 40 passes, 41 refuses")

    card = (SOURCE / "packages" / "steering" / "skills" / "pp-steering" / "SKILL.md").read_text(encoding="utf-8")
    assert "only writer of `.sys/records/threads.json`" in card and "trivial" not in card.lower()
    assert "worked_at" in card and "touched_at" not in card and "move <thread id>" in card and "unnamed" not in card
    assert all(gone not in card for gone in ("done_at", "never leaves the thread it was born in", "No verb changes it",
                                             "stays in it"))
    assert all(gone not in card for gone in ("open --braid", "🪢", "refer <", "unlist <", "thread-braid",
                                             "thread-not-braid", "braid-thin", "dissolved", "step-last-host"))
    assert all(said in card for said in ("--bare", '"closed"', "note <thread id>", "--note", "steering_note_budget",
                                         "steering_next_max", "steering_line_max", "steering_front_min",
                                         "--all [--open]", "steering-ledger", "⏸"))
    assert "open_steps" not in card
    assert all(word in card for word in ("threads-seen.json", "status --due", threads.NOT_CHANGED))
    assert "context-no-run" not in card and "Open the turn" not in card
    bench.held("the card says what the script IS", "the one writer of the record, its verbs and "
               "their refusals, the note, the front and the ledger the boot serves -- no braid left; who decides "
               "a gesture is NEXT's word, not the card's")

    # --- the verifier: `steering-thread:` is this package's family, an OPEN thread is a node --
    import contextlib, io, sys
    from conductor import events

    @contextlib.contextmanager
    def fed(text: str):
        spot, sys.stdin = sys.stdin, io.StringIO(text)
        try:
            yield
        finally:
            sys.stdin = spot

    threads.open_thread(root, "le-fil-clos", "une-etape-qui-finit | une etape qui finit\n")
    threads.close(root, fid("le-fil-clos"))
    with fed(f"steering-thread:{f(4)}\n"):                   # le-fil-long
        assert threads.main(["verify"]) == 0
    with fed(f"steering-thread:{f(5)}\n"):                   # le-fil-clos, closed
        bench.expect_exit("thread-unknown", lambda: threads.main(["verify"]))
    with fed("steering-thread:jamais.f.9\n"):
        bench.expect_exit("thread-unknown", lambda: threads.main(["verify"]))
    with fed("plan:piscine\n"):
        bench.expect_exit("family-foreign", lambda: threads.main(["verify"]))
    assert threads.main(["verify", "le-fil-long"]) == 2          # an argument: the usage, rc 2
    bench.held("the verifier answers for steering-thread:", "a vector names a thread's id: an open thread "
               "passes; a closed one, an unknown one refuse thread-unknown -- the keeper's own refusal; "
               "a foreign family refuses family-foreign; an argument says the usage -- read-only, the "
               "vector on stdin")

    latched = [{"source": "steering", "signal": "held-on", "vector": f"steering-thread:{f(4)}",
                "sector": "protocol", "n": 1},
               {"source": "steering", "signal": "held-on", "vector": f"steering-thread:{f(5)}",
                "sector": "protocol", "n": 1}]
    served = [one["vector"] for one in events.standing(root, latched)]
    threads.rename(root, fid("le-fil-long"), "le-fil-tres-long")            # a rename keeps the line riding
    still = [one["vector"] for one in events.standing(root, latched)]
    threads.close(root, fid("le-fil-tres-long"))
    served_after = [one["vector"] for one in events.standing(root, latched)]
    if served == [f"steering-thread:{f(4)}"] and still == served and served_after == []:
        bench.held("a closed thread drops from the serve", "the family is registered at the "
                   "manifest (`verify: pp-steering`); the engine's service asks the record -- the "
                   "open thread's line rides, through a rename, the closed ones' fall, no broom of their own")
    else:
        bench.failures.append(f"  ✗ closed thread at the service {served} {served_after}")

    # --- a GUARDED close (batch le-gardien-declare): the family's guardian says no ---------
    keeper = root / ".sys" / "vendor" / "keeper@0.0.1"
    keep = keeper / "skills" / "pp-keeper"
    keep.mkdir(parents=True)
    (keeper / "package.yaml").write_text("name: keeper\nversion: 0.0.1\ndescription: guards the threads it does not own\n"
                                         "requires: [steering]\ncontributes:\n  events:\n    vectors:\n      steering-thread: {guard: pp-keeper}\n", encoding="utf-8")
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
    assert "le-fil-tenu" in names and "le-fil-libre" not in names
    del pins["packages"]["keeper"]
    instance.write(root, pins)
    threads.close(root, fid("le-fil-tenu"))
    bench.held("a guarded close relays the guardian's no", "the engine asks the family's guardian "
               "before the thread retires: a held thread stays with the reason, a free one closes, "
               "and without a guardian nothing is asked")

    # --- the front: freshest first, the flags, the icons, no id -- the ledger on demand -------
    threads.open_thread(root, "le-fil-fini", "une-etape-vite-faite | une etape vite faite\n")
    fini = thread("le-fil-fini")[1]["steps"][0]
    threads.done(root, fid("le-fil-fini"), fini)
    threads.open_thread(root, "le-fil-adresse", "voisin-dis-moi-ce | @voisin dis-moi ce que tu vois\n")
    threads.attach(root, fid("le-fil-deux"), "un pas de plus", "un-pas-de-plus")   # under the 40-char budget set above
    front = threads.status(root, None)
    rows = [line for line in front.splitlines() if line.startswith("| ") and not line.startswith("| initiative |")]
    assert rows[0].startswith("| le-fil-deux | — | ▱▱▱▱▱ 0/3 |") and rows[1].startswith("| le-fil-adresse | — | ▱▱▱▱▱ 0/1 |")
    assert "le-fil-fini" not in front                                     # nothing to do: no row (KFM14)
    assert "| 🔗 le-fil-arrive | — | ▰▱▱▱▱ 1/4 | " in front and "`la-suite`" in front
    assert "| `voisin-dis-moi-ce`✉️ |" in front
    assert "| #" not in front and "@voisin" not in front                 # 📥 marks a received step among the actions
    assert ".s." not in front and ".f." not in front and "[" not in front
    assert threads.main(["status", "--all"]) == 0 and threads.main(["status", fid("le-fil-deux"), "--all"]) == 0
    bench.expect_exit("thread-addressed-by-name", lambda: threads.main(["status", "le-fil-deux"]))
    bench.expect_exit("thread-addressed-by-name", lambda: threads.done(root, "le-fil-deux", fini))
    bench.held("the front is the keeper's, without an id", "the table freshest first (the last written thread "
               "first), no rank, every thread with a step to do on its row with its flag and bare name, its note "
               "or `—`, its five-cell bar and delivered/total, its age and its next actions with their marks "
               "(🔄 reopened, 📥 crossed in, ✉️ addressed), 🔗 for a thread another member owns; a thread with "
               "nothing to do has no row; no text, no key, no id -- the "
               "operator reads work, the agent reads ids and keys at `--all`; a NAME given to any verb but "
               "`open` refuses thread-addressed-by-name, naming the id it labels")

    # --- the cycle completes: block, drop, move, amend --key, reopen, closed_as, dormant
    from datetime import datetime as _dt, timedelta as _td, timezone as _tz
    threads.open_thread(root, "le-fil-cycle", "premier-pas | premier pas\nsecond-pas | second pas\ntroisieme-pas | troisieme pas\n")
    c1, c2, c3 = thread("le-fil-cycle")[1]["steps"]
    dated = record()["threads"][fid("le-fil-cycle")]["worked_at"]
    threads.block(root, fid("le-fil-cycle"), c1, "attend la machine")
    state = record()
    assert state["threads"][fid("le-fil-cycle")]["worked_at"] > dated            # a block is work
    assert state["steps"][c1]["status"] == "blocked" and state["steps"][c1]["reason"] == "attend la machine"
    assert thread("le-fil-cycle")[1]["next"] == c2
    front = threads.status(root, fid("le-fil-cycle"))
    assert "| le-fil-cycle | — | ▱▱▱▱▱ 0/3 | now | `second-pas` · `troisieme-pas` |" in front
    assert "⏸ le-fil-cycle › `premier-pas` (attend la machine)" in front
    threads.renext(root, fid("le-fil-cycle"), c1)
    state = record()
    assert state["steps"][c1]["status"] == "open" and "reason" not in state["steps"][c1] and thread("le-fil-cycle")[1]["next"] == c1
    dated = record()["threads"][fid("le-fil-cycle")]["worked_at"]
    threads.drop(root, fid("le-fil-cycle"), c3)
    assert record()["threads"][fid("le-fil-cycle")]["worked_at"] > dated          # a drop is work
    front = threads.status(root, fid("le-fil-cycle"))
    assert "troisieme" not in front and "| le-fil-cycle | — | ▱▱▱▱▱ 0/2 |" in front and f"🗑️ {c3} troisieme-pas — troisieme pas" in threads.status(root, fid("le-fil-cycle"), everything=True)
    threads.done(root, fid("le-fil-cycle"), c1)
    state = record()
    assert state["steps"][c1]["status"] == "done" and "done_at" not in state["steps"][c1]
    assert thread("le-fil-cycle")[1]["next"] == c2
    bench.held("block, drop and the marks", "a blocked step waits with its reason (the pointer moves on, "
               "the step and its reason at the ⏸ line) and renext releases it; a dropped step leaves the front "
               "and the counts, stays at --all (🗑️); done writes no date")

    cycle_key = f"steering-thread:{thread('le-fil-cycle')[0]}"
    threads.amend(root, fid("le-fil-cycle"), c2, None, key=cycle_key)
    assert record()["steps"][c2]["key"] == cycle_key
    bench.expect_exit("step-taken", lambda: threads.attach(root, fid("le-fil-cycle"), "la meme cle", "la-meme-cle", key=cycle_key))
    threads.amend(root, fid("le-fil-cycle"), c2, "second pas, dit autrement", key="-")
    step2 = record()["steps"][c2]
    assert "key" not in step2 and step2["text"] == "second pas, dit autrement"
    bench.expect_exit("step-invalid", lambda: threads.amend(root, fid("le-fil-cycle"), c2, None, None))
    bench.held("amend poses, changes and removes a key", "--key after the fact, verified and unique at the "
               "dictionary; `-` takes it away; the text may change in the same call; nothing to amend refuses")

    threads.open_thread(root, "le-fil-cible", "un-pas-cible | un pas cible\n")
    born_in = record()["steps"][c2]
    assert threads.main(["move", fid("le-fil-cycle"), c2, fid("le-fil-cible")]) == 0
    assert c2 not in thread("le-fil-cycle")[1]["steps"] and thread("le-fil-cible")[1]["steps"][-1] == c2
    assert thread("le-fil-cycle")[1]["next"] is None and record()["steps"][c2] == born_in
    assert threads.main(["move", fid("le-fil-cible"), c2, fid("le-fil-cycle")]) == 0
    threads.reorder(root, fid("le-fil-cycle"), c2, "2")
    assert thread("le-fil-cycle")[1]["steps"] == [c1, c2, c3] and thread("le-fil-cycle")[1]["next"] == c2
    assert record()["steps"][c2]["thread"] == fid("le-fil-cycle") and record()["steps"][s(9)]["thread"] == "voisin.f.7"
    bench.held("a step moves and comes back unchanged", "`move` takes the step to the end of another thread and "
               "back; `thread` keeps where it was born, a crossed one included; the pointer follows the step")
    threads.done(root, fid("le-fil-cycle"), c2)

    threads.close(root, fid("le-fil-cycle"))
    closed = json.loads((root / ".sys" / "records" / "threads-closed.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert closed["name"] == "le-fil-cycle" and closed["closed_as"] == "delivered" and closed["steps"] == [c1, c2, c3]
    assert closed["worked_at"] >= closed["opened_at"] and "touched_at" not in closed
    threads.open_thread(root, "le-fil-abandon", "un-pas-laisse-la | un pas laisse la\n")
    threads.close(root, fid("le-fil-abandon"))
    left = json.loads((root / ".sys" / "records" / "threads-closed.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert left["closed_as"] == "dropped"
    threads.reopen(root, closed_id("le-fil-cycle"))
    tid, cycle = thread("le-fil-cycle")
    assert tid == closed["id"] and cycle["steps"] == [c1, c2, c3] and cycle["next"] is None and cycle["worked_at"] > closed["worked_at"]
    graves = [json.loads(l) for l in (root / ".sys" / "records" / "threads-closed.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    assert any(one["name"] == "le-fil-cycle" and one.get("reopened_at") for one in graves)
    bench.expect_exit("thread-taken", lambda: threads.reopen(root, closed_id("le-fil-cycle")))
    bench.expect_exit("thread-unknown", lambda: threads.reopen(root, "jamais-clos"))
    bench.held("close says what it delivered, reopen brings a thread back", "closed_as delivered when every "
               "step of the dictionary it lists is done or dropped, dropped otherwise; reopen restores the id, "
               "the owner and the ids as they were, the history entry stays and says reopened_at; a name "
               "still open or never closed refuses")

    later = _dt.now(_tz.utc) + _td(days=8)
    live = [tid for tid, one in record()["threads"].items()
            if any(record()["steps"][sid]["status"] in ("open", "redo") for sid in one["steps"])]
    every = threads.front(root, threads.load(root), now=later)
    table_rows = [line for line in every.splitlines() if line.startswith("| ") and not line.startswith("| initiative |")]
    assert len(table_rows) == min(5, len(live)) and ("💤 " in every) == (len(live) > 5), (len(live), every)
    awake = threads.front(root, threads.load(root))
    assert "💤" not in awake
    settings.write_text(re.sub(r"^steering_front_min:.*$", "steering_front_min: 0",
                               settings.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
    every = threads.front(root, threads.load(root), now=later)
    assert "| initiative |" not in every and "\n💤 " in "\n" + every.split("\n\n")[-1] and "older than" not in every
    kept = record()["threads"][fid("le-fil-deux")]["worked_at"]
    ahead = threads.load(root)
    ahead["threads"][fid("le-fil-deux")]["worked_at"] = later.isoformat(timespec="microseconds")
    threads.save(root, ahead)
    mixed = threads.front(root, threads.load(root), now=later)
    last = mixed.rsplit("\n", 1)[1]
    assert last.startswith("💤 ") and " · " in last and "le-fil-cible `un-pas-cible` (1 week)" in last
    assert "| le-fil-deux | — | ▱▱▱▱▱ 0/3 | now |" in mixed and "| le-fil-cible |" not in mixed
    back = threads.load(root)
    back["threads"][fid("le-fil-deux")]["worked_at"] = kept
    threads.save(root, back)
    settings.write_text(re.sub(r"^steering_front_min:.*$", "steering_front_min: 5",
                               settings.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
    bench.held("a thread nobody wrote for the cut FOLDS to the footer, past the rows kept", "past "
               "steering_dormant_days (7 by default, read at worked_at) a thread may leave the table for the footer "
               "-- one line after 💤, its name, its pointed step fenced and its age -- but the table keeps the "
               "steering_front_min freshest rows first (5): every thread dormant, the table still shows five, or all "
               "of them when fewer; at 0 the table empties to the footer as before")

    stable = record()["threads"][fid("le-fil-cycle")]["worked_at"]
    threads.amend(root, fid("le-fil-cycle"), c2, None, name="le-pas-renomme")
    assert record()["steps"][c2]["name"] == "le-pas-renomme"
    threads.amend(root, fid("le-fil-cycle"), c2, "le meme pas, dit autrement")
    threads.amend(root, fid("le-fil-cycle"), c2, None, key=f"steering-thread:{fid('le-fil-cycle')}")
    threads.rename(root, fid("le-fil-cycle"), "le-fil-cycle-bis")
    threads.rename(root, fid("le-fil-cycle-bis"), "le-fil-cycle")
    assert record()["threads"][fid("le-fil-cycle")]["worked_at"] == stable
    threads.reorder(root, fid("le-fil-cycle"), c2, "1")
    ranked = record()["threads"][fid("le-fil-cycle")]["worked_at"]
    assert ranked > stable
    threads.renext(root, fid("le-fil-cycle"), c2)
    assert record()["threads"][fid("le-fil-cycle")]["worked_at"] > ranked
    bench.held("the date says the work", "`worked_at` moves with the work alone -- a step reordered, "
               "pointed again, delivered, blocked, dropped, added, a thread closed or reopened -- and never "
               "with an amend of the text, the name or the key, nor with a rename")
    at = _dt(2026, 9, 6, 12, 0, 0, tzinfo=_tz.utc)
    def since(**delta):
        return threads.ago((at - _td(**delta)).isoformat(timespec="microseconds"), at)
    assert since(seconds=30) == "now" and since(minutes=12) == "12 min" and since(minutes=95) == "1h 35 min"
    assert since(hours=3) == "3h" and since(hours=24, minutes=56, seconds=12) == "> 1 day" and since(days=3) == "3 days"
    assert since(days=10) == "1 week" and since(days=20) == "2 weeks" and since(days=100) == "~3 months"
    assert since(days=505) == "~1.4 years" and threads.ago("not-a-stamp", at) == "not-a-stamp"
    assert "| now |" in threads.status(root, fid("le-fil-deux"))
    bench.held("the age is the time elapsed", "now, minutes, hours and minutes, > 1 day, days, weeks, "
               "~months, ~years -- the coarsest unit that still says it; a fresh thread says now")

    # --- an id this dictionary does not hold is listed nowhere: a record carrying one is refused ----
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
    bench.expect_exit("state-legacy", lambda: threads.load(root))       # a braid is a former shape (0.6.0)
    threads.save(root, kept_record)
    graves = root / ".sys" / "records" / "threads-closed.jsonl"
    tombs_before = graves.read_text(encoding="utf-8")
    graves.write_text(tombs_before + json.dumps(
        {"id": f(99), "name": "le-fil-etranger", "owner": member, "steps": ["voisin.s.9"],
         "opened_at": "2026-09-01T00:00:00+00:00", "worked_at": "2026-09-01T00:00:00+00:00",
         "closed_at": "2026-09-02T00:00:00+00:00", "closed_as": "dropped"}) + "\n", encoding="utf-8")
    bench.expect_exit("state-legacy", lambda: threads.reopen(root, f(99)))
    assert f(99) not in record()["threads"]
    graves.write_text(tombs_before, encoding="utf-8")
    bench.held("an id the dictionary does not hold is refused at the read", "a braid too: a "
               "record whose open thread lists such an id, or that is a braid, refuses state-legacy at every read -- load, status, "
               "a write; a closure of the history listing one refuses state-legacy at "
               "reopen, nothing reopened; the record restored reads again")

    # --- the former shape of the record is refused -------------------------------------------
    former = bench.temp() / ".pp"
    (former / ".sys" / "records").mkdir(parents=True)
    keeper_of = former.resolve().parent.name
    (former / ".sys" / "records" / "threads.json").write_text(json.dumps(
        {"vieux": {"id": f"{keeper_of}-4", "steps": [{"id": f"{keeper_of}#{keeper_of}-4#1", "text": "a", "status": "done"},
                                                    {"id": f"{keeper_of}#{keeper_of}-4#2", "text": "b", "status": "open"},
                                                    {"from": f"{keeper_of}#{keeper_of}-4#1"}],
                   "next": f"{keeper_of}#{keeper_of}-4#2", "last": 2, "opened_at": "2026-09-01T00:00:00+00:00", "touched_at": "2026-09-01T00:00:00+00:00"}}), encoding="utf-8")
    bench.expect_exit("state-legacy", lambda: threads.load(former))
    bench.held("the former shape is refused", "a record of a former shape -- threads keyed by name, steps inside them -- refuses state-legacy; the keeper guesses nothing")
    # --- le NOM d'un pas : ce qui le designe quand son texte est de la prose -----------------
    threads.open_thread(root, "le-fil-nomme", "le-pas-nomme | un texte a reecrire\n")
    nomme = fid("le-fil-nomme")
    premier = record()["threads"][nomme]["steps"][0]
    assert record()["steps"][premier]["name"] == "le-pas-nomme"
    threads.amend(root, nomme, premier, "un tout autre texte")
    assert record()["steps"][premier]["name"] == "le-pas-nomme"
    threads.amend(root, nomme, premier, None, name="le-pas-renomme")
    assert record()["steps"][premier]["name"] == "le-pas-renomme" and record()["steps"][premier]["status"] == "open"
    bench.expect_exit("step-invalid", lambda: threads.attach(root, nomme, "un pas sans nom"))
    bench.expect_exit("name-invalid", lambda: threads.attach(root, nomme, "un nom qui crie", "Le Pas"))
    bench.expect_exit("name-taken", lambda: threads.attach(root, nomme, "le meme nom", "le-pas-renomme"))
    bench.expect_exit("step-invalid", lambda: threads.open_thread(root, "le-fil-sans-nom", "un pas sans son nom\n"))
    threads.open_thread(root, "le-fil-homonyme", "le-pas-renomme | le meme nom ailleurs\n")
    bench.held("a step wears a NAME", "the name designates the step while the text stays prose: a rewritten "
               "text leaves the name alone, `--as` renames without touching the id or the status, a step "
               "minted without a name refuses, a name that is not kebab-case refuses, a name already worn in "
               "THIS thread refuses -- and the same name lives freely in another thread")

    # --- a step is born by its name alone: `<name>` and `<name> | <key>` at `open` ---------------
    threads.open_thread(root, "le-fil-nu", f"un-pas-nu\nun-pas-cle | steering-thread:{nomme}\n")
    nu_tid = fid("le-fil-nu")
    nu_a, nu_b = record()["threads"][nu_tid]["steps"]
    assert record()["steps"][nu_a]["text"] == "" and record()["steps"][nu_b]["text"] == ""
    assert record()["steps"][nu_b]["key"] == f"steering-thread:{nomme}" and record()["steps"][nu_a]["thread"] == nu_tid
    assert "| `un-pas-nu` · `un-pas-cle` |" in threads.status(root, nu_tid)
    bench.held("a step is born by its name alone", "`open` takes `<name>` and `<name> | <key>` as well as "
               "the forms with a text; the front's action cell says the name")

    threads.attach(root, nomme, "le pas que la tete montrera", "le-second-du-fil")
    threads.renext(root, nomme, record()["threads"][nomme]["steps"][1])
    whole = record()
    for broken in ("name", "thread", "worked_at"):
        forged = json.loads(json.dumps(whole))
        if broken == "worked_at":
            forged["threads"][nomme]["touched_at"] = forged["threads"][nomme].pop("worked_at")
        else:
            forged["steps"][premier].pop(broken)
        (root / ".sys" / "records" / "threads.json").write_text(json.dumps(forged, indent=1, ensure_ascii=False),
                                                               encoding="utf-8")
        bench.expect_exit("state-legacy", lambda: threads.load(root))
    (root / ".sys" / "records" / "threads.json").write_text(json.dumps(whole, indent=1, ensure_ascii=False),
                                                           encoding="utf-8")
    assert threads.main(["unnamed"]) == 2
    bench.held("the keeper reads one shape", "a step without a name or without its thread, a thread without "
               "`worked_at` refuse state-legacy; `unnamed` is no verb any more")

    # --- `data`: the member's open threads as DATA, read through the vendored script ----------
    import hashlib
    from conductor import install
    from tests.harness import PRODUCT_ENGINE
    town = bench.temp()
    for name in ("alpha", "beta"):
        install.install(PRODUCT_ENGINE, town / name / ".pp", ["steering"])
    alpha = town / "alpha" / ".pp"
    script = next((alpha / ".sys" / "vendor").glob("steering@*")) / "skills" / "pp-steering" / "pp-steering.py"

    def play(*args: str, stdin: str = "", cwd: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([_sys.executable, str(script), *args], input=stdin, capture_output=True,
                              text=True, cwd=str(cwd or alpha.parent))

    play("open", "le-fil-vif", stdin="un-pas-livre | un pas livre\nun-pas-laisse | un pas laisse\n"
                                   "un-pas-rouvert | un pas rouvert\nun-pas-en-attente | un pas en attente\n"
                                   "un-pas-ouvert | un pas ouvert\n")
    play("open", "le-fil-mort", stdin="un-pas-du-fil-mort | un pas du fil mort\n")
    ledger = json.loads((alpha / ".sys" / "records" / "threads.json").read_text(encoding="utf-8"))
    vif = next(tid for tid, one in ledger["threads"].items() if one["name"] == "le-fil-vif")
    mort = next(tid for tid, one in ledger["threads"].items() if one["name"] == "le-fil-mort")
    livre, laisse, rouvert, attente, ouvert = ledger["threads"][vif]["steps"]
    play("done", vif, livre)
    play("drop", vif, laisse)
    play("done", vif, rouvert)
    play("renext", vif, rouvert)
    play("block", vif, attente, "attend la machine")
    play("close", mort)
    play("reopen", mort)
    assert json.loads(play("data").stdout)["closed"] == []          # a reopened thread is open, not closed
    play("close", mort)
    records = alpha / ".sys" / "records"
    prints = {one.name: hashlib.sha256(one.read_bytes()).hexdigest() for one in records.glob("threads*")}

    served = play("data", cwd=town / "beta")                     # from ANOTHER member's directory
    seen = json.loads(served.stdout)
    [one] = seen["threads"]
    ids = [step["id"] for step in one["steps"]]
    front = subprocess.run([_sys.executable, str(script), "status", vif], capture_output=True, text=True).stdout
    assert served.returncode == 0 and seen["version"] == 3 and seen["member"] == "alpha"
    assert one["id"] == vif and one["name"] == "le-fil-vif" and one["owner"] == "alpha" and mort not in json.dumps(seen["threads"])
    assert ids == [rouvert, attente, ouvert] and livre not in ids and laisse not in ids
    assert [step.get("status") for step in one["steps"]] == ["redo", "blocked", "open"]
    assert one["steps"][1]["reason"] == "attend la machine"
    assert one["counts"] == {"done": 1, "redo": 1, "open": 1, "blocked": 1}
    assert "| le-fil-vif | — | ▰▱▱▱▱ 1/4 🔄1 | now | `un-pas-rouvert`🔄 · `un-pas-ouvert` |" in front, front
    assert "⏸ le-fil-vif › `un-pas-en-attente` (attend la machine)" in front, front
    assert one["next"] == rouvert and "open_steps" not in seen and seen["closed"] == [mort]
    assert "worked_at" in one and "touched_at" not in one and all("thread" not in step for step in one["steps"])
    bare = json.loads(play("data", "--bare").stdout)
    [bare_one] = bare["threads"]
    assert all("text" not in step and "reason" not in step for step in bare_one["steps"])
    assert ([(s["id"], s["name"], s["status"]) for s in bare_one["steps"]]
            == [(s["id"], s["name"], s["status"]) for s in one["steps"]] and bare["closed"] == [mort])
    assert {one.name: hashlib.sha256(one.read_bytes()).hexdigest() for one in records.glob("threads*")} == prints
    refused = play("data", "x")
    empty = subprocess.run([_sys.executable, str(next((town / "beta" / ".pp" / ".sys" / "vendor").glob("steering@*"))
                                               / "skills" / "pp-steering" / "pp-steering.py"), "data"],
                           capture_output=True, text=True, cwd=str(alpha.parent))
    assert refused.returncode == 2 and json.loads(empty.stdout) == {"version": 3, "member": "beta", "threads": [], "closed": []}
    bench.held("the member's open threads as data", "`data` run on alpha's vendored script from beta's "
               "directory prints ONE JSON object -- version 3, alpha's name, its open threads alone: a "
               "closed thread absent, the delivered and the dropped steps absent, the reopened, the blocked "
               "(its reason) and the open ones in the thread's order, the counts the front's; an argument "
               "refuses, an empty record says empty lists, and not a byte of the records moved")

    console = str(town / "alpha" / "pp")
    opened = subprocess.run([console, "-new"], capture_output=True, text=True, cwd=str(alpha.parent))
    key = opened.stdout.split("run ", 1)[1].split()[0]
    through = None
    for _ in range(6):
        through = subprocess.run([console, key, "-s", "pp-steering", "data"], capture_output=True, text=True,
                                 cwd=str(alpha.parent))
        if through.returncode == 0 and '{"version"' in through.stdout:
            break
        subprocess.run([console, key], capture_output=True, text=True, cwd=str(alpha.parent))
    body = next((line for line in through.stdout.splitlines() if line.startswith('{"version"')), "")
    assert body and json.loads(body) == seen, through.stdout + through.stderr
    bench.held("the console plays the same data", "`./pp <key> -s pp-steering data` hands the agent the "
               "same object the script gave another member")

    # --- the changed verbs, played by the SCRIPT in a subprocess (KS12) ----------------------------
    def ledger_of() -> dict:
        return json.loads((alpha / ".sys" / "records" / "threads.json").read_text(encoding="utf-8"))
    born = play("open", "le-fil-identite", stdin="un-pas-nu\nun-pas-dit | un complement court\n")
    assert born.returncode == 0, born.stderr
    ident = next(tid for tid, one in ledger_of()["threads"].items() if one["name"] == "le-fil-identite")
    nu, dit = ledger_of()["threads"][ident]["steps"]
    assert ledger_of()["steps"][nu]["text"] == "" and ledger_of()["steps"][nu]["thread"] == ident
    assert "| `un-pas-nu` · `un-pas-dit` |" in play("status", ident).stdout
    assert play("attach", ident, "--as", "un-pas-court").returncode == 0
    over = play("attach", ident, "--as", "un-pas-long", "y" * 101)
    assert over.returncode == 2 and "budget" in over.stderr
    before = ledger_of()["threads"][ident]["worked_at"]
    assert play("amend", ident, nu, "--as", "un-pas-renomme", "un", "texte", "ajoute").returncode == 0
    assert play("rename", ident, "le-fil-identite-bis").returncode == 0
    after = ledger_of()
    assert after["threads"][ident]["worked_at"] == before and after["threads"][ident]["name"] == "le-fil-identite-bis"
    assert after["steps"][nu]["name"] == "un-pas-renomme" and after["steps"][nu]["text"] == "un texte ajoute"
    assert play("done", ident, dit).returncode == 0 and ledger_of()["threads"][ident]["worked_at"] > before
    assert play("unnamed").returncode == 2
    assert f"{nu} un-pas-renomme — un texte ajoute" in play("status", "--all").stdout
    bench.held("the changed verbs play by the script", "in a subprocess, as the console runs it: a step born "
               "by its name alone with its thread, the head at the name, an empty text attached, 101 "
               "characters refused, amend and rename leaving `worked_at` alone, done moving it, "
               "`unnamed` gone, the ledger naming the step")

    # --- a waiting step says what it covers AND why it waits ---------------------------------------
    assert play("open", "le-fil-en-attente", stdin="un-pas-ouvert | ce que le pas couvre\n"
                                                   "un-pas-garde | ce que le pas garde\nun-pas-nu\n").returncode == 0
    attente = next(tid for tid, one in ledger_of()["threads"].items() if one["name"] == "le-fil-en-attente")
    ouvert, garde, sans_texte = ledger_of()["threads"][attente]["steps"]
    assert play("block", attente, garde, "attend", "la", "machine").returncode == 0
    assert play("block", attente, sans_texte, "attend", "aussi").returncode == 0
    waiting = next(one for one in play("status", "--all").stdout.split("\n\n") if one.startswith("~ le-fil-en-attente"))
    assert f" -> {ouvert} un-pas-ouvert — ce que le pas couvre" in waiting, waiting
    assert f" ⛔ {garde} un-pas-garde — ce que le pas garde (attend la machine)" in waiting, waiting
    assert f" ⛔ {sans_texte} un-pas-nu — attend aussi" in waiting, waiting
    bench.held("a waiting step says its text and its reason", "at the ledger, a blocked step renders its text "
               "then its reason in parentheses, and its reason alone when it has no text -- the line of an "
               "open step does not move")

    # --- the BRAID by the script (batch la-tresse, KTR5): a thread that orders steps of other threads
    def tid_of(name: str) -> str:
        return next(tid for tid, one in ledger_of()["threads"].items() if one["name"] == name)

    def refused(code: str, *args: str, stdin: str = "") -> None:
        played = play(*args, stdin=stdin)
        assert played.returncode == 2 and code in played.stderr, (args, played.stdout, played.stderr)
        bench.held(code, "refused by the script")

    def graves_of() -> list:
        return [json.loads(one) for one in (alpha / ".sys" / "records" / "threads-closed.jsonl")
                .read_text(encoding="utf-8").splitlines() if one.strip()]

    assert play("open", "le-fil-gauche", stdin="g-un\ng-deux\ng-trois\n").returncode == 0
    assert play("open", "le-fil-droit", stdin="d-un\nd-deux\n").returncode == 0
    assert play("open", "le-fil-tiers", stdin="t-un\n").returncode == 0
    gauche, droit, tiers = tid_of("le-fil-gauche"), tid_of("le-fil-droit"), tid_of("le-fil-tiers")
    g1, g2, g3 = ledger_of()["threads"][gauche]["steps"]
    d1, d2 = ledger_of()["threads"][droit]["steps"]
    [t1] = ledger_of()["threads"][tiers]["steps"]
    assert play("amend", droit, d2, "--key", f"steering-thread:{gauche}").returncode == 0
    homes = {sid: step["thread"] for sid, step in ledger_of()["steps"].items()}          # read before, compared after
    for gone in (("open", "--braid", "la-tresse"), ("refer", gauche, d2), ("unlist", gauche, g1)):
        assert play(*gone, stdin=f"{g1}\n{d1}\n").returncode == 2, gone          # the braid's verbs are gone
    refused("step-invalid", "open", "le-fil-d-ids", stdin=f"{g1}\n")
    bench.held("the braid is gone", "`open --braid`, `refer` and `unlist` answer the usage; an id line at "
               "`open` still refuses -- a thread mints its own steps")

    whole = ledger_of()
    mixed = json.loads(json.dumps(whole))
    mixed["threads"][droit]["steps"].remove(d1)
    mixed["threads"][gauche]["steps"].append(d1)
    (alpha / ".sys" / "records" / "threads.json").write_text(json.dumps(mixed, indent=1, ensure_ascii=False), encoding="utf-8")
    played = play("status")
    assert played.returncode == 0 and "state-legacy" not in played.stderr, played.stderr
    (alpha / ".sys" / "records" / "threads.json").write_text(json.dumps(whole, indent=1, ensure_ascii=False), encoding="utf-8")
    bench.held("a thread lists freely", "a thread listing a step born in another thread reads: the list says "
               "where a step stands, `thread` where it was born")

    # --- move: a step changes thread and stays byte-identical ------------------------------------
    spool_alpha = alpha / ".sys" / "records" / "threads.json"
    assert play("open", "le-fil-source", stdin="s-pointe\ns-attend\ns-cle\n").returncode == 0
    assert play("open", "le-fil-arrivee", stdin="a-un\n").returncode == 0
    assert play("open", "le-fil-repos", stdin="r-un\n").returncode == 0
    source, arrivee, repos = tid_of("le-fil-source"), tid_of("le-fil-arrivee"), tid_of("le-fil-repos")
    sp, sa, sk = ledger_of()["threads"][source]["steps"]
    [a1] = ledger_of()["threads"][arrivee]["steps"]
    [r1] = ledger_of()["threads"][repos]["steps"]
    assert play("block", source, sa, "attend", "la", "machine").returncode == 0
    assert play("renext", source, sp).returncode == 0
    assert play("amend", source, sk, "--key", f"steering-thread:{tiers}").returncode == 0
    assert play("done", repos, r1).returncode == 0 and ledger_of()["threads"][repos]["next"] is None
    before = ledger_of()
    moved = play("move", source, sp, arrivee)
    after = ledger_of()
    assert moved.returncode == 0, (moved.stdout, moved.stderr)
    assert f"moved -- {sp} s-pointe : le-fil-source -> le-fil-arrivee [{arrivee}]" in moved.stdout, moved.stdout
    assert after["steps"] == before["steps"] and after["steps"][sp]["thread"] == source
    assert after["threads"][source]["steps"] == [sa, sk] and after["threads"][arrivee]["steps"] == [a1, sp]
    assert after["threads"][source]["next"] == sk and after["threads"][arrivee]["next"] == a1
    assert after["threads"][source]["worked_at"] > before["threads"][source]["worked_at"]
    assert after["threads"][arrivee]["worked_at"] > before["threads"][arrivee]["worked_at"]
    assert play("move", source, sa, arrivee).returncode == 0
    assert ledger_of()["threads"][arrivee]["steps"] == [a1, sp, sa] and ledger_of()["steps"][sa]["status"] == "blocked"
    assert play("move", source, sk, repos).returncode == 0
    landed = ledger_of()
    assert landed["threads"][repos]["steps"] == [r1, sk] and landed["threads"][repos]["next"] == sk
    assert landed["threads"][source]["steps"] == [] and landed["threads"][source]["next"] is None
    assert landed["steps"] == before["steps"]
    ledger = play("status", "--all").stdout
    block_of = next(one for one in ledger.split("\n\n") if one.startswith("~ le-fil-arrivee"))
    assert f"{sp} s-pointe" in block_of and f"{sa} s-attend" in block_of, ledger
    shown = {one["id"]: one for one in json.loads(play("data").stdout)["threads"]}
    assert [one["id"] for one in shown[arrivee]["steps"]] == [a1, sp, sa]
    assert all("thread" not in one for thread in shown.values() for one in thread["steps"])
    bench.held("move changes a step's thread, nothing else", "the id leaves the source's list and joins the end "
               "of the target's; the step byte-identical, its `thread` of birth included; the source's pointer "
               "moves on, the target's takes the step when it was empty; both threads dated; the ledger and "
               "`data` show it under the target")

    assert play("attach", "voisin.f.3", "--as", "venu-d-ailleurs", "--from", "voisin.s.1", "--owner", "voisin",
                "--name", "le-fil-du-voisin").returncode == 0
    assert play("attach", arrivee, "--as", "recu-ici", "--from", "voisin.s.2", "--owner", "voisin").returncode == 0
    assert play("open", "le-fil-homonyme", stdin="s-pointe\n").returncode == 0
    homonyme = tid_of("le-fil-homonyme")
    recu = ledger_of()["threads"][arrivee]["steps"][-1]
    for code, args in (("step-invalid", ("move", arrivee, sp, arrivee)),
                       ("thread-unknown", ("move", arrivee, sp, "alpha.f.999")),
                       ("thread-addressed-by-name", ("move", arrivee, sp, "le-fil-repos")),
                       ("step-unknown", ("move", arrivee, r1, repos)),
                       ("name-taken", ("move", arrivee, sp, homonyme)),
                       ("step-crossed", ("move", arrivee, recu, repos)),
                       ("thread-foreign", ("move", arrivee, sa, "voisin.f.3"))):
        kept = spool_alpha.read_bytes()
        refused(code, *args)
        assert spool_alpha.read_bytes() == kept, code
    bench.held("move refuses by name and writes nothing", "the same thread, an unknown target, a target given by "
               "its name, a step the source does not list, a name the target already wears, a step crossed from "
               "a neighbour, a thread another member owns -- the record byte-identical after each")

    listed = ledger_of()["threads"][arrivee]["steps"]
    assert play("close", arrivee).returncode == 0 and play("reopen", arrivee).returncode == 0
    assert ledger_of()["threads"][arrivee]["steps"] == listed
    assert play("done", arrivee, sp).returncode == 0 and "done_at" not in ledger_of()["steps"][sp]
    stamped = ledger_of()
    stamped["steps"][sp]["done_at"] = "2026-09-01T00:00:00+00:00"
    spool_alpha.write_text(json.dumps(stamped, indent=1, ensure_ascii=False), encoding="utf-8")
    assert play("status").returncode == 0 and play("data").returncode == 0
    stamped["steps"][sp].pop("done_at")
    spool_alpha.write_text(json.dumps(stamped, indent=1, ensure_ascii=False), encoding="utf-8")
    bench.held("a thread holding moved steps closes and reopens, done stamps no date", "the closure lists what the "
               "thread held, reopen reads it back; `done` writes no `done_at`, and a record still carrying one reads")
    whole = ledger_of()

    # --- an id of another member listed by a thread: refused by the script, closed `dropped` when none is held
    stranger = json.loads(json.dumps(whole))
    stranger["threads"][tiers]["steps"].append("voisin.s.7")
    (alpha / ".sys" / "records" / "threads.json").write_text(json.dumps(stranger, indent=1, ensure_ascii=False), encoding="utf-8")
    played = play("status")
    assert played.returncode == 2 and "state-legacy" in played.stderr and "voisin.s.7" in played.stderr, played.stderr
    assert play("data").returncode == 2 and play("done", tiers, t1).returncode == 2
    hollow = json.loads(json.dumps(whole))
    hollow["counters"]["f"] += 1
    hollow_id = f"alpha.f.{hollow['counters']['f']}"
    fresh = _dt.now(_tz.utc).isoformat(timespec="microseconds")
    hollow["threads"][hollow_id] = {"name": "le-fil-creux", "owner": "alpha", "steps": [], "next": None,
                                    "opened_at": fresh, "worked_at": fresh}
    (alpha / ".sys" / "records" / "threads.json").write_text(json.dumps(hollow, indent=1, ensure_ascii=False), encoding="utf-8")
    assert "le-fil-creux" not in play("status").stdout                     # nothing to do: no row
    ending = play("close", hollow_id)
    assert ending.returncode == 0 and graves_of()[-1]["id"] == hollow_id and graves_of()[-1]["closed_as"] == "dropped", ending.stderr
    (alpha / ".sys" / "records" / "threads.json").write_text(json.dumps(whole, indent=1, ensure_ascii=False), encoding="utf-8")
    bench.held("a foreign id is refused by the script, a hollow thread closes dropped", "an id no step of the "
               "dictionary holds, listed by a thread, refuses state-legacy at status, data and a write, naming "
               "the id; a thread listing no id at all has no row and closes `dropped`, never "
               "`delivered` -- nothing is delivered on nothing")

    front = play("status").stdout
    assert "| le-fil-gauche | — | ▱▱▱▱▱ 0/3 | now | `g-un` · `g-deux` · `g-trois` |" in front, front
    assert "| le-fil-droit | — |" in front and "| le-fil-tiers | — |" in front and f"steering-thread:{gauche}" not in front
    assert play("note", gauche, "le", "fil", "de", "gauche").returncode == 0
    assert "| le-fil-gauche | le fil de gauche | ▱▱▱▱▱ 0/3 |" in play("status").stdout
    seen = json.loads(play("data").stdout)
    by_id = {one["id"]: one for one in seen["threads"]}
    assert by_id[gauche]["note"] == "le fil de gauche" and "note" not in by_id[droit] and "braid" not in by_id[gauche]
    assert "note" not in json.loads(play("data", "--bare").stdout)["threads"][0]
    flat = [one for thread in seen["threads"] for one in thread["steps"]]
    assert all(one["status"] in ("open", "redo", "blocked") and "thread" not in one and one["name"] for one in flat)
    assert {sid: step["thread"] for sid, step in ledger_of()["steps"].items() if sid in homes} == homes
    bench.held("the script plays the front of the moment", "the table by the script: the note or `—`, up to three "
               "actions; `note` by the script sets it; `data` says the note (the bare form not), no `braid`, the open "
               "steps once under the thread that lists them; through the case no step changed its thread of birth")

    # --- the due front without a run --------------------------------------------------------------
    seen_file = alpha / ".sys" / "records" / "threads-seen.json"
    seen_before = seen_file.read_bytes() if seen_file.is_file() else None
    by_hand = play("status", "--due")
    assert by_hand.returncode == 0 and "| initiative | note | progress |" in by_hand.stdout, by_hand.stderr
    assert (seen_file.read_bytes() if seen_file.is_file() else None) == seen_before
    bench.held("no run, no snapshot", "`status --due` by hand renders the table and keeps nothing -- the "
               "snapshot record, whether the run the console played above bore it or not, is byte-identical")

    # --- a run whose slot is gone leaves the snapshot record when a table is served ----------------
    other = subprocess.run([console, "-new"], capture_output=True, text=True, cwd=str(alpha.parent))
    key_other = other.stdout.split("run ", 1)[1].split()[0]

    def served_to(run_key: str) -> subprocess.CompletedProcess:
        return subprocess.run([_sys.executable, str(script), "status", "--due"], capture_output=True, text=True,
                              cwd=str(alpha.parent), env={**os.environ, "PP_RUN": run_key})

    assert served_to(key_other).returncode == 0 and served_to(key).returncode == 0
    both = json.loads(seen_file.read_text(encoding="utf-8"))
    persistence.slot_of(alpha, key_other).unlink()
    assert served_to(key).returncode == 0
    after = json.loads(seen_file.read_text(encoding="utf-8"))
    assert {key, key_other} <= set(both) and set(after) == {key}, (sorted(both), sorted(after))
    bench.held("a gone run leaves at the service", "two runs of the console seen, the slot of one removed, "
               "the table served to the other: `threads-seen.json` keeps the served run alone")

    # --- after the whole case: one open thread at most lists a step, its thread of birth kept ------
    for meta, final in ((root, record()), (alpha, ledger_of())):
        tombs = [json.loads(one) for one in (meta / ".sys" / "records" / "threads-closed.jsonl")
                 .read_text(encoding="utf-8").splitlines() if one.strip()]
        known = set(final["threads"]) | {tomb["id"] for tomb in tombs}
        for sid, step in final["steps"].items():
            assert sum(sid in one["steps"] for one in final["threads"].values()) <= 1, sid
            assert step["thread"] in known and step["name"], (sid, step)
    assert all(ledger_of()["steps"][sid]["thread"] == source for sid in (sp, sa, sk))
    bench.held("a step stands in one open thread at most", "after every move of the case, no step is listed "
               "by two open threads, and each keeps the thread it was born in")

    return 0
