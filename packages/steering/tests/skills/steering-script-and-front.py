"""packages/steering/skills/pp-steering -- the keeper played as a SCRIPT, in a subprocess as the
console runs it, on a town of members installed by hand (alpha, beta, gamma), and the FRONT OF
THE MOMENT it renders:
- `data`: a member's open threads as one JSON object, read from another member's directory,
  the same through the console; the verbs by the script -- a step by its name alone, the ledger's
  waiting line, `move` and its refusals, a foreign id refused, a hollow thread closed `dropped`;
  `status --due` keeping the snapshot of the runs that are served
- the front, without an id: a thread's NOTE, the table freshest first with its marks, up to
  `steering_next_max` actions then `…`, the ⏸ line of the waiting steps and its cap, the 💤
  footer past the `steering_front_min` rows kept, the age, `attach` saying the thread's id, and
  `status --all --open`, the ledger the boot serves."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

from conductor import install, persistence
from tests.harness import PRODUCT_ENGINE, load_script, support

K = support(__file__, "keeper")


def scenario(bench) -> int:
    town = bench.temp()
    for name in ("alpha", "beta", "gamma"):
        install.install(PRODUCT_ENGINE, town / name / ".pp", ["steering"])
    alpha, beta, gamma = (town / name / ".pp" for name in ("alpha", "beta", "gamma"))
    script = K.script_of(alpha)
    play = K.player(script, alpha.parent)
    spool = alpha / ".sys" / "records" / "threads.json"

    def ledger_of() -> dict:
        return K.record(alpha)

    def tid_of(name: str) -> str:
        return K.tid_of(alpha, name)

    # --- `data`: the member's open threads as DATA, read through the vendored script ----------
    with K.case(bench, "the member's open threads as data", "`data` run on alpha's vendored script from beta's "
                "directory prints ONE JSON object -- version 3, alpha's name, its open threads alone: a "
                "closed thread absent, the delivered and the dropped steps absent, the reopened, the blocked "
                "(its reason) and the open ones in the thread's order, the counts the front's; an argument "
                "refuses, an empty record says empty lists, and not a byte of the records moved") as check:
        play("open", "le-fil-vif", stdin="un-pas-livre | un pas livre\nun-pas-laisse | un pas laisse\n"
                                       "un-pas-rouvert | un pas rouvert\nun-pas-en-attente | un pas en attente\n"
                                       "un-pas-ouvert | un pas ouvert\n")
        play("open", "le-fil-mort", stdin="un-pas-du-fil-mort | un pas du fil mort\n")
        vif, mort = tid_of("le-fil-vif"), tid_of("le-fil-mort")
        livre, laisse, rouvert, attente, ouvert = ledger_of()["threads"][vif]["steps"]
        play("done", vif, livre)
        play("drop", vif, laisse)
        play("done", vif, rouvert)
        play("renext", vif, rouvert)
        play("block", vif, attente, "attend la machine")
        play("close", mort)
        play("reopen", mort)
        check(json.loads(play("data").stdout)["closed"] == [], "a reopened thread is open, not closed")
        play("close", mort)
        records = alpha / ".sys" / "records"
        prints = {one.name: hashlib.sha256(one.read_bytes()).hexdigest() for one in records.glob("threads*")}

        served = play("data", cwd_=town / "beta")                    # from ANOTHER member's directory
        seen = json.loads(served.stdout)
        [one] = seen["threads"]
        ids = [step["id"] for step in one["steps"]]
        check(served.returncode == 0 and seen["version"] == 3 and seen["member"] == "alpha", "the object's head")
        check(one["id"] == vif and one["name"] == "le-fil-vif" and one["owner"] == "alpha"
              and mort not in json.dumps(seen["threads"]), "the open thread alone")
        check(ids == [rouvert, attente, ouvert] and livre not in ids and laisse not in ids, f"the steps {ids}")
        check([step.get("status") for step in one["steps"]] == ["redo", "blocked", "open"], "their statuses")
        check(one["steps"][1].get("reason") == "attend la machine", "the blocked step's reason")
        check(one["counts"] == {"done": 1, "redo": 1, "open": 1, "blocked": 1}, f"the counts {one['counts']}")
        shown = K.front(subprocess.run([sys.executable, str(script), "status", vif], capture_output=True, text=True).stdout)
        row = shown.row("le-fil-vif")
        check(row and (row.note, row.bar, row.done, row.total, row.redo, row.age) == ("—", "▰▱▱▱▱", 1, 4, 1, "now"),
              f"the front's counts {row}")
        check(row and row.actions == [("un-pas-rouvert", "🔄"), ("un-pas-ouvert", "")], "the front's actions")
        check(("le-fil-vif", "un-pas-en-attente", "attend la machine") in shown.waiting, f"the ⏸ line {shown.waiting}")
        check(one["next"] == rouvert and "open_steps" not in seen and seen["closed"] == [mort], "next and closed")
        check("worked_at" in one and "touched_at" not in one and all("thread" not in step for step in one["steps"]),
              "the date of the work, no thread of birth")
        bare = json.loads(play("data", "--bare").stdout)
        [bare_one] = bare["threads"]
        check(all("text" not in step and "reason" not in step for step in bare_one["steps"]), "--bare: no text")
        check([(x["id"], x["name"], x["status"]) for x in bare_one["steps"]]
              == [(x["id"], x["name"], x["status"]) for x in one["steps"]] and bare["closed"] == [mort], "--bare: the same steps")
        check({x.name: hashlib.sha256(x.read_bytes()).hexdigest() for x in records.glob("threads*")} == prints,
              "a byte of the records moved")
        empty = subprocess.run([sys.executable, str(K.script_of(beta)), "data"], capture_output=True, text=True,
                               cwd=str(alpha.parent))
        check(play("data", "x").returncode == 2, "an argument refuses")
        check(json.loads(empty.stdout) == {"version": 3, "member": "beta", "threads": [], "closed": []}, "the empty record")

    console = str(town / "alpha" / "pp")
    with K.case(bench, "the console plays the same data", "`./pp <key> -s pp-steering data` hands the agent "
                "the same object the script gave another member") as check:
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
        check(body and json.loads(body) == seen, (through.stdout + through.stderr)[-200:])

    # --- the verbs played by the SCRIPT in a subprocess --------------------------------------------
    with K.case(bench, "the changed verbs play by the script", "in a subprocess, as the console runs it: a step "
                "born by its name alone with its thread, the head at the name, an empty text attached, 101 "
                "characters refused, amend and rename leaving `worked_at` alone, done moving it, `unnamed` "
                "gone, the ledger naming the step") as check:
        born = play("open", "le-fil-identite", stdin="un-pas-nu\nun-pas-dit | un complement court\n")
        check(born.returncode == 0, born.stderr)
        ident = tid_of("le-fil-identite")
        nu, dit = ledger_of()["threads"][ident]["steps"]
        check(ledger_of()["steps"][nu]["text"] == "" and ledger_of()["steps"][nu]["thread"] == ident, "born by its name")
        row = K.front(play("status", ident).stdout).row("le-fil-identite")
        check(row and row.actions == [("un-pas-nu", ""), ("un-pas-dit", "")], f"the head at the name {row}")
        check(play("attach", ident, "--as", "un-pas-court").returncode == 0, "an empty text attached")
        over = play("attach", ident, "--as", "un-pas-long", "y" * 101)
        check(over.returncode == 2 and "budget" in over.stderr, "101 characters refused")
        before = ledger_of()["threads"][ident]["worked_at"]
        check(play("amend", ident, nu, "--as", "un-pas-renomme", "un", "texte", "ajoute").returncode == 0, "amend")
        check(play("rename", ident, "le-fil-identite-bis").returncode == 0, "rename")
        after = ledger_of()
        check(after["threads"][ident]["worked_at"] == before and after["threads"][ident]["name"] == "le-fil-identite-bis",
              "amend and rename leave the date")
        check(after["steps"][nu]["name"] == "un-pas-renomme" and after["steps"][nu]["text"] == "un texte ajoute", "amended")
        check(play("done", ident, dit).returncode == 0 and ledger_of()["threads"][ident]["worked_at"] > before, "done dates")
        check(play("unnamed").returncode == 2, "`unnamed` gone")
        line = K.ledger(play("status", "--all").stdout)["le-fil-identite-bis"].steps.get(nu)
        check(line and (line.name, line.text) == (after["steps"][nu]["name"], after["steps"][nu]["text"]),
              f"the ledger names the step {line}")

    with K.case(bench, "a waiting step says its text and its reason", "at the ledger, a blocked step renders its "
                "text then its reason in parentheses, and its reason alone when it has no text -- the line of "
                "an open step does not move") as check:
        check(play("open", "le-fil-en-attente", stdin="un-pas-ouvert | ce que le pas couvre\n"
                                                      "un-pas-garde | ce que le pas garde\nun-pas-nu\n").returncode == 0, "open")
        waits = tid_of("le-fil-en-attente")
        open_one, kept, bare_one = ledger_of()["threads"][waits]["steps"]
        check(play("block", waits, kept, "attend", "la", "machine").returncode == 0, "block")
        check(play("block", waits, bare_one, "attend", "aussi").returncode == 0, "block")
        steps = ledger_of()["steps"]
        lines = K.ledger(play("status", "--all").stdout)["le-fil-en-attente"].steps
        check((lines[open_one].mark, lines[open_one].name, lines[open_one].text)
              == ("->", steps[open_one]["name"], steps[open_one]["text"]), "the open step's line")
        check((lines[kept].mark, lines[kept].name, lines[kept].text)
              == ("⛔", steps[kept]["name"], f"{steps[kept]['text']} ({steps[kept]['reason']})"), "text then reason")
        check((lines[bare_one].mark, lines[bare_one].name, lines[bare_one].text)
              == ("⛔", steps[bare_one]["name"], steps[bare_one]["reason"]), "the reason alone")

    # --- a thread mints its own steps, and lists freely ------------------------------------------
    with K.case(bench, "the braid is gone", "`open --braid`, `refer` and `unlist` answer the usage; an id line "
                "at `open` still refuses -- a thread mints its own steps") as check:
        check(play("open", "le-fil-gauche", stdin="g-un\ng-deux\ng-trois\n").returncode == 0, "open")
        check(play("open", "le-fil-droit", stdin="d-un\nd-deux\n").returncode == 0, "open")
        check(play("open", "le-fil-tiers", stdin="t-un\n").returncode == 0, "open")
        gauche, droit, tiers = tid_of("le-fil-gauche"), tid_of("le-fil-droit"), tid_of("le-fil-tiers")
        g1, _, _ = ledger_of()["threads"][gauche]["steps"]
        d1, d2 = ledger_of()["threads"][droit]["steps"]
        [t1] = ledger_of()["threads"][tiers]["steps"]
        check(play("amend", droit, d2, "--key", f"steering-thread:{gauche}").returncode == 0, "the key")
        homes = {sid: step["thread"] for sid, step in ledger_of()["steps"].items()}       # read before, compared after
        for gone in (("open", "--braid", "la-tresse"), ("refer", gauche, d2), ("unlist", gauche, g1)):
            check(play(*gone, stdin=f"{g1}\n{d1}\n").returncode == 2, f"{gone[0]} answers the usage")
        K.refused(bench, play("open", "le-fil-d-ids", stdin=f"{g1}\n"), "step-invalid")

    with K.case(bench, "a thread lists freely", "a thread listing a step born in another thread reads: the list "
                "says where a step stands, `thread` where it was born") as check:
        whole = ledger_of()
        mixed = json.loads(json.dumps(whole))
        mixed["threads"][droit]["steps"].remove(d1)
        mixed["threads"][gauche]["steps"].append(d1)
        spool.write_text(json.dumps(mixed, indent=1, ensure_ascii=False), encoding="utf-8")
        played = play("status")
        check(played.returncode == 0 and "state-legacy" not in played.stderr, played.stderr)
        spool.write_text(json.dumps(whole, indent=1, ensure_ascii=False), encoding="utf-8")

    # --- move: a step changes thread and stays byte-identical ------------------------------------
    with K.case(bench, "move changes a step's thread, nothing else", "the id leaves the source's list and joins "
                "the end of the target's; the step byte-identical, its `thread` of birth included; the source's "
                "pointer moves on, the target's takes the step when it was empty; both threads dated; the "
                "ledger and `data` show it under the target") as check:
        check(play("open", "le-fil-source", stdin="s-pointe\ns-attend\ns-cle\n").returncode == 0, "open")
        check(play("open", "le-fil-arrivee", stdin="a-un\n").returncode == 0, "open")
        check(play("open", "le-fil-repos", stdin="r-un\n").returncode == 0, "open")
        source, arrivee, repos = tid_of("le-fil-source"), tid_of("le-fil-arrivee"), tid_of("le-fil-repos")
        sp, sa, sk = ledger_of()["threads"][source]["steps"]
        [a1] = ledger_of()["threads"][arrivee]["steps"]
        [r1] = ledger_of()["threads"][repos]["steps"]
        check(play("block", source, sa, "attend", "la", "machine").returncode == 0, "block")
        check(play("renext", source, sp).returncode == 0, "renext")
        check(play("amend", source, sk, "--key", f"steering-thread:{tiers}").returncode == 0, "the key")
        check(play("done", repos, r1).returncode == 0 and ledger_of()["threads"][repos]["next"] is None, "done")
        before = ledger_of()
        went = play("move", source, sp, arrivee)
        after = ledger_of()
        check(went.returncode == 0, went.stderr)
        check(K.moved(went.stdout) == (sp, "s-pointe", "le-fil-source", "le-fil-arrivee", arrivee),
              f"the move said: step, its name, source, target and its id {K.moved(went.stdout)}")
        check(after["steps"] == before["steps"] and after["steps"][sp]["thread"] == source, "the step byte-identical")
        check(after["threads"][source]["steps"] == [sa, sk] and after["threads"][arrivee]["steps"] == [a1, sp], "the lists")
        check(after["threads"][source]["next"] == sk and after["threads"][arrivee]["next"] == a1, "the pointers")
        check(after["threads"][source]["worked_at"] > before["threads"][source]["worked_at"]
              and after["threads"][arrivee]["worked_at"] > before["threads"][arrivee]["worked_at"], "both dated")
        check(play("move", source, sa, arrivee).returncode == 0, "move a blocked step")
        check(ledger_of()["threads"][arrivee]["steps"] == [a1, sp, sa] and ledger_of()["steps"][sa]["status"] == "blocked",
              "the blocked step moved, still blocked")
        check(play("move", source, sk, repos).returncode == 0, "move to a thread with no next")
        landed = ledger_of()
        check(landed["threads"][repos]["steps"] == [r1, sk] and landed["threads"][repos]["next"] == sk, "the target points it")
        check(landed["threads"][source]["steps"] == [] and landed["threads"][source]["next"] is None, "the source empty")
        check(landed["steps"] == before["steps"], "the dictionary unchanged")
        block = K.ledger(play("status", "--all").stdout).get("le-fil-arrivee")
        check(block and sp in block.steps and sa in block.steps
              and (block.steps[sp].name, block.steps[sa].name) == ("s-pointe", "s-attend"), "the ledger under the target")
        shown = {one["id"]: one for one in json.loads(play("data").stdout)["threads"]}
        check([one["id"] for one in shown[arrivee]["steps"]] == [a1, sp, sa], "`data` under the target")
        check(all("thread" not in one for thread in shown.values() for one in thread["steps"]), "`data` says no birth")

    with K.case(bench, "move refuses by name and writes nothing", "the same thread, an unknown target, a target "
                "given by its name, a step the source does not list, a name the target already wears, a step "
                "crossed from a neighbour, a thread another member owns -- the record byte-identical after "
                "each") as check:
        check(play("attach", "voisin.f.3", "--as", "venu-d-ailleurs", "--from", "voisin.s.1", "--owner", "voisin",
                   "--name", "le-fil-du-voisin").returncode == 0, "a crossing")
        check(play("attach", arrivee, "--as", "recu-ici", "--from", "voisin.s.2", "--owner", "voisin").returncode == 0,
              "a crossing received")
        check(play("open", "le-fil-homonyme", stdin="s-pointe\n").returncode == 0, "open")
        homonyme = tid_of("le-fil-homonyme")
        recu = ledger_of()["threads"][arrivee]["steps"][-1]
        for code, args in (("step-invalid", ("move", arrivee, sp, arrivee)),
                           ("thread-unknown", ("move", arrivee, sp, "alpha.f.999")),
                           ("thread-addressed-by-name", ("move", arrivee, sp, "le-fil-repos")),
                           ("step-unknown", ("move", arrivee, r1, repos)),
                           ("name-taken", ("move", arrivee, sp, homonyme)),
                           ("step-crossed", ("move", arrivee, recu, repos)),
                           ("thread-foreign", ("move", arrivee, sa, "voisin.f.3"))):
            kept = spool.read_bytes()
            K.refused(bench, play(*args), code)
            check(spool.read_bytes() == kept, f"{code} wrote")

    with K.case(bench, "a thread holding moved steps closes and reopens, done stamps no date", "the closure lists "
                "what the thread held, reopen reads it back; `done` writes no `done_at`, and a record still "
                "carrying one reads") as check:
        listed = ledger_of()["threads"][arrivee]["steps"]
        check(play("close", arrivee).returncode == 0 and play("reopen", arrivee).returncode == 0, "close and reopen")
        check(ledger_of()["threads"][arrivee]["steps"] == listed, "the list read back")
        check(play("done", arrivee, sp).returncode == 0 and "done_at" not in ledger_of()["steps"][sp], "done writes no date")
        stamped = ledger_of()
        stamped["steps"][sp]["done_at"] = "2026-09-01T00:00:00+00:00"
        spool.write_text(json.dumps(stamped, indent=1, ensure_ascii=False), encoding="utf-8")
        check(play("status").returncode == 0 and play("data").returncode == 0, "a record carrying a date reads")
        stamped["steps"][sp].pop("done_at")
        spool.write_text(json.dumps(stamped, indent=1, ensure_ascii=False), encoding="utf-8")

    # --- an id of another member listed by a thread: refused; a hollow thread closes `dropped` ---
    with K.case(bench, "a foreign id is refused by the script, a hollow thread closes dropped", "an id no step of "
                "the dictionary holds, listed by a thread, refuses state-legacy at status, data and a write, "
                "naming the id; a thread listing no id at all has no row and closes `dropped`, never "
                "`delivered` -- nothing is delivered on nothing") as check:
        whole = ledger_of()
        stranger = json.loads(json.dumps(whole))
        stranger["threads"][tiers]["steps"].append("voisin.s.7")
        spool.write_text(json.dumps(stranger, indent=1, ensure_ascii=False), encoding="utf-8")
        played = play("status")
        check(played.returncode == 2 and "state-legacy" in played.stderr and "voisin.s.7" in played.stderr, played.stderr)
        check(play("data").returncode == 2 and play("done", tiers, t1).returncode == 2, "data and a write refuse")
        hollow = json.loads(json.dumps(whole))
        hollow["counters"]["f"] += 1
        hollow_id = f"alpha.f.{hollow['counters']['f']}"
        fresh = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        hollow["threads"][hollow_id] = {"name": "le-fil-creux", "owner": "alpha", "steps": [], "next": None,
                                        "opened_at": fresh, "worked_at": fresh}
        spool.write_text(json.dumps(hollow, indent=1, ensure_ascii=False), encoding="utf-8")
        check(K.front(play("status").stdout).row("le-fil-creux") is None, "nothing to do: no row")
        ending = play("close", hollow_id)
        check(ending.returncode == 0 and K.graves(alpha)[-1]["id"] == hollow_id
              and K.graves(alpha)[-1]["closed_as"] == "dropped", ending.stderr)
        spool.write_text(json.dumps(whole, indent=1, ensure_ascii=False), encoding="utf-8")

    with K.case(bench, "the script plays the front of the moment", "the table by the script: the note or `—`, up "
                "to three actions; `note` by the script sets it; `data` says the note (the bare form not), no "
                "`braid`, the open steps once under the thread that lists them; through the case no step changed "
                "its thread of birth") as check:
        seen_front = K.front(play("status").stdout)
        row = seen_front.row("le-fil-gauche")
        check(row and (row.note, row.bar, row.done, row.total, row.age) == ("—", "▱▱▱▱▱", 0, 3, "now"), f"the row {row}")
        check(row and row.actions == [("g-un", ""), ("g-deux", ""), ("g-trois", "")] and not row.more, "three actions")
        check(all(seen_front.row(name) and seen_front.row(name).note == "—" for name in ("le-fil-droit", "le-fil-tiers")),
              "the other rows")
        check(f"steering-thread:{gauche}" not in play("status").stdout, "no key at the front")
        check(play("note", gauche, "le", "fil", "de", "gauche").returncode == 0, "note")
        row = K.front(play("status").stdout).row("le-fil-gauche")
        check(row and (row.note, row.done, row.total) == ("le fil de gauche", 0, 3), f"the note in its column {row}")
        seen = json.loads(play("data").stdout)
        by_id = {one["id"]: one for one in seen["threads"]}
        check(by_id[gauche].get("note") == "le fil de gauche" and "note" not in by_id[droit]
              and "braid" not in by_id[gauche], "`data` says the note")
        check("note" not in json.loads(play("data", "--bare").stdout)["threads"][0], "the bare form says none")
        flat = [one for thread in seen["threads"] for one in thread["steps"]]
        check(all(one["status"] in ("open", "redo", "blocked") and "thread" not in one and one["name"] for one in flat),
              "the open steps alone")
        check({sid: step["thread"] for sid, step in ledger_of()["steps"].items() if sid in homes} == homes,
              "a step changed its thread of birth")

    # --- the due front without a run -------------------------------------------------------------
    seen_file = alpha / ".sys" / "records" / "threads-seen.json"
    with K.case(bench, "no run, no snapshot", "`status --due` by hand renders the table and keeps nothing -- the "
                "snapshot record, whether the run the console played above bore it or not, is "
                "byte-identical") as check:
        seen_before = seen_file.read_bytes() if seen_file.is_file() else None
        by_hand = play("status", "--due")
        check(by_hand.returncode == 0 and K.front(by_hand.stdout).header == K.HEADER, by_hand.stderr)
        check((seen_file.read_bytes() if seen_file.is_file() else None) == seen_before, "the snapshot moved")

    # --- a run whose slot is gone leaves the snapshot record when a table is served ---------------
    with K.case(bench, "a gone run leaves at the service", "two runs of the console seen, the slot of one "
                "removed, the table served to the other: `threads-seen.json` keeps the served run alone") as check:
        other = subprocess.run([console, "-new"], capture_output=True, text=True, cwd=str(alpha.parent))
        key_other = other.stdout.split("run ", 1)[1].split()[0]

        def served_to(run_key: str) -> subprocess.CompletedProcess:
            return play("status", "--due", env={**os.environ, "PP_RUN": run_key})

        check(served_to(key_other).returncode == 0 and served_to(key).returncode == 0, "served to both")
        both = json.loads(seen_file.read_text(encoding="utf-8"))
        persistence.slot_of(alpha, key_other).unlink()
        check(served_to(key).returncode == 0, "served again")
        after = json.loads(seen_file.read_text(encoding="utf-8"))
        check({key, key_other} <= set(both) and set(after) == {key}, f"{sorted(both)} {sorted(after)}")

    # --- the FRONT OF THE MOMENT, on gamma: the note ----------------------------------------------
    play_g = K.player(K.script_of(gamma), gamma.parent)

    def record_g() -> dict:
        return K.record(gamma)

    def tid_g(name: str) -> str:
        return K.tid_of(gamma, name)

    with K.case(bench, "a thread wears a note", "`open --note` gives it, `note` rewrites it without moving the "
                "date, 81 characters refuse `budget`; the front shows it in its column (a pipe escaped), the "
                "ledger after `—`") as check:
        born = play_g("open", "le-banc", "--note", "rouges excusés à chaque suite",
                      stdin="les-motifs-morts\nla-cle-en-chiffres\nla-cle-du-run-ferme\nle-marbre-qui-fuit\n")
        check(born.returncode == 0 and "opened -- le-banc [" in born.stdout, born.stderr)
        banc = tid_g("le-banc")
        check(record_g()["threads"][banc].get("note") == "rouges excusés à chaque suite", "the note given")
        dated = record_g()["threads"][banc]["worked_at"]
        check(play_g("note", banc, "motifs", "morts", "levés ;", "3", "rouges", "restent").returncode == 0, "note")
        check(record_g()["threads"][banc].get("note") == "motifs morts levés ; 3 rouges restent", "the note rewritten")
        check(record_g()["threads"][banc]["worked_at"] == dated, "a note is no work")
        over = play_g("note", banc, "x" * 81)
        check(over.returncode == 2 and "budget" in over.stderr and record_g()["threads"][banc]["note"].startswith("motifs"),
              "81 characters refuse")
        check(play_g("note", banc, "x" * 80).returncode == 0, "80 characters pass")
        check(play_g("note", banc, "a | pipe").returncode == 0, "a pipe")
        seen = K.front(play_g("status").stdout)
        check(seen.header == K.HEADER, f"the header {seen.header}")
        row = seen.row("le-banc")
        check(row and (row.note, row.bar, row.done, row.total, row.age) == ("a \\| pipe", "▱▱▱▱▱", 0, 4, "now"),
              f"a pipe stays in its cell {row}")
        block = K.ledger(play_g("status", "--all").stdout).get("le-banc")
        check(block and block.id == banc and block.note == "a | pipe", f"the ledger after `—` {block}")

    with K.case(bench, "attach says the thread's id", "`attached -- <name> [<thread id>] <step id>`: a step minted "
                "after the boot gives its thread's id to the context") as check:
        added = play_g("attach", banc, "--as", "la-trace-intermittente")
        check(added.returncode == 0 and f"attached -- le-banc [{banc}] " in added.stdout, added.stdout)

    with K.case(bench, "the next actions", "from the pointed step on, in the thread's order, three at most then "
                "`…`; `steering_next_max: 1` names one") as check:
        names = [record_g()["steps"][sid]["name"] for sid in record_g()["threads"][banc]["steps"]]
        row = K.front(play_g("status").stdout).row("le-banc")
        check(row and row.actions == [(name, "") for name in names[:3]] and row.more, f"three then … {row}")
        K.set_to(gamma, "steering_next_max", 1)
        row = K.front(play_g("status").stdout).row("le-banc")
        check(row and row.actions == [(names[0], "")] and row.more, f"one then … {row}")
        K.set_to(gamma, "steering_next_max", 3)

    with K.case(bench, "no row without an action, the ⏸ line", "a thread whose steps all wait has no row; every "
                "waiting step of the open threads stands at the ⏸ line as `thread › step (reason)`, seven named "
                "then `+n`; released, a step brings its thread back to the table") as check:
        parked = play_g("open", "le-temoin", "--note", "témoin garé ici",
                        stdin="".join(f"le-defaut-{n}\n" for n in range(1, 10)))
        check(parked.returncode == 0, parked.stderr)
        temoin = tid_g("le-temoin")
        for sid in record_g()["threads"][temoin]["steps"]:
            check(play_g("block", temoin, sid, "témoin garé ici").returncode == 0, f"block {sid}")
        steps = record_g()["steps"]
        first = steps[record_g()["threads"][temoin]["steps"][0]]
        seen = K.front(play_g("status").stdout)
        check(seen.row("le-temoin") is None, "no row")
        check(seen.waiting[:1] == [("le-temoin", first["name"], first["reason"])], f"the ⏸ line {seen.waiting[:1]}")
        check(len(seen.waiting) == 7 and seen.beyond == 2, f"seven named then +2: {len(seen.waiting)} +{seen.beyond}")
        check(play_g("renext", temoin, record_g()["threads"][temoin]["steps"][0]).returncode == 0, "renext")
        seen = K.front(play_g("status").stdout)
        row = seen.row("le-temoin")
        check(row and row.note == record_g()["threads"][temoin]["note"] and seen.beyond == 1, f"back at the table {row}")

    # --- the table keeps the freshest rows before anything folds to the 💤 footer -----------------
    keeper = load_script(K.script_of(gamma))
    with K.case(bench, "a thread nobody wrote for the cut FOLDS to the footer, past the rows kept", "past "
                "steering_dormant_days (7 by default, read at worked_at) a thread may leave the table for the "
                "footer -- one line after 💤, its name, its pointed step fenced and its age -- but the table "
                "keeps the steering_front_min freshest rows first (5): every thread dormant, the table still "
                "shows five, or all of them when fewer; at 0 the table empties to the footer as before") as check:
        for n in range(1, 7):
            check(play_g("open", f"le-fil-{n}", stdin=f"le-pas-{n}\n").returncode == 0, f"open le-fil-{n}")
        later = datetime.now(timezone.utc) + timedelta(days=9)
        live = sum(1 for one in record_g()["threads"].values()
                   if any(record_g()["steps"][sid]["status"] in ("open", "redo") for sid in one["steps"]))
        check(live == 8, f"{live} threads with work")
        every = K.front(keeper.front(gamma, keeper.load(gamma), now=later))
        check(len(every.rows) == 5 and len(every.dormant) == 3, f"all dormant: {len(every.rows)} rows, {len(every.dormant)} folded")
        awake = K.front(keeper.front(gamma, keeper.load(gamma)))
        check(len(awake.rows) == 8 and not awake.dormant, "awake: every row, no footer")
        K.set_to(gamma, "steering_front_min", 0)
        bare = keeper.front(gamma, keeper.load(gamma), now=later)
        every = K.front(bare)
        check(every.header is None and len(every.dormant) == 8 and "older than" not in bare, "at 0: the footer alone")
        kept = record_g()["threads"][tid_g("le-fil-1")]["worked_at"]
        ahead = keeper.load(gamma)
        ahead["threads"][tid_g("le-fil-1")]["worked_at"] = later.isoformat(timespec="microseconds")
        keeper.save(gamma, ahead)
        mixed = K.front(keeper.front(gamma, keeper.load(gamma), now=later))
        row = mixed.row("le-fil-1")
        check([one.name for one in mixed.rows] == ["le-fil-1"] and row.age == "now", f"the fresh row {mixed.rows}")
        check(("le-fil-2", "le-pas-2", "1 week") in mixed.dormant and mixed.row("le-fil-2") is None,
              f"the footer: name, pointed step, age {mixed.dormant}")
        back = keeper.load(gamma)
        back["threads"][tid_g("le-fil-1")]["worked_at"] = kept
        keeper.save(gamma, back)
        K.set_to(gamma, "steering_front_min", 5)
        for n in range(1, 7):
            check(play_g("close", tid_g(f"le-fil-{n}")).returncode == 0, f"close le-fil-{n}")
        few = K.front(keeper.front(gamma, keeper.load(gamma), now=later))
        check(len(few.rows) == 2 and not few.dormant, f"two dormant threads: {len(few.rows)} rows, no footer")

    # --- the front is the keeper's, without an id: order, marks, flags --------------------------
    with K.case(bench, "the front is the keeper's, without an id", "the table freshest first (the last written "
                "thread first), no rank, every thread with a step to do on its row with its flag and bare name, "
                "its note or `—`, its five-cell bar and delivered/total, its age and its next actions with their "
                "marks (🔄 reopened, 📥 crossed in, ✉️ addressed), 🔗 for a thread another member owns; a thread "
                "with nothing to do has no row; no text, no key, no id -- the operator reads work, the agent "
                "reads ids and keys at `--all`; a NAME given to any verb but `open` refuses "
                "thread-addressed-by-name, naming the id it labels") as check:
        check(play_g("open", "le-fil-fini", stdin="une-etape-vite-faite\n").returncode == 0, "open")
        fini = record_g()["threads"][tid_g("le-fil-fini")]["steps"][0]
        check(play_g("done", tid_g("le-fil-fini"), fini).returncode == 0, "done")
        check(play_g("attach", "voisin.f.7", "--as", "le-pas-venu", "--from", "voisin.s.4", "--owner", "voisin",
                     "--name", "le-fil-arrive").returncode == 0, "a crossing")
        arrive = "voisin.f.7"
        check(play_g("done", arrive, record_g()["threads"][arrive]["steps"][0]).returncode == 0, "done")
        check(play_g("attach", arrive, "--as", "la-suite").returncode == 0, "attach")
        check(play_g("attach", arrive, "--as", "voisin-la-suite", "--from", "voisin.s.5", "--owner", "voisin")
              .returncode == 0, "a second crossing")
        check(play_g("open", "le-fil-adresse", stdin="voisin-dis-moi-ce | @voisin dis-moi ce que tu vois\n")
              .returncode == 0, "open")
        check(play_g("open", "le-fil-deux", stdin="une-etape\nun-pas-qui-vise\n").returncode == 0, "open")
        check(play_g("attach", tid_g("le-fil-deux"), "--as", "un-pas-de-plus").returncode == 0, "attach")
        shown = play_g("status").stdout
        seen = K.front(shown)
        check([one.name for one in seen.rows][:3] == ["le-fil-deux", "le-fil-adresse", "le-fil-arrive"],
              f"freshest first {[one.name for one in seen.rows]}")
        deux, adresse, crossed = (seen.row(name) for name in ("le-fil-deux", "le-fil-adresse", "le-fil-arrive"))
        check(deux and (deux.flag, deux.note, deux.bar, deux.done, deux.total) == ("", "—", "▱▱▱▱▱", 0, 3), f"{deux}")
        check(adresse and (adresse.done, adresse.total) == (0, 1) and adresse.actions == [("voisin-dis-moi-ce", "✉️")],
              f"addressed {adresse}")
        check(crossed and (crossed.flag, crossed.done, crossed.total) == ("🔗", 1, 3)
              and crossed.actions == [("la-suite", ""), ("voisin-la-suite", "📥")], f"owned elsewhere, crossed in {crossed}")
        check(seen.row("le-fil-fini") is None, "nothing to do: no row")
        check("| #" not in shown and "@voisin" not in shown, "no rank, no text")
        check(".s." not in shown and ".f." not in shown and "[" not in shown, "no id, no key")
        check(play_g("status", "--all").returncode == 0 and play_g("status", tid_g("le-fil-deux"), "--all").returncode == 0,
              "the ledger by id")
        K.refused(bench, play_g("status", "le-fil-deux"), "thread-addressed-by-name")
        K.refused(bench, play_g("done", "le-fil-deux", fini), "thread-addressed-by-name")

    with K.case(bench, "the age is the time elapsed", "now, minutes, hours and minutes, > 1 day, days, weeks, "
                "~months, ~years -- the coarsest unit that still says it; a fresh thread says now") as check:
        at = datetime(2026, 9, 6, 12, 0, 0, tzinfo=timezone.utc)

        def since(**delta) -> str:
            return keeper.ago((at - timedelta(**delta)).isoformat(timespec="microseconds"), at)

        check(since(seconds=30) == "now" and since(minutes=12) == "12 min" and since(minutes=95) == "1h 35 min", "minutes")
        check(since(hours=3) == "3h" and since(hours=24, minutes=56, seconds=12) == "> 1 day" and since(days=3) == "3 days",
              "hours and days")
        check(since(days=10) == "1 week" and since(days=20) == "2 weeks" and since(days=100) == "~3 months", "weeks, months")
        check(since(days=505) == "~1.4 years" and keeper.ago("not-a-stamp", at) == "not-a-stamp", "years, a bad stamp")
        row = K.front(play_g("status", tid_g("le-fil-deux")).stdout).row("le-fil-deux")
        check(row and row.age == "now", f"a fresh thread {row}")

    # --- the ledger of the steps still to do: what the boot serves -------------------------------
    with K.case(bench, "the open ledger", "`status --all --open` keeps each open thread with its id and note and "
                "its steps still to do -- a waiting one with its reason -- and leaves the delivered out; `--open` "
                "alone refuses") as check:
        delivered = record_g()["threads"][banc]["steps"][0]
        check(play_g("done", banc, delivered).returncode == 0, "done")
        opened_text = play_g("status", "--all", "--open").stdout
        whole_text = play_g("status", "--all").stdout
        opened, whole = K.ledger(opened_text), K.ledger(whole_text)
        check(delivered in whole["le-banc"].steps and delivered not in opened["le-banc"].steps, "the delivered left out")
        check(opened["le-banc"].id == banc and opened["le-banc"].note == record_g()["threads"][banc]["note"],
              "the thread with its id and note")
        check(any(line.name == "la-cle-en-chiffres" for line in opened["le-banc"].steps.values()), "a step to do kept")
        waiting = next((line for line in opened["le-temoin"].steps.values() if line.name == "le-defaut-2"), None)
        check(waiting and waiting.mark == "⛔" and waiting.text == "témoin garé ici", f"a waiting one with its reason {waiting}")
        check(len(opened_text) < len(whole_text), "shorter than the ledger")
        check(play_g("status", "--open").returncode == 2, "--open alone refuses")

    with K.case(bench, "a step stands in one open thread at most", "after every move of the case, no step is "
                "listed by two open threads, and each keeps the thread it was born in") as check:
        wrong = K.one_open_thread(alpha) + K.one_open_thread(gamma)
        check(not wrong, " ".join(wrong))
        check(all(ledger_of()["steps"][sid]["thread"] == source for sid in (sp, sa, sk)), "the moved keep their birth")

    return 0
