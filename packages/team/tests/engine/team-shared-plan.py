"""Scenario `team-shared-plan` -- 8 case(s): the WITNESS of a plan shared by the members of a team (plan
0.3.0, batch plan/le-plan-partage/le-temoin-d-equipe). One house pinning `agent`, `team` and `plan`; one team,
`shared`: `fa` the root, `pa` and `pb` its delegates, `parallel: 3`, a `work:` repository, its season switching
`plan` on for every member (`--package plan=on`: the season decides a member's packages). Every member's wake-up
opens its run under the team's directory, the ROOT OF DOCUMENTS; the witness holds each launch at a gate while the
bench plays `pp-plan` on that run through the console, as the member itself would -- never on a run the bench
opened, never on an instance by hand. Each member prints its act before its gate: fa its `do`, the delegates their
answers; fa answers at its next launch.
- (a) the birth: `section s Context --shared` on fa's run births the plan under `teams/shared/plans/`, its lock
  beside it; no member's instance carries a `plans/`
- (b) the delivery from the other run: pa frames a phase and a batch of `s` and delivers its todo by the
  batch's Delivery (`--item t1`) -- todo, batch, phase and plan close by the cascade; `status s` from fa's run says
  `shared` and `done`; last, pa mounts `s` through the console; the run being conducted by its launcher, the view
  is held for the launcher's call, and the engine's ledger of that block serves the documents `mount_chain` names,
  in its order -- the plan's own document resolved at the team's directory --, `pp-plan` offered (a mounted plan
  offers `pp-plan` at two segments, so the mount comes last)
- (c) two writers at once: pa and pb write two sections of a second shared plan `s2` at the same moment; both
  sections land, `check` from fa's run is clean
- (d) the launcher's material declared: pb's clone stands under `pb/work/<key>`, and `material s2 clone <its path>`
  from pb's run declares it the plan's tree and writes `material: clone` (a plan names the trees it declares,
  `work` none of them: plan 0.3.3)
- (e) `next-move` from fa's run says the node pb opened on `s2`, read from the document, by its vector `plan:s2/ph`
- (f) the journal: one wake-up ended per delegate, two for fa -- its `do`, then its answer printed at the launch
  its delegates' answers wake --, no `wake-failed`, T1 resolved by fa's answer
- (g) the mass: `-stats <key> --blocks` of pa's run renders; the mount of `s` carried the documents of its chain (b), its
  block's weight read from the ledger
"""
from __future__ import annotations

import json
import re
import subprocess
import threading
import time
from pathlib import Path

from conductor import instance
from tests.harness import cli, load_script, support

T = support(__file__, "team")
KEY = re.compile(r"^▌ pp · run ([0-9a-f]{6})", re.M)
MOUNTED = re.compile(r"pp-plan: (\d+) documents for s\b")
BODY = "shared-team-plan-5"          # one token: what the mount must show, never a sentence
TEXT = "a section of the witness."


def _repository(bench) -> Path:
    """-> a throwaway git repository, the team's `work:`."""
    target = bench.temp() / "target"
    subprocess.run(["git", "init", "-q", str(target)], check=True)
    (target / "README").write_text("the target\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(target), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(target), "-c", "user.name=bench", "-c", "user.email=bench@bench.local",
                    "commit", "-q", "-m", "the target"], check=True)
    return target


