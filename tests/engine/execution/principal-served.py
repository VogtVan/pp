"""Scenario `principal-served` -- 12 case(s) (plan core, batch la-remise, rework of 2026-10-11): in a
run its principal conducts, EVERY block the engine renders on the agent's call -- not the value
alone -- leaves through one seam and is HELD at the run until the principal's bare call serves it;
the agent's tool return carries what the act answers and one neutral line. A script's own text and
a refusal are answers: they reach the caller in both modes. One output is held at a time.
- (a) `-mount`: one neutral line, no block; the mount written and the hold at the slot (`act:
  mount`); the principal's bare call serves the view
- (b) a script's `::mount`: the script's text in the tool return, the view held
- (c) a script called bare: its manual held (`act: manual`)
- (d) a routed door: its frame pushed, its block held (`act: door`)
- (e) `-compacted`: the re-serve held (`act: compacted`)
- (f) `-disable`: the fact in the tool return, the package out of the play, the block held
- (g) `-peek`: the view held (`act: view`)
- (h) an offer not at this step: exit 2, the block and its DEVIATION held (`act: denied`)
- (i) while an output is held, a mount, a re-serve, a peek, a switch and a value bounce: nothing
  played, the slot byte-identical
- (j) the same mount at the same step: the LLM mode's tool return and the principal's served
  output are the same matter, their closings apart
- (k) the LLM's mode is today's: every site renders its block in the tool return, nothing held
- (l) one seam: no line of the console prints `.rendered(` or `.shown(` itself
"""
from __future__ import annotations

import json
import re

from conductor import persistence
from tests.harness import cli

MARK = {"PP_CONDUCTED_BY_PRINCIPAL": "true"}
KEY = re.compile(r"run ([0-9a-f]{6})")
PROVER = ("---\nname: PROVER\nkind: proc\ndescription: a witness\ntools: |\n  pp-probe\n  SIDE\n"
          "constraints.production: |\n  Z1  say it plainly\nproc: |\n  WORK\n---\nprove\n")
SIDE = "---\nname: SIDE\nkind: proc\ndescription: a side door\nproc: |\n  WORK\n---\nthe side door's brief\n"
EXT = "---\nname: EXT\nkind: doc\n---\n\nthe mounted matter\n"
CONTRACT = "---\nname: pp-probe\ndescription: a witness script that mounts\n---\n\nthe probe's manual\n"
PROBE = ("def main(argv):\n"
         "    print('::mount [{\"doc\": \"EXT.md\", \"body\": true}]')\n"
         "    print('probe: chain derived')\n"
         "    return 0\n")
GOOD = '[{"code": "Z1", "evidence": "said plainly", "verdict": "ok"}]'


def _env(bench, name: str, packages=()):
    env = bench.env(name, packages)
    env.write("procs/PROVER.md", PROVER)
    env.write("procs/SIDE.md", SIDE)
    env.write("EXT.md", EXT)
    env.write("skills/pp-probe/SKILL.md", CONTRACT)
    env.write("skills/pp-probe/pp-probe.py", PROBE)
    return env


def _opened(env, marked: bool = True) -> str:
    out = cli(env.engine, "-new", cwd=env.root, env={"PP_DOOR": "PROVER.md", **(MARK if marked else {})})
    found = KEY.search(out.stdout)
    return found.group(1) if found else ""


def _slot(env, key: str) -> dict:
    path = persistence.slot_of(env.made, key)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _held(env, key: str) -> dict:
    return _slot(env, key).get("held") or {}


def _agent(env, key: str, *words, stdin: str | None = None):
    return cli(env.engine, key, *words, cwd=env.root, stdin=stdin)


def _principal(env, key: str):
    return cli(env.engine, key, cwd=env.root, env=MARK)


