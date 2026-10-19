"""Scenario `documents-root` -- the root of documents a LAUNCHER gives a run (plan core, phase
l-etat, batch la-racine-de-documents-du-run, 2026-10-10). `PP_DOCUMENTS=<absolute dir>` is
read by `-new` alone and kept at the slot; for THAT run the directory is one more space of
documents, between the instance's own and the packages':
- a name only the root carries resolves: the launcher's door, a CALL of another root document
  (the instance never names the root's: the build judges its CALLs without any root)
- a document of the root declares: its `attach: boot.ready` is played at the boot
- a document of the root named as a base is its overlay: its law rides the base's block
- the root holds from one call to the next: a keyed advance, `-peek`, `-compacted`, and the
  reopening after an upgrade's renewal mark
- another run of the instance, opened without it, sees nothing of it, and renders what a
  throwaway that never had a root renders
- what is badly given refuses `documents-unknown` at `-new` (a relative path, a missing one,
  a file), nothing written; a keyed call naming ANOTHER root refuses `documents-fixed`
- the decider of a root document names a PACKAGE's skill, and its successor follows
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from conductor import persistence
from tests.harness import cli, support

shared = support(__file__, "run")
ROOTED = "---\nname: ROOTED\nkind: proc\ndescription: a document the root alone carries\nproc: |\n  WORK\n---\n\nThe root's own document.\n"
HOOKED = "---\nname: HOOKED\nkind: proc\ndescription: a root contributor at the boot\nattach: boot.ready\nproc: |\n  WORK\n---\n\nThe root's contributor.\n"
TURN_OVERLAY = "---\nname: TURN\nconstraints.behavior: |\n  RT1  the root's law rides the turn.\n---\n"
CALLER = "---\nname: CALLER\nkind: proc\ndescription: a root document that calls another\nproc: |\n  CALL ROOTED.md\n---\n\nThe caller.\n"
DECIDED = ("---\nname: DECIDED\nkind: proc\ndescription: a root document whose successor a package's skill decides\n"
           "next: LEFT.md RIGHT.md\ndecide: pp-motor decide RIGHT.md\nproc: |\n  INFER\n---\n\nDecide.\n")
LEFT = "---\nname: LEFT\nkind: proc\ndescription: the successor not taken\nproc: |\n  WORK\n---\n\nLeft.\n"
RIGHT = "---\nname: RIGHT\nkind: proc\ndescription: the successor the skill names\nproc: |\n  WORK\n---\n\nRight.\n"


def _root(files: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp())
    for name, text in files.items():
        (root / name).write_text(text, encoding="utf-8")
    return root


def _trace(made: Path, key: str) -> list[dict]:
    return [json.loads(line)
            for log in sorted((made / ".sys" / "state").glob(f"session-*-{key}.jsonl"))
            for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("documents-root")
    root = _root({"ROOTED.md": ROOTED, "HOOKED.md": HOOKED, "TURN.md": TURN_OVERLAY, "CALLER.md": CALLER})
    given = {"PP_DOCUMENTS": str(root)}

    def run(*args, extra: dict | None = None, stdin: str | None = None):
        return cli(env.engine, *args, cwd=env.root, stdin=stdin, env=extra or {})

    # --- the root declares and amends: its attach plays, its overlay's law rides -----------------
    opened = run("-new", extra=given)
    key = shared.key_of(opened.stdout)
    slot = persistence.slot_of(env.made, key) if key else None
    new_line = next((one for one in _trace(env.made, key) if one.get("kind") == "new"), {}) if key else {}
    if opened.returncode == 0 and "▸ HOOKED" in opened.stdout:
        held("an attach of the root plays", f"run {key}: `attach: boot.ready` of HOOKED.md, in the root alone")
    else:
        failures.append(f"  ✗ the root's attach             rc={opened.returncode} {opened.stdout[-300:]!r} "
                        f"{opened.stderr[-200:]!r}")
    amending = _root({"TURN.md": TURN_OVERLAY})
    amended = run("-new", extra={"PP_DOCUMENTS": str(amending)})
    if amended.returncode == 0 and "RT1" in amended.stdout and "▸ TURN" in amended.stdout:
        held("a document of the root is an overlay", "TURN.md of the root: its law RT1 rides the stand-in's TURN")
    else:
        failures.append(f"  ✗ the root's overlay           rc={amended.returncode} {amended.stdout[-300:]!r}")
    at_slot = persistence.documents_of(slot) if slot is not None and hasattr(persistence, "documents_of") else ""
    if at_slot == str(root) and new_line.get("documents") == str(root):
        held("the root is kept at the slot", "the slot and the trace's `new` line say the directory")
    else:
        failures.append(f"  ✗ the root at the slot          slot={at_slot!r} new={new_line}")

    # --- a name the root alone carries resolves: the door, a CALL ------------------------------------
    doored = run("-new", extra={**given, "PP_DOOR": "ROOTED.md"})
    called = run("-new", extra={**given, "PP_DOOR": "CALLER.md"})
    if doored.returncode == 0 and "▸ ROOTED" in doored.stdout:
        held("the door resolves in the root", "PP_DOOR=ROOTED.md, a document of the root alone, opens")
    else:
        failures.append(f"  ✗ the root's door               rc={doored.returncode} {doored.stderr[-200:]!r}")
    if called.returncode == 0 and "▸ ROOTED" in called.stdout:
        held("a CALL resolves in the root", "CALLER.md calls ROOTED.md, both in the root alone")
    else:
        failures.append(f"  ✗ the root's CALL              rc={called.returncode} {called.stdout[-300:]!r} "
                        f"{called.stderr[-200:]!r}")

    # --- the root holds from one call to the next ----------------------------------------------------
    door_key = shared.key_of(doored.stdout)
    peeked = run(door_key, "-peek") if door_key else None
    advanced = run(door_key) if door_key else None
    compacted = run(door_key, "-compacted") if door_key else None
    if (peeked is not None and peeked.returncode == 0 and "ROOTED" in peeked.stdout
            and advanced.returncode == 0 and "▸ HOOKED" in advanced.stdout
            and compacted.returncode == 0 and "▸ HOOKED" in compacted.stdout):
        held("the root holds across the calls", f"run {door_key}, no variable: -peek stands on ROOTED, the "
             "advance reaches HOOKED of the root, -compacted serves it again")
    else:
        failures.append(f"  ✗ the root across the calls     peek={peeked and peeked.returncode} "
                        f"advance={advanced and advanced.returncode} compacted={compacted and compacted.returncode} "
                        f"{(advanced.stdout if advanced else '')[-400:]!r} "
                        f"{(compacted.stdout if compacted else '')[-400:]!r}")
    if slot is not None and slot.exists():
        persistence.renew(slot, {"kit": "0"}, {"kit": "1"}, "2026-10-10T00:00:00Z")
        mark = persistence.renewed(slot) or {}
        reopened = run(key)
        kept = persistence.documents_of(slot) if hasattr(persistence, "documents_of") else ""
        if (mark.get("documents") == str(root) and reopened.returncode == 0
                and "▸ HOOKED" in reopened.stdout and kept == str(root)):
            held("the renewal keeps the root", f"run {key}: the mark carries it, the reopened boot plays HOOKED")
        else:
            failures.append(f"  ✗ the root through a renewal    mark={mark.get('documents')!r} kept={kept!r} "
                            f"rc={reopened.returncode} {reopened.stderr[-200:]!r}")
    else:
        failures.append("  ✗ the root through a renewal    no slot to renew")

    # --- another run sees nothing of it, and renders what a run that never had one renders ----------
    blind = run("-new", extra={"PP_DOOR": "ROOTED.md"})
    plain = run("-new")
    other = bench.env("documents-never")
    never = cli(other.engine, "-new", cwd=other.root, env={})
    lines = [out.stdout.replace(shared.key_of(out.stdout) or "?", "KEY").replace(str(where), "WS").splitlines()[1:]
             for out, where in ((plain, env.root), (never, other.root))]
    if blind.returncode == 2 and "door-unknown" in blind.stderr:
        held("another run does not see the root", "PP_DOOR=ROOTED.md without PP_DOCUMENTS: door-unknown")
    else:
        failures.append(f"  ✗ the root seen by another run  rc={blind.returncode} {blind.stdout[-200:]!r}")
    if plain.returncode == 0 and lines[0] and lines[0] == lines[1] and "HOOKED" not in plain.stdout:
        held("a run without a root renders as before", f"{len(lines[0])} lines identical to a throwaway that "
             "never had a root")
    else:
        drift = next((i for i, (a, b) in enumerate(zip(*lines)) if a != b), None)
        failures.append(f"  ✗ a run without a root         rc={plain.returncode} lines={len(lines[0])}/{len(lines[1])} "
                        f"drift={drift}")

    # --- what is badly given refuses ------------------------------------------------------------------
    a_file = root / "ROOTED.md"
    verdicts = []
    for value in ("relative/dir", str(root / "absent"), str(a_file)):
        before = len(persistence.slots(env.made))
        refused = run("-new", extra={"PP_DOCUMENTS": value})
        verdicts.append(refused.returncode == 2 and "documents-unknown" in refused.stderr
                        and len(persistence.slots(env.made)) == before)
        bench.refusals += refused.returncode == 2
    if all(verdicts):
        held("a bad root refuses at -new", "relative, missing, a file: documents-unknown, no slot written")
    else:
        failures.append(f"  ✗ documents-unknown            {verdicts}")
    elsewhere = _root({})
    moved = run(door_key, "-peek", extra={"PP_DOCUMENTS": str(elsewhere)}) if door_key else None
    same = run(door_key, "-peek", extra=given) if door_key else None
    if (moved is not None and moved.returncode == 2 and "documents-fixed" in moved.stderr
            and same.returncode == 0):
        bench.refusals += 1
        held("a run keeps the root it opened", "a keyed call naming another root: documents-fixed; the same "
             "root plays")
    else:
        failures.append(f"  ✗ documents-fixed              moved={moved and moved.returncode} "
                        f"same={same and same.returncode} {(moved.stderr if moved else '')[-200:]!r}")

    # --- the decider of a root document names a package's skill -------------------------------------
    driven = bench.env("documents-root-motor", packages=("motor",))
    decided_root = _root({"DECIDED.md": DECIDED, "LEFT.md": LEFT, "RIGHT.md": RIGHT})
    started = cli(driven.engine, "-new", cwd=driven.root,
                  env={"PP_DOCUMENTS": str(decided_root), "PP_DOOR": "DECIDED.md"})
    decided_key = shared.key_of(started.stdout)
    answered = (cli(driven.engine, decided_key, cwd=driven.root, env={})
                if decided_key else None)
    nexts = [one for one in _trace(driven.made, decided_key) if one.get("kind") == "next"] if decided_key else []
    if (answered is not None and answered.returncode == 0 and "▸ RIGHT" in answered.stdout
            and nexts and nexts[-1].get("by") == "skill" and nexts[-1].get("successor") == "RIGHT.md"):
        held("a root document's decider names a package's skill", "`decide: pp-motor decide RIGHT.md`: the "
             "skill of motor prints RIGHT.md, the successor plays")
    else:
        failures.append(f"  ✗ the root's decider            start={started.returncode} "
                        f"answer={answered and answered.returncode} next={nexts} "
                        f"{started.stderr[-200:]!r} {(answered.stdout if answered else '')[-300:]!r}")
    return 0