def _key_of(h, member: str, timeout: float = 60.0) -> str:
    """-> the key of the run the member's first wake-up opened, read from the prompt the witness kept."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        prompts = h.prompts_of(member)
        found = KEY.search(prompts[0]) if prompts else None
        if found:
            return found.group(1)
        time.sleep(0.1)
    return ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    gates = {name: bench.temp() / f"gate-{name}" for name in ("fa", "pa", "pb")}
    h = T.House(bench, packages=("agent", "team", "plan"), script={
        "fa": [{"sleep": 0.1, "words": [{"do": ["pa", "pb"]}, {"gate": str(gates["fa"])}]},
               {"sleep": 0.1, "body": {"re": "DO", "text": "the shared plan is delivered"}}],
        "pa": [{"sleep": 0.1, "words": [{"re": "DO", "text": "pa delivered"}, {"gate": str(gates["pa"])}]}],
        "pb": [{"sleep": 0.1, "words": [{"re": "DO", "text": "pb wrote"}, {"gate": str(gates["pb"])}]}]})
    by_kind, all_ended = T.by_kind, T.all_ended
    repository = _repository(bench)
    h.declare("shared", "---\nagents: |\n  fa agents/fa\n  pa agents/pa\n  pb agents/pb\nreports: |\n"
                        "  pa pb -> fa\nroot: fa\nparallel: 3\nschedule: off\n---\n"
                        "Share one plan.\n")
    (h.teams / "shared" / "SEASON.md").write_text(f"---\nwork: {repository}\n---\n", encoding="utf-8")   # the season's material
    started = h.call("team", "start", "shared", "--message", "frame and deliver the shared plan", *h.harnessed,
                     "--package", "plan=on")   # the season decides: plan plays for every member
    keys = {name: _key_of(h, name) for name in ("fa", "pa", "pb")}   # the three runs alive at their gates

    def play(member: str, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
        """`pp-plan <args>` on the member's run, through the console -- the member's own gesture."""
        return cli(h.engine, "--instance", str(h.meta_of(f"agents/{member}")), keys[member], "-s", "pp-plan",
                   *args, cwd=h.ws, env=h.env, stdin=stdin)

    def section(member: str, address: str, name: str, text: str = TEXT, *flags: str) -> subprocess.CompletedProcess:
        return play(member, "section", address, name, *flags, stdin=text + "\n")

    # --- (a) the birth under the team's directory -----------------------------------------------------
    born = section("fa", "s", "Context", BODY, "--shared")
    for name, text in (("Ground", TEXT), ("Expected", TEXT), ("Choices", TEXT), ("Items", "- ph -- the phase")):
        section("fa", "s", name, text)
    plans_dir = h.teams / "shared" / "plans"
    at_members = [str(one) for member in ("fa", "pa", "pb") for one in [h.meta_of(f"agents/{member}") / "plans"]
                  if one.exists()]
    if (started.returncode == 0 and all(keys.values()) and born.returncode == 0
            and (plans_dir / "s" / "PLAN.md").is_file() and (plans_dir / "s.lock").is_file() and not at_members):
        held("(a) the birth under the team's directory", f"fa's run {keys['fa']} births s under teams/shared/plans/, "
             "the lock beside it; no member's instance carries a plans/")
    else:
        failures.append(f"  ✗ (a) the birth                  rc={started.returncode}/{born.returncode} keys={keys} "
                        f"plan={(plans_dir / 's' / 'PLAN.md').is_file()} lock={(plans_dir / 's.lock').is_file()} "
                        f"at_members={at_members} {born.stderr[-300:]!r} {started.stderr[-200:]!r}")

    # --- (b) framed and delivered from pa's run; then mounted ------------------------------------------------
    for name, text in (("Ground", TEXT), ("Expected", TEXT), ("Choices", TEXT), ("Items", "- bt -- the batch")):
        section("pa", "s/ph", name, text)
    for name, text in (("Ground", TEXT), ("Expected", TEXT), ("Tests", TEXT), ("Choices", TEXT),
                       ("Items", "- t1 -- the todo")):
        section("pa", "s/ph/bt", name, text)
    delivered = section("pa", "s/ph/bt", "Delivery", "landed", "--item", "t1")
    seen = play("fa", "status", "s")
    first = seen.stdout.splitlines()[0] if seen.stdout.strip() else ""
    if (delivered.returncode == 0 and "pp-plan: s/ph/bt/t1 -> done" in delivered.stdout
            and "closes s/ph, s" in delivered.stdout and (plans_dir / "s" / "1-ph" / "1-bt" / "BATCH.md").is_file()
            and seen.returncode == 0 and first.split()[:4] == ["s", "plan", "done", "shared"]):
        held("(b) delivered from the other run", f"pa's run {keys['pa']} frames s/ph and s/ph/bt, delivers t1 "
             f"by the Delivery: todo, batch, phase and plan close; status s from fa's run: {first!r}")
    else:
        failures.append(f"  ✗ (b) delivered from pa          delivery={delivered.returncode} "
                        f"{delivered.stdout[-200:]!r} {delivered.stderr[-200:]!r} status={first!r} {seen.stderr[-200:]!r}")

    # --- (c) two writers at once on a second shared plan ------------------------------------------------
    second = section("fa", "s2", "Context", "two writers", "--shared")
    answers: dict[str, subprocess.CompletedProcess] = {}
    writers = [threading.Thread(target=lambda m=member, n=name: answers.__setitem__(m, section(m, "s2", n)))
               for member, name in (("pa", "Ground"), ("pb", "Expected"))]
    for one in writers:
        one.start()
    for one in writers:
        one.join()
    body = (plans_dir / "s2" / "PLAN.md").read_text(encoding="utf-8") if (plans_dir / "s2" / "PLAN.md").is_file() else ""
    clean = play("fa", "check")
    if (second.returncode == 0 and all(one.returncode == 0 for one in answers.values())
            and "## Ground" in body and "## Expected" in body and clean.returncode == 0):
        held("(c) two writers at once", "pa's and pb's runs write Ground and Expected of s2 at the same moment: both "
             "sections land under the plan's lock, check clean from fa's run")
    else:
        failures.append(f"  ✗ (c) two writers                 rc={second.returncode} "
                        f"{ {m: one.returncode for m, one in answers.items()} } ground={'## Ground' in body} "
                        f"expected={'## Expected' in body} check={clean.returncode} {clean.stderr[-200:]!r}")

    # --- (d) the launcher's material ---------------------------------------------------------------------
    clone = h.ws / "agents" / "pb" / "work" / keys["pb"]
    material = play("pb", "material", "s2", "clone", str(clone))
    front = (plans_dir / "s2" / "PLAN.md").read_text(encoding="utf-8").split("\n---\n", 1)[0] if body else ""
    if material.returncode == 0 and "material: clone" in front and clone.is_dir():
        held("(d) the material declared", f"pb's run declares its clone {clone.relative_to(h.ws)} the tree `clone` "
             "of s2 and writes material: clone")
    else:
        failures.append(f"  ✗ (d) the material declared      rc={material.returncode} front={'material: clone' in front} "
                        f"clone={clone.is_dir()} {material.stderr[-200:]!r}")

    # --- (e) the next move read from the document ---------------------------------------------------------
    section("pb", "s2", "Choices")
    section("pb", "s2", "Items", "- ph -- the phase")
    moves = play("fa", "next-move")
    lines = [one for one in moves.stdout.splitlines() if one.endswith("(plan:s2/ph)")]
    if moves.returncode == 0 and len(lines) == 1 and not [one for one in moves.stdout.splitlines() if "plan:s)" in one]:
        held("(e) next-move says what pb did", "from fa's run, the line of s2 names the phase pb prepared "
             "(plan:s2/ph), read from the document; s, done, has no line")
    else:
        failures.append(f"  ✗ (e) next-move                  rc={moves.returncode} lines={moves.stdout.splitlines()} "
                        f"{moves.stderr[-200:]!r}")

    # --- (b) the mount from pa's run, last: a mounted plan offers pp-plan at two segments ------------------------
    mounted = play("pa", "mount", "s")
    # the run is conducted by its launcher: the view is HELD for the launcher's call and served at pa's next
    # launch -- what the bench reads is the engine's own ledger of that block (its served lines, origin
    # `mount`: the documents of the plan's chain, its own resolved at the team's directory) and the block that
    # stands under `-peek`, where `pp-plan` is offered and the plan's own law is in force
    peeked = cli(h.engine, "--instance", str(h.meta_of("agents/pa")), keys["pa"], "-peek", cwd=h.ws, env=h.env)
    chain = MOUNTED.search(mounted.stdout)
    blocks = [one for one in h.trace_kinds("agents/pa", keys["pa"]) if one.get("kind") == "block"
              and any(line.get("origin") == "mount" for line in one.get("served") or [])]
    served = [line for one in blocks[-1:] for line in one.get("served") or [] if line.get("origin") == "mount"]
    documents = [(line.get("by"), line.get("package"), int(line.get("chars") or 0)) for line in served]
    offered = re.search(r"^\[([^\]]*)\]$", peeked.stdout, re.M)
    offers = offered.group(1).split() if offered else []
    # the chain the script commands for `s`, read from its own `mount_chain`: the name of each document mounted,
    # in its order, and its package -- the plan's own document, under `plans/`, read as the repository's
    plans = load_script(instance.bundle_of(h.house, "plan") / "skills" / "pp-plan" / "pp-plan.py")
    commanded = plans.mount_chain(h.teams / "shared", ["s"])
    owed = [Path(one["doc"].rpartition(":")[2]).name for one in commanded]
    owners = ["repository" if one["doc"].startswith("plans/") else "plan" for one in commanded]
    if (mounted.returncode == 0 and chain and chain.group(1) == str(len(owed))
            and [by for by, _, _ in documents] == owed
            and [package for _, package, _ in documents] == owners
            and all(chars > 0 for _, _, chars in documents)
            and peeked.returncode == 0 and "pp-plan" in offers):
        weight = (blocks[-1].get("weight") or {}) if blocks else {}
        held("(b) the mount from pa's run", f"`-s pp-plan mount s` on pa's run: {len(owed)} documents, the view held "
             "for the launcher; the ledger of that block serves by origin mount the documents of mount_chain, in its order -- "
             f"{', '.join(f'{by} of {package} ({chars} c)' for by, package, chars in documents)}, the plan's own "
             f"document read as the repository's; the block stands at {weight.get('total')} c, "
             f"{weight.get('tokens')} tokens, pp-plan offered")
    else:
        failures.append(f"  ✗ (b) the mount                  rc={mounted.returncode}/{peeked.returncode} "
                        f"chain={chain.group(1) if chain else None} documents={documents} owed={list(zip(owed, owners))} offers={offers} "
                        f"{mounted.stderr[-200:]!r} {peeked.stdout[:400]!r}")

    # --- the gates open: the delegates answer, fa closes T1 ----------------------------------------------------
    for name in ("pa", "pb", "fa"):
        gates[name].write_text("open", encoding="utf-8")
    ended = h.settled("shared", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    time.sleep(1.0)                                          # the last on-end tick writes after the response
    found = h.events("shared")

    # --- (f) the journal ---------------------------------------------------------------------------------
    ends = sorted(one.get("agent") for one in by_kind(found, "wake-ended"))
    fails = [(one.get("agent"), one.get("reason")) for one in by_kind(found, "wake-failed")]
    if ended and ends == ["fa", "fa", "pa", "pb"] and not fails and T.result_of(found, "T1") == "the shared plan is delivered":
        held("(f) the journal", f"wake-ended for {ends}, no wake-failed, T1 resolved by fa's answer")
    else:
        failures.append(f"  ✗ (f) the journal                ended={ended} ends={ends} fails={fails} "
                        f"result={T.result_of(found, 'T1')!r}")

    # --- (g) the mass of pa's outputs ------------------------------------------------------------------------
    stats = cli(h.engine, "--instance", str(h.meta_of("agents/pa")), "-stats", keys["pa"], "--blocks", cwd=h.ws, env=h.env)
    if stats.returncode == 0 and stats.stdout.strip():
        held("(g) the mass by -stats --blocks", f"pa's run {keys['pa']}: {len(stats.stdout.splitlines())} lines of blocks "
             "rendered; the mount of s carried the documents of its chain (b)")
    else:
        failures.append(f"  ✗ (g) the mass                   rc={stats.returncode} {stats.stderr[-200:]!r}")
    print(stats.stdout)                                      # the figures for the batch's Delivery, under -detail
    return 0
