"""Scenario `print-owed` -- a step said on `terminal` is OWED from its rendering to the print call
that answers it (`./pp <key> -print <DOCUMENT> -`, the production piped):
- (a) a door of three free steps and a proof renders ONE output carrying the
  three lines `=> terminal`; the run's state holds three prints due, the trace three `print-due` and no
  `batched`; three print calls naming the document, each answered by the short line of
  `messages.PRINTED`, leave on the trace three `answer` of channel `terminal` whose `given` is the
  text handed, byte for byte, in the order of the steps, and no print due; the proof then plays -- the
  prints and the proof typed by the agent, under the run its launcher names
- (g) a door opened from a step due stands for its production: the step's print is due no more from the
  opening, which traces the debt lifted `print-by-door` (never `print-waived`: nothing was missed); the
  door's block, never served, is held and served by the principal's bare call; the door's own values are
  judged, and its exit traces `consumed-by-door`
- (h) a step asked alone is answered by its print: the run moves on, the next block -- never served --
  held, the print's call answered by the held line, the principal's bare call serving it
- (f) a proof joins the output of its prints: two callees' lines and the door's own, then the proof in
  the same output -- three prints due, each answered by the line that names the call due next, the
  proof then judged and its output held -- the prints due after it are those the held output says on
  `terminal`, none of the door's; a door closed by a `§` behind a callee's line holds the output its one
  print moves the run to (no value asked), where the door's own step, said on `terminal`, is due first,
  with every step that output says on `terminal` behind it
- (c) a turn with a contributor holds in one launch: a WORK, a HOOK that
  injects a free step, a proof -- ONE output carries the two lines `=> terminal`, then the proof; two
  prints due, each answered by the line that names the call due next, no `pending` and no `inline` on the
  trace; the proof judged is held
- (d) a gesture in the middle loses nothing: one print, a mount, then `-peek` -- the block the mount
  brings back (held, its matter new, served by the principal's bare call) and the view carry the line of
  each step still due, the state holds them after each act
- (e) a space opened then closed closes no print due: the state holds them after each gesture, the block
  the closing brings back -- held, served by the principal's bare call -- carries their lines
"""
from __future__ import annotations

from conductor.core import messages
from conductor import Conductor, persistence
from conductor.core import language
from tests.harness import cli, support

run = support(__file__, "run")

PRINTS = getattr(persistence, "PRINTS", "prints")            # the key of the prints due, at the run's state
LEAF = "---\nname: {name}\nkind: proc\ndescription: a witness\nproc: |\n  INFER\n---\n{name} speaks\n"
TRIO = ("---\nname: TRIO\nkind: proc\ndescription: two callees' lines and its own, then a proof\n"
        "constraints.production: |\n  Z1  say it plainly\n"
        "proc: |\n  CALL ALPHA.md\n  CALL BRAVO.md\n  INFER\n  PROVE\n---\nTRIO speaks\n")
THREE = ("---\nname: THREE\nkind: proc\ndescription: three said steps of one document, then a proof\n"
         "tools: |\n  +ROOM\nconstraints.production: |\n  Z1  say it plainly\n"
         "proc: |\n  WORK\n  INFER\n  INFER\n  PROVE\n---\nTHREE speaks\n")
TOUR = ("---\nname: TOUR\nkind: proc\ndescription: a turn with a contributor\n"
        "constraints.production: |\n  Z1  say it plainly\n"
        "proc: |\n  WORK\n  HOOK tour.end\n  PROVE\n---\nTOUR works\n")
ECHO = ("---\nname: ECHO\nkind: proc\ndescription: a contributor behind the work\nattach: tour.end\n"
        "proc: |\n  INFER\n---\nECHO speaks\n")
SECT = ("---\nname: SECT\nkind: proc\ndescription: a callee's line, a section break, a step\n"
        "proc: |\n  CALL ALPHA.md\n  §\n  INFER\n---\nSECT speaks\n")