def _one_line(out) -> bool:
    return "▌" not in out.stdout and out.stdout.strip().count("\n") <= 1


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    one = _env(bench, "ps-acts", ("wit",))
    key = _opened(one)

    # --- (a) -mount -------------------------------------------------------------------------------
    mounted = _agent(one, key, "-mount", '[{"doc": "EXT.md", "body": true}]')
    hold = _held(one, key)
    docs = [entry.get("doc") for entry in _slot(one, key).get("mounted", [])]
    served = _principal(one, key)
    if (mounted.returncode == 0 and mounted.stdout.startswith("pp: mounted --") and _one_line(mounted)
            and hold.get("act") == "mount" and "EXT.md" in docs
            and "▌" in served.stdout and "the mounted matter" in served.stdout and not _held(one, key)):
        held("(a) `-mount` is held", "one neutral line back, the mount and the hold at the slot, the "
             "principal's call serves the view with the mounted matter")
    else:
        failures.append(f"  ✗ (a) -mount                  rc={mounted.returncode} {mounted.stdout[:160]!r} "
                        f"act={hold.get('act')!r} docs={docs}")

    # --- (b) a script's ::mount ----------------------------------------------------------------------
    gesture = _agent(one, key, "-s", "pp-probe", "go")
    hold = _held(one, key)
    _principal(one, key)
    if (gesture.returncode == 0 and "probe: chain derived" in gesture.stdout and "▌" not in gesture.stdout
            and "pp: mounted --" in gesture.stdout and hold.get("act") == "mount"
            and "the mounted matter" in hold.get("matter", "")):
        held("(b) a script's `::mount`", "its own text in the tool return, the view held")
    else:
        failures.append(f"  ✗ (b) ::mount                 rc={gesture.returncode} {gesture.stdout[:200]!r} "
                        f"act={hold.get('act')!r}")

    # --- (c) a script called bare: its manual ------------------------------------------------------------
    manual = _agent(one, key, "-s", "pp-probe")
    hold = _held(one, key)
    _principal(one, key)
    if (manual.returncode == 0 and _one_line(manual) and hold.get("act") == "manual"
            and "the probe's manual" in hold.get("matter", "")):
        held("(c) a bare script's manual is held", "one line back, the manual at the slot")
    else:
        failures.append(f"  ✗ (c) manual                  rc={manual.returncode} {manual.stdout[:160]!r} "
                        f"act={hold.get('act')!r}")

    # --- (g) -peek ------------------------------------------------------------------------------------
    peeked = _agent(one, key, "-peek")
    hold = _held(one, key)
    _principal(one, key)
    if peeked.returncode == 0 and _one_line(peeked) and hold.get("act") == "view" and hold.get("matter"):
        held("(g) `-peek` is held", "one line back, the view at the slot")
    else:
        failures.append(f"  ✗ (g) -peek                   rc={peeked.returncode} {peeked.stdout[:160]!r} "
                        f"act={hold.get('act')!r}")

    # --- (h) an offer not at this step ---------------------------------------------------------------
    stray = _agent(one, key, "-s", "NOBODY")
    hold = _held(one, key)
    _principal(one, key)
    if (stray.returncode == 2 and _one_line(stray) and hold.get("act") == "denied"
            and "NOBODY" in hold.get("matter", "")):
        held("(h) a denied offer is held", "exit 2, one line back, the block and its DEVIATION at the slot")
    else:
        failures.append(f"  ✗ (h) denied                  rc={stray.returncode} {stray.stdout[:160]!r} "
                        f"act={hold.get('act')!r}")

    # --- (f) -disable -------------------------------------------------------------------------------------
    switched = _agent(one, key, "-disable", "wit")
    hold = _held(one, key)
    off = _slot(one, key).get("off") or []
    _principal(one, key)
    if (switched.returncode == 0 and "`wit` off" in switched.stdout and "▌" not in switched.stdout
            and "wit" in off and hold.get("act") == "switch"):
        held("(f) `-disable`: the fact answered, the block held", "the fact in the tool return, `wit` "
             "out of the play, the block at the slot")
    else:
        failures.append(f"  ✗ (f) -disable                rc={switched.returncode} {switched.stdout[:160]!r} "
                        f"off={off} act={hold.get('act')!r}")
    _agent(one, key, "-enable", "wit")
    _principal(one, key)

    # --- (i) one hold at a time ------------------------------------------------------------------------
    _agent(one, key, "-peek")
    frozen = persistence.slot_of(one.made, key).read_bytes()
    bounced = [_agent(one, key, *call) for call in (("-mount", '[{"doc": "EXT.md"}]'), ("-compacted",),
                                                     ("-peek",), ("-disable", "wit"))]
    bounced.append(_agent(one, key, "-", stdin=GOOD))
    same = persistence.slot_of(one.made, key).read_bytes() == frozen
    _principal(one, key)
    if all(out.returncode == 0 and "held for your principal" in out.stdout and "▌" not in out.stdout
           for out in bounced) and same:
        held("(i) one output held at a time", "a mount, a re-serve, a peek, a switch and a value bounce, "
             "the slot byte-identical")
    else:
        failures.append(f"  ✗ (i) the bounces             {[(o.returncode, o.stdout[:60]) for o in bounced]} same={same}")

    # --- (e) -compacted --------------------------------------------------------------------------------
    compacted = _agent(one, key, "-compacted")
    hold = _held(one, key)
    _principal(one, key)
    if compacted.returncode == 0 and _one_line(compacted) and hold.get("act") == "compacted":
        held("(e) `-compacted` is held", "one line back, the re-serve at the slot")
    else:
        failures.append(f"  ✗ (e) -compacted              rc={compacted.returncode} {compacted.stdout[:160]!r} "
                        f"act={hold.get('act')!r}")

    # --- (d) a routed door ------------------------------------------------------------------------------
    frames = len(_slot(one, key).get("frames", []))
    door = _agent(one, key, "-s", "SIDE")
    hold = _held(one, key)
    pushed = len(_slot(one, key).get("frames", []))
    _principal(one, key)
    if (door.returncode == 0 and _one_line(door) and hold.get("act") == "door" and pushed > frames
            and "the side door's brief" in hold.get("matter", "")):
        held("(d) a routed door is held", f"one line back, the frame pushed ({frames} -> {pushed}), its "
             "block at the slot")
    else:
        failures.append(f"  ✗ (d) door                    rc={door.returncode} {door.stdout[:160]!r} "
                        f"act={hold.get('act')!r} frames={frames}->{pushed}")

    # --- (j) the same matter in both modes; (k) the LLM's mode is today's ---------------------------------
    llm, led = _env(bench, "ps-llm"), _env(bench, "ps-led")
    key_llm, key_led = _opened(llm, marked=False), _opened(led)
    returned = _agent(llm, key_llm, "-mount", '[{"doc": "EXT.md", "body": true}]')
    _agent(led, key_led, "-mount", '[{"doc": "EXT.md", "body": true}]')
    delivered = _principal(led, key_led)

    def matter(text: str, run: str, root) -> str:
        return text.split("\n▶ ")[0].replace(run, "KEY").replace(str(root), "WS").split("\n", 1)[-1]

    same = matter(returned.stdout, key_llm, llm.root) == matter(delivered.stdout, key_led, led.root)
    if same and "▌" in returned.stdout and "▌" in delivered.stdout:
        held("(j) the same matter in both modes", "the LLM mode's tool return and the principal's served "
             "output agree under the heading")
    else:
        failures.append(f"  ✗ (j) the matter              same={same}")
    gesture_llm = _agent(llm, key_llm, "-s", "pp-probe", "go")
    peek_llm = _agent(llm, key_llm, "-peek")
    if ("▌" in returned.stdout and "▌" in peek_llm.stdout and "probe: chain derived" in gesture_llm.stdout
            and "▌" in gesture_llm.stdout and not _held(llm, key_llm)
            and "pp: mounted" not in returned.stdout + gesture_llm.stdout):
        held("(k) the LLM's mode is today's", "the mount, the script's view and the peek come back in the "
             "tool return, nothing held, no neutral line")
    else:
        failures.append(f"  ✗ (k) the LLM's mode           held={bool(_held(llm, key_llm))} "
                        f"{gesture_llm.stdout[:120]!r}")

    # --- (l) one seam ------------------------------------------------------------------------------------
    console = (bench.source() / "engine" / "pp.py").read_text(encoding="utf-8")
    printed = [n for n, line in enumerate(console.splitlines(), 1)
               if ".rendered(" in line or ".shown(" in line]
    if not printed:
        held("(l) one seam", "no line of engine/pp.py calls `.rendered(` or `.shown(` itself")
    else:
        failures.append(f"  ✗ (l) the seam                lines {printed}")
    return 0