DOORED = ("---\nname: DOORED\nkind: proc\ndescription: a step asked alone, a door offered to it\nfusion: 1\n"
          "tools: |\n  +SIDE\nconstraints.production: |\n  Z1  say it plainly\n"
          "proc: |\n  WORK\n  PROVE\n---\nDOORED works\n")
SIDE = ("---\nname: SIDE\nkind: proc\ndescription: a door that stands for the step\n"
        "constraints.production: |\n  Y1  say it plainly\nproc: |\n  INFER\n  PROVE\n---\nSIDE speaks\n")
ROOM = "---\nname: ROOM\nkind: proc\ndescription: a space\nproc: |\n  WORK\n---\nROOM works\n"
EXT = "---\nname: EXT\nkind: doc\n---\n\nthe mounted matter\n"
MOUNT = '[{"doc": "EXT.md", "body": true}]'


def _text(name: str) -> str:
    """-> a production of several lines: an indented one, a blank one."""
    return f"{name} line one\n  an indented second line\n\nthe last line, after a blank"


def _line(keyword: str, name: str) -> str:
    return f"{keyword} any {run.SAID}{name})"


def _agent(env, key: str, *words, stdin: str | None = None):
    """-> the AGENT's call on the run: under the run its launcher names."""
    return cli(env.engine, key, *words, cwd=env.root, stdin=stdin, env=run.agent(key))


def _principal(env, key: str, *words):
    """-> the principal's call on the run."""
    return cli(env.engine, key, *words, cwd=env.root)


def _printed(env, key: str, name: str, said: str = ""):
    return _agent(env, key, "-print", name, "-", stdin=_text(said or name) + "\n")


def _due(env, key: str) -> list:
    """-> the documents of the prints due at the run's state, in order."""
    return [one.get("document") for one in run.slot(env, key).get(PRINTS) or [] if isinstance(one, dict)]


def _owed(env, key: str) -> list:
    """-> the `print-due` events of the run, in order: one per step said on `terminal`."""
    return [one for one in run.trace(env, key) if one.get("kind") == "print-due"]


def _captured(env, key: str) -> list:
    return [one.get("given") for one in run.trace(env, key)
            if one.get("kind") == "answer" and one.get("channel") == language.TERMINAL]


def three(bench, env, label: str) -> None:
    """Three steps of one document owed in one output, three prints captured as handed, then the proof."""
    held, failures = bench.held, bench.failures
    said = ("first", "second", "third")
    key, first = run.opened(env, "THREE.md")
    more = [messages.printed("more", messages.next_print("THREE"))] * 2 + [
        messages.printed("more", messages.next_value("THREE", key, True))]   # each names the call due next
    counts = (first.stdout.count(_line("WORK", "THREE")), first.stdout.count(_line("INFER", "THREE")))
    due, owed, kinds = _due(env, key), _owed(env, key), run.kinds(env, key)
    answers = [_printed(env, key, "THREE", one) for one in said]
    left = _due(env, key)
    proved = _agent(env, key, "-", stdin=run.proof_of(first.stdout))
    if (key and first.returncode == 0 and counts == (1, 2) and run.CODES.search(first.stdout)
            and due == ["THREE"] * 3 and len(owed) == 3 and "batched" not in kinds
            and [one.stdout.strip() for one in answers] == more and all(one.returncode == 0 for one in answers)
            and _captured(env, key) == [_text(one) for one in said] and not left
            and proved.returncode == 0 and "repair" not in run.kinds(env, key)):
        held(f"({label}) three steps owed in one output", f"run {key}: three lines on `terminal` and the proof's, "
             "three prints due at the state, three `print-due` and no `batched`; each print answered by the line "
             "that names the call due next -- the next print, then the proof's value --, its text on the trace as handed, byte for byte, in the order of the steps; nothing due "
             "left, the proof plays")
    else:
        failures.append(f"  ✗ ({label}) three owed          rc={first.returncode} lines={counts} "
                        f"due={due} owed={len(owed)} batched={'batched' in kinds} "
                        f"answers={[(one.returncode, one.stdout.strip()[:60], one.stderr.strip()[-80:]) for one in answers]} "
                        f"captured={len(_captured(env, key))} left={left} proved={proved.returncode} "
                        f"{first.stderr[-600:]!r}")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("print-owed")
    for name in ("ALPHA", "BRAVO"):
        env.write(f"procs/{name}.md", LEAF.format(name=name))
    for name, text in (("TRIO", TRIO), ("THREE", THREE), ("SECT", SECT), ("TOUR", TOUR), ("ECHO", ECHO), ("ROOM", ROOM),
                       ("DOORED", DOORED), ("SIDE", SIDE)):
        env.write(f"procs/{name}.md", text)
    env.write("EXT.md", EXT)
    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 60000\n"
                             "instructions_fusion: max\n---\n")
    # --- (a) three steps owed in one output ----------------------------------------------------------
    three(bench, env, "a")

    # --- (c) a turn with a contributor holds in one launch ----------------------------------------------
    key, first = run.opened(env, "TOUR.md")
    work, echo = _line("WORK", "TOUR"), _line("INFER", "ECHO")
    due = _due(env, key)
    printed = _printed(env, key, "TOUR")
    moved = _printed(env, key, "ECHO")
    kinds, left = run.kinds(env, key), _due(env, key)
    proved = _agent(env, key, "-", stdin=run.proof_of(first.stdout))
    codes = run.CODES.search(first.stdout)
    if (key and first.returncode == 0 and first.stdout.count(work) == 1 and first.stdout.count(echo) == 1
            and codes and first.stdout.index(work) < first.stdout.index(echo) < codes.start()
            and not [name for name in ("TOUR", "ECHO") if f"any => {language.RESPONSE}  ({name})" in first.stdout]
            and due == ["TOUR", "ECHO"]
            and printed.returncode == 0 and printed.stdout.strip() == messages.printed("more", messages.next_print("ECHO"))
            and moved.returncode == 0 and moved.stdout.strip() == messages.printed("more", messages.next_value("TOUR", key, True))
            and "inline" not in kinds
            and proved.returncode == 0 and proved.stdout.strip() == messages.held("value")
            and "pending" not in kinds and "repair" not in run.kinds(env, key)
            and _captured(env, key) == [_text("TOUR"), _text("ECHO")] and not left):
        held("(c) a turn with a contributor holds in one launch", f"run {key}: the WORK, the step the HOOK "
             "injects and the proof in the output the opening serves, the two lines on `terminal`; two prints "
             "due, each answered by the line that names the call due next, no `pending`, no `inline`; the proof is "
             "judged and its output held")
    else:
        failures.append(f"  ✗ (c) the contributor's turn    rc={first.returncode} work={first.stdout.count(work)} "
                        f"echo={first.stdout.count(echo)} due={due} pending={'pending' in kinds} "
                        f"printed={(printed.returncode, printed.stdout.strip()[:60])} "
                        f"moved={(moved.returncode, moved.stdout.strip()[:60], 'inline' in kinds)} "
                        f"proved={(proved.returncode, proved.stdout.strip()[:40])} left={left} "
                        f"captured={_captured(env, key)} kinds={sorted(set(run.kinds(env, key)))}")

    # --- (d) a gesture in the middle: a print, a mount, a peek ------------------------------------------
    key, first = run.opened(env, "THREE.md")
    left, gone = _line("INFER", "THREE"), _line("WORK", "THREE")
    kept = ["THREE", "THREE"]
    printed = _printed(env, key, "THREE", "first")
    gesture = _agent(env, key, "-mount", MOUNT)
    after_mount = _due(env, key)
    mounted = _principal(env, key)             # the mounted view, held: the principal's bare call serves it
    peeked = _agent(env, key, "-peek")
    after_peek = _due(env, key)
    proof = run.CODES.search(mounted.stdout)
    if (key and printed.returncode == 0 and after_mount == after_peek == kept
            and gesture.returncode == 0 and gesture.stdout.strip() == messages.held("mount")
            and mounted.returncode == 0 and mounted.stdout.count(left) == 2 and gone not in mounted.stdout
            and proof and mounted.stdout.rindex(left) < proof.start()
            and peeked.returncode == 0 and peeked.stdout.count(left) == 2 and gone not in peeked.stdout):
        held("(d) a gesture in the middle loses nothing", f"run {key}: one print, a mount, a peek -- two prints "
             "due at the state after each; the block the mount brings back, held then served, and the view carry their two lines "
             "on `terminal` before the proof's, the line of the step printed gone")
    else:
        failures.append(f"  ✗ (d) the gesture in the middle  printed={printed.returncode} {printed.stdout.strip()[:60]!r} "
                        f"mounted={mounted.returncode} due={after_mount}/{after_peek} "
                        f"mount={mounted.stdout.count(left)} peek={peeked.stdout.count(left)} "
                        f"{mounted.stdout[-300:]!r} {peeked.stderr[-120:]!r}")

    # --- (e) a space opened then closed closes no print due ----------------------------------------------
    key, first = run.opened(env, "THREE.md")
    printed = _printed(env, key, "THREE", "first")
    opened = _agent(env, key, "-open", "ROOM")
    in_space = _due(env, key)
    closed = _agent(env, key, "-close")
    back = _due(env, key)
    served = _principal(env, key)           # the block the closing brings back, held: the principal's call serves it
    if (key and printed.returncode == 0 and opened.returncode == 0 and closed.returncode == 0
            and [one for one in in_space if one == "THREE"] == kept and [one for one in back if one == "THREE"] == kept
            and served.stdout.count(left) == 2 and gone not in served.stdout):
        held("(e) a space closes no print due", f"run {key}: ROOM opened then closed over two prints due -- "
             "both at the state in the space and back from it, their lines in the block the closing brings back")
    else:
        failures.append(f"  ✗ (e) the space                  printed={printed.returncode} opened={opened.returncode} "
                        f"{opened.stderr[-120:]!r} closed={closed.returncode} {closed.stderr[-120:]!r} "
                        f"due={in_space}/{back} lines={served.stdout.count(left)} {served.stdout[-200:]!r}")

    # --- (g) a door opened from a step due stands for its production -----------------------------------------
    key, first = run.opened(env, "DOORED.md")
    asked = _due(env, key)
    opened = _agent(env, key, "-s", "SIDE")
    in_door = _due(env, key)
    door = _principal(env, key)               # the door's block, never served, held: the principal serves it
    said = _printed(env, key, "SIDE")
    proved = _agent(env, key, "-", stdin=run.proof_of(door.stdout))
    kinds = run.kinds(env, key)
    if (key and asked == ["DOORED"] and opened.returncode == 0 and opened.stdout.strip() == messages.held("door")
            and door.returncode == 0 and run.CODES.search(door.stdout) and in_door == ["SIDE"]
            and said.returncode == 0 and said.stdout.strip() == messages.printed("more", messages.next_value("SIDE", key, True))
            and proved.returncode == 0 and "consumed-by-door" in kinds and "stray" not in kinds
            and kinds.count("print-by-door") == 1 and "print-waived" not in kinds
            and _captured(env, key) == [_text("SIDE")]):
        held("(g) a door stands for the step it is opened from", f"run {key}: DOORED's WORK due, then SIDE opened "
             "from it -- the debt lifted is traced `print-by-door`, once, never as a debt waived; the door's block "
             "held, served by the principal; the door's own "
             "step alone is due, its print captured, its proof judged (no stray), and its exit traced "
             "`consumed-by-door`")
    else:
        failures.append(f"  ✗ (g) the door from a step due   asked={asked} door={door.returncode} {door.stderr[-120:]!r} "
                        f"in_door={in_door} said={(said.returncode, said.stdout.strip()[:50])} "
                        f"proved={proved.returncode} consumed={'consumed-by-door' in kinds} stray={'stray' in kinds} "
                        f"by-door={kinds.count('print-by-door')}")

    # --- (h) a step asked alone is answered by its print ------------------------------------------------------
    key, first = run.opened(env, "DOORED.md")
    answered = _printed(env, key, "DOORED")
    served = _principal(env, key)             # the proof's block, never served, held: the principal serves it
    if (key and _line("WORK", "DOORED") in first.stdout and answered.returncode == 0
            and answered.stdout.strip() == messages.held("value")
            and served.returncode == 0 and run.CODES.search(served.stdout) and not _due(env, key)
            and _captured(env, key) == [_text("DOORED")]):
        held("(h) a step asked alone is answered by its print", f"run {key}: DOORED's WORK, asked alone on "
             "`terminal` -- its print moves the run to the proof's block, held, the principal's bare call "
             "serves it, nothing due left")
    else:
        failures.append(f"  ✗ (h) a step asked alone         printed={(answered.returncode, answered.stdout.strip()[:60])} "
                        f"served={served.stdout[-120:]!r} "
                        f"due={_due(env, key)}")

    # --- (f) a proof joins the output of its prints -------------------------------------------------------
    names = ("ALPHA", "BRAVO", "TRIO")
    lines = [_line("INFER", name) for name in names]
    key_p, first_p = run.opened(env, "TRIO.md")
    due_p = _due(env, key_p)
    answers_p = [_printed(env, key_p, name) for name in names]
    proved_p = _agent(env, key_p, "-", stdin=run.proof_of(first_p.stdout))
    codes_p = run.CODES.search(first_p.stdout)
    key_s, first_s = run.opened(env, "SECT.md")
    due_s = _due(env, key_s)
    crossed = _printed(env, key_s, "ALPHA")
    held_s = bool(run.slot(env, key_s).get(persistence.HELD))
    served_s = _principal(env, key_s)                     # the held output, served by the principal's bare call
    served_p = _principal(env, key_p)
    if (key_s and due_s == ["ALPHA"] and first_s.stdout.count(lines[0]) == 1
            and crossed.returncode == 0 and crossed.stdout.strip() == messages.held("value")
            and held_s and run.said(served_s.stdout)[:1] == ["SECT"] and _due(env, key_s) == run.said(served_s.stdout)
            and key_p and all(first_p.stdout.count(one) == 1 for one in lines)
            and codes_p and first_p.stdout.index(lines[2]) < codes_p.start()
            and due_p == list(names)
            and [one.stdout.strip() for one in answers_p] == [
                messages.printed("more", messages.next_print("BRAVO")), messages.printed("more", messages.next_print("TRIO")),
                messages.printed("more", messages.next_value("TRIO", key_p, True))]
            and not set(names) & set(_due(env, key_p)) and _due(env, key_p) == run.said(served_p.stdout)
            and proved_p.returncode == 0 and "repair" not in run.kinds(env, key_p)
            and _captured(env, key_p) == [_text(name) for name in names]
            and proved_p.stdout.strip() == messages.held("value")):
        held("(f) a proof joins the output of its prints", f"run {key_p}: the three lines and the proof in one "
             "output, three prints due, each answered by the line that names the call due next, the proof judged and "
             "its output held")
    else:
        failures.append(f"  ✗ (f) closed on its prints       lines={[first_p.stdout.count(one) for one in lines]} "
                        f"proof={bool(codes_p)} proved={proved_p.returncode} "
                        f"captured={_captured(env, key_p) == [_text(name) for name in names]} "
                        f"sect={first_s.stdout.count(lines[0])} held={held_s} "
                        f"left_s={_due(env, key_s)}/{run.said(served_s.stdout)} "
                        f"left_p={_due(env, key_p)}/{run.said(served_p.stdout)} "
                        f"section: due={due_s} crossed={(crossed.returncode, crossed.stdout.strip()[:50])} "
                        f"principal: due={due_p} "
                        f"answers={[(one.returncode, one.stdout.strip()[:50]) for one in answers_p]}")
    return 0
