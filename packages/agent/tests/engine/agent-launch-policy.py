"""Scenario `agent-launch-policy` -- everything decided before a launch:
- the dry run composes and judges, nothing launched: every line a provider bears on is the one
  `conductor.adapters.launch` composes, every provider chosen by what its adapter declares (`SPELLS`,
  `COST`) -- FULL spells the four keys of a policy, BARE lacks the regime, FLAT the effort, never a
  provider's literal. `--dry-run` says the marked `-new` line (no `PP_NEW_KEY`), the composed line, the
  variables, then `--- stdin (<n> chars) ---` and the head of the first prompt; `--run <key>` composes the
  resume for the recorded session; a cap under an adapter whose `COST` is None refuses `budget-unmeasured`;
  `--door` rides an opening alone (`door-on-resume`); `--permissions` and `--effort` name the regime and the
  effort -- a word outside refuses `policy-invalid`, an adapter that lacks the key relays
  `policy-unsupported`; the record keeps the policy the face judged, never the typed text; an opening the
  adapter refuses leaves no slot, no wake lock file, no run in `status`
- the grammar a `--harness` command's output is read in is named by the caller: `run`, `chat` and `start`
  with a `--harness` and no `--provider` refuse `grammar-missing` -- no run opened, no record; the
  grammar named beside it plays, the response kept, the run parked
- the provider's binary is judged before a run opens: a PATH that carries none refuses `harness-missing`,
  naming the binary and the provider; a caller's own command (`--harness`) is not judged
- the receipt rides the principal's own calls: a launch whose adapter declares `PP_MARBLE` (claude, a stub
  on PATH that plays the witness) gets a boot block without the standing orders -- the marble rides the
  CLI's system prompt, the dry run says the receipt on the marked line; the agent's bare `-new` and a
  `--harness` launch (no marble channel) serve them in the block
- `--documents <dir>` gives a run its root of documents, carried by `PP_DOCUMENTS` on the house's `-new`
  alone: the run resolves from the directory, the slot keeps the absolute path; the harness inherits
  nothing; a resume under another root refuses `documents-fixed`, the same root or none plays;
  `chat --json --documents` says the root on `ready`
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path

from conductor import adapters, persistence
from tests.harness import cli, support

A = support(__file__, "agent")
HEAD = A.HEAD
ORDERS = "INFORMATION — standing orders"
ROOTED = "---\nname: ROOTED\nkind: proc\ndescription: a door the root alone carries\nproc: |\n  WORK\n---\n\nThe root's door.\n"


def scenario(bench) -> int:
    dry_run(bench, A.House(bench))         # a run woken to resume, a session written by hand
    grammar(bench, A.House(bench))         # reads a house with nothing on it, then its one run
    pathed = A.House(bench)                # reads no run, then the one its witness opens
    harness_missing(bench, pathed)
    principal_receipt(bench, pathed)       # reads no count: the boot block of an opening, the dry run's line
    documents(bench, A.House(bench))       # its run is the house's first; teams/alpha beside it
    return 0


def dry_run(bench, h) -> None:
    """The launch composed and judged, nothing launched."""
    held, failures = bench.held, bench.failures
    keys, counted, messages = h.keys, h.counted, h.messages
    h.wake("first ask")                                   # one run standing, to resume in the dry runs
    key = keys()[0] if keys() else ""
    full = A.spelling(h.house, "model", "max_budget_usd", "permissions", "effort")
    bare_regime, flat = A.lacking(h.house, "permissions"), A.lacking(h.house, "effort")
    marble = str(h.agent_meta / ".sys" / "system.common.md")

    def composed(provider: str, policy: dict | None = None, session: str | None = None) -> str:
        """-> the line `conductor.adapters.launch` composes for `provider` on this house, as a dry run says it."""
        return shlex.join(adapters.launch(provider, h.agent_ws, h.agent_meta, "x", wiring=h.ws, marble=Path(marble),
                                          policy=policy or None, session=session)[0])

    # --- --dry-run composes, launches nothing ---------------------------------------------------------
    runs_before, recorded = len(keys()), counted()
    dry = h.call("agent", "run", "agents/ag1", "--provider", full, "--model", "m", "--max-budget-usd", "0.5",
                 "--message", "never sent", "--dry-run")
    product = adapters.product_of(h.house) / "adapters"
    unmeasured = next((one.name for one in sorted(product.iterdir()) if (one / "wire.py").is_file()
                       and getattr(adapters.load(one.name, h.house), "COST", "absent") is None), "")
    refused = h.call("agent", "run", "agents/ag1", "--provider", unmeasured, "--max-budget-usd", "0.5", "--dry-run")
    budgeted = composed(full, {"model": "m", "max_budget_usd": 0.5})
    with (h.records / "sessions.jsonl").open("a", encoding="utf-8") as handle:   # a session of FULL no model makes here
        handle.write(json.dumps({"at": "2026-09-27T00:00:00+00:00", "agent": "agents/ag1", "run": key,
                                 "provider": full, "session": "S"}) + "\n")
    resume = h.call("agent", "run", "agents/ag1", "--run", key, "--provider", full, "--message", "later", "--dry-run")
    resumed = composed(full, session="S")
    new_line = next((one for one in dry.stdout.splitlines() if " -new " in one), "")
    resume_line = next((one for one in resume.stdout.splitlines() if f" {key} " in one and "--instance" in one), "")
    if (full and dry.returncode == 0 and budgeted in dry.stdout.splitlines()
            and resumed not in dry.stdout.splitlines() and str(h.agent_ws) in dry.stdout
            and new_line.startswith("PP_CONDUCTED_BY_PRINCIPAL=true ") and new_line.endswith("-new 'never sent'")
            and "PP_NEW_KEY" not in dry.stdout and "PP_NEW_KEY" not in resume.stdout
            and unmeasured and refused.returncode == 2 and "budget-unmeasured" in refused.stderr
            and unmeasured in refused.stderr
            and resume.returncode == 0 and resumed in resume.stdout.splitlines() and " -new " not in resume.stdout
            and resume_line.startswith("PP_CONDUCTED_BY_PRINCIPAL=true ") and resume_line.endswith(f"{key} later")
            and len(keys()) == runs_before
            and (len(h.responses()), len(messages()), len(h.sessions()) - 1) == recorded):
        held("--dry-run composes and launches nothing", f"the opening: the marked -new line, the {full} line "
             "conductor.adapters.launch composes for the policy, the house's wiring and the marble of the mode, no "
             "PP_NEW_KEY; the resume: the marked `<key> <message>` line and the line composed for the recorded session; "
             f"a cap under {unmeasured} (COST None) refuses budget-unmeasured; no run, no record")
    else:
        failures.append(f"  ✗ dry run                     {dry.returncode}/{refused.returncode}/{resume.returncode} "
                        f"new={new_line[-80:]!r} resume={resume_line[-80:]!r} {dry.stdout[-300:]!r} {resume.stderr[-160:]!r}")

    # --- --dry-run says the prompt apart: the lines, then the head of the first prompt ---------------------
    said_line = next((one for one in dry.stdout.splitlines() if one == budgeted), "")
    stdin_at = dry.stdout.find("--- stdin (")
    if (said_line and "never sent" not in said_line and stdin_at > 0
            and re.search(r"^--- stdin \(\d+ chars\) ---$", dry.stdout, re.M)
            and f"{HEAD}\nnever sent\n\n" in dry.stdout[stdin_at:] and dry.stdout.index("  env ") < stdin_at):
        held("--dry-run says the prompt apart", "the composed line without the message, the variables, then "
             "`--- stdin (<n> chars) ---` and the head of the first prompt: the message under its head, then where "
             "pp's output goes")
    else:
        failures.append(f"  ✗ dry run stdin               line={said_line[-80:]!r} at={stdin_at} {dry.stdout[-200:]!r}")

    # --- --door rides an opening alone ---------------------------------------------------------------
    counted_before = (len(keys()), len(h.responses()), len(messages()))
    doored = h.call("agent", "run", "agents/ag1", "--provider", full, "--message", "never sent",
                    "--dry-run", "--door", "DAILY.md")
    door_line = next((one for one in doored.stdout.splitlines() if " -new " in one), "")
    on_resume = h.call("agent", "run", "agents/ag1", "--run", key, "--provider", full,
                       "--message", "later", "--door", "DAILY.md")
    if (doored.returncode == 0 and "PP_DOOR=DAILY.md " in door_line
            and on_resume.returncode == 2 and "door-on-resume" in on_resume.stderr
            and (len(keys()), len(h.responses()), len(messages())) == counted_before):
        held("--door rides an opening alone", "the dry run says PP_DOOR=DAILY.md on the -new line; --door with "
             "--run refuses door-on-resume before anything is launched")
    else:
        failures.append(f"  ✗ door flag                   {doored.returncode}/{on_resume.returncode} "
                        f"{door_line!r} {on_resume.stderr[-200:]!r}")

    # --- --permissions names the regime ------------------------------------------------------------
    runs_before, recorded = len(keys()), counted()

    def dry_with(*regime: str, provider: str = full):
        return h.call("agent", "run", "agents/ag1", "--provider", provider, "--message", "never sent", "--dry-run", *regime)

    plain, strict, bypass = dry_with(), dry_with("--permissions", "strict"), dry_with("--permissions", "bypass")
    wrong = dry_with("--permissions", "yolo")
    elsewhere = dry_with("--permissions", "strict", provider=bare_regime)
    regimes = [composed(full), composed(full, {"permissions": "strict"}), composed(full, {"permissions": "bypass"})]
    if (plain.returncode == 0 and regimes[0] in plain.stdout.splitlines()
            and strict.returncode == 0 and regimes[1] in strict.stdout.splitlines()
            and bypass.returncode == 0 and regimes[2] in bypass.stdout.splitlines() and len(set(regimes)) == 3
            and wrong.returncode == 2 and "policy-invalid" in wrong.stderr and "permissions" in wrong.stderr
            and bare_regime and elsewhere.returncode == 2 and "policy-unsupported" in elsewhere.stderr
            and bare_regime in elsewhere.stderr
            and len(keys()) == runs_before and counted() == recorded):
        held("--permissions names the regime", f"the {full} line composed without it, under strict, under bypass -- "
             f"three lines apart; yolo refuses policy-invalid, {bare_regime} relays policy-unsupported; nothing launched")
    else:
        failures.append(f"  ✗ permissions flag            {plain.returncode}/{strict.returncode}/{bypass.returncode}/"
                        f"{wrong.returncode}/{elsewhere.returncode} {plain.stdout[-200:]!r} {strict.stdout[-200:]!r} "
                        f"{bypass.stdout[-200:]!r} {wrong.stderr[-160:]!r} {elsewhere.stderr[-160:]!r}")

    # --- the record keeps the judged policy -----------------------------------------------------------
    judged = h.wake("judged", "play", "--max-budget-usd", "1.00", "--permissions", "strict")
    kept = messages()[-1] if messages() else {}
    if (judged.returncode == 0 and kept.get("message") == "judged"
            and kept.get("policy") == {"max_budget_usd": 1.0, "permissions": "strict"}
            and isinstance(kept["policy"]["max_budget_usd"], float)):
        held("the record keeps the judged policy", "--max-budget-usd 1.00 --permissions strict kept as "
             f"{kept.get('policy')} -- the types the face judged, never the typed text")
    else:
        failures.append(f"  ✗ judged record               rc={judged.returncode} {kept} {judged.stderr[-200:]!r}")

    # --- --effort names the model's effort ----------------------------------------------------------
    runs_before, recorded = len(keys()), counted()
    high = dry_with("--effort", "high")
    turbo = dry_with("--effort", "turbo")
    flat_effort = dry_with("--effort", "high", provider=flat)
    unlaunched = len(keys()) == runs_before and counted() == recorded
    efforted = h.wake("with effort", "play", "--effort", "high")
    kept = messages()[-1] if messages() else {}
    if (high.returncode == 0 and composed(full, {"effort": "high"}) in high.stdout.splitlines()
            and turbo.returncode == 2 and "policy-invalid" in turbo.stderr and "effort" in turbo.stderr
            and flat and flat_effort.returncode == 2 and "policy-unsupported" in flat_effort.stderr
            and flat in flat_effort.stderr and unlaunched
            and efforted.returncode == 0 and kept.get("message") == "with effort"
            and kept.get("policy") == {"effort": "high"}):
        held("--effort names the model's effort", f"the {full} line composed under high; turbo refuses "
             f"policy-invalid, {flat} relays policy-unsupported, nothing launched; the wake-up keeps "
             f"{kept.get('policy')}")
    else:
        failures.append(f"  ✗ effort flag                 {high.returncode}/{turbo.returncode}/{flat_effort.returncode}/"
                        f"{efforted.returncode} {high.stdout[-200:]!r} {turbo.stderr[-160:]!r} "
                        f"{flat_effort.stderr[-160:]!r} unlaunched={unlaunched} {kept}")

    # --- an opening the adapter refuses leaves no run behind ----------------------------------------------------
    runs_before = sorted(keys())
    state_dir = h.agent_meta / persistence.DIRECTORY
    files_before = sorted(one.name for one in state_dir.glob("session-*"))
    listed_runs = lambda: sorted(re.findall(r"^run ([0-9a-f]{6}) ·", h.call("agent", "status", "agents/ag1").stdout, re.M))
    shown_before = listed_runs()
    refused_open = h.call("agent", "run", "agents/ag1", "--provider", flat, "--effort", "low", "--message", "x")
    if (refused_open.returncode == 2 and "policy-unsupported" in refused_open.stderr
            and sorted(keys()) == runs_before
            and sorted(one.name for one in state_dir.glob("session-*")) == files_before
            and listed_runs() == shown_before):
        held("an opening the adapter refuses leaves no run", f"policy-unsupported ({flat}, effort): no run opened, "
             "no wake lock file, status says no ghost run")
    else:
        failures.append(f"  ✗ refused opening             rc={refused_open.returncode} {refused_open.stderr[-160:]!r} "
                        f"keys={sorted(set(keys()) - set(runs_before))} "
                        f"files={sorted(set(one.name for one in state_dir.glob('session-*')) - set(files_before))}")


def grammar(bench, h) -> None:
    """The grammar a `--harness` command's output is read in, named by the caller beside it."""
    held, failures = bench.held, bench.failures

    # --- run: a --harness alone refuses ---------------------------------------------------------------
    alone = h.call("agent", "run", "agents/ag1", "--message", "read me", "--harness", h.harness("play"))
    if alone.returncode == 2 and "grammar-missing" in alone.stderr and h.keys() == [] and h.counted() == (0, 0, 0):
        bench.refusals += 1
        held("run: a --harness without --provider refuses", "grammar-missing, exit 2, no run opened, no record")
    else:
        failures.append(f"  ✗ run grammar-missing         rc={alone.returncode} keys={h.keys()} records={h.counted()} "
                        f"{alone.stderr[-300:]!r}")

    # --- chat: refused before any message -------------------------------------------------------------
    talked = h.call("agent", "chat", "agents/ag1", "--harness", h.harness("play"), stdin="hi\n")
    if talked.returncode == 2 and "grammar-missing" in talked.stderr and h.keys() == [] and h.counted() == (0, 0, 0):
        bench.refusals += 1
        held("chat: a --harness without --provider refuses", "grammar-missing before any message, nothing opened")
    else:
        failures.append(f"  ✗ chat grammar-missing        rc={talked.returncode} keys={h.keys()} records={h.counted()} "
                        f"{talked.stderr[-300:]!r}")

    # --- start: the child's refusal relayed -----------------------------------------------------------
    started = h.call("agent", "start", "agents/ag1", "--message", "read me", "--harness", h.harness("play"))
    if (started.returncode == 2 and "grammar-missing" in started.stderr and started.stdout.strip() == ""
            and h.keys() == [] and h.counted() == (0, 0, 0)):
        bench.refusals += 1
        held("start: the refusal relayed", "grammar-missing on stderr, no report, nothing opened")
    else:
        failures.append(f"  ✗ start grammar-missing       rc={started.returncode} out={started.stdout[-120:]!r} "
                        f"keys={h.keys()} records={h.counted()} {started.stderr[-300:]!r}")

    # --- the grammar named: the exchange plays ---------------------------------------------------------
    named = h.wake("read me")
    kept = h.responses()
    if (named.returncode == 0 and len(h.keys()) == 1 and len(kept) == 1
            and kept[0].get("response") == "witness answer: play"):
        held("the grammar named beside the harness plays", f"run {h.keys()[0]}: the witness's answer kept, read in "
             f"the grammar its support declares")
    else:
        failures.append(f"  ✗ grammar named               rc={named.returncode} keys={h.keys()} "
                        f"responses={[one.get('response') for one in kept]} {named.stderr[-300:]!r}")


def harness_missing(bench, h) -> None:
    """The provider's binary, judged before a run is opened."""
    held, failures = bench.held, bench.failures
    provider = A.providers(h.house)[0]
    binary = adapters.launch(provider, h.agent_ws, h.agent_meta, "x", marble=h.agent_meta / ".sys" / "system.common.md")[0][0]
    bare_path = str(Path(sys.executable).parent)       # the interpreter alone: no provider's CLI stands there
    before = h.counted()

    # --- (a) the provider's binary absent --------------------------------------------------------------
    refused = h.call("agent", "run", "agents/ag1", "--message", "hi", "--provider", provider,
                     extra={"PATH": bare_path})
    if (refused.returncode == 2 and "harness-missing" in refused.stderr and binary in refused.stderr
            and provider in refused.stderr and not h.keys() and h.counted() == before):
        held("(a) harness-missing before the opening", f"`{binary}` absent from the PATH: refused by name, no run, "
             "no record")
    else:
        failures.append(f"  ✗ (a) missing                  rc={refused.returncode} {refused.stderr[-240:]!r} "
                        f"keys={h.keys()} counted={h.counted()}")

    # --- (b) a caller's command is the caller's -----------------------------------------------------------
    played = h.call("agent", "run", "agents/ag1", "--message", "hi", *h.harnessed("play"),
                    extra={"PATH": bare_path + os.pathsep + os.environ.get("PATH", "")})
    if played.returncode == 0 and "· parked ·" in played.stderr and len(h.keys()) == 1:
        held("(b) a caller's command is not judged", "the witness under --harness plays, the run parked")
    else:
        failures.append(f"  ✗ (b) harness                  rc={played.returncode} {played.stderr[-200:]!r}")


def principal_receipt(bench, h) -> None:
    """The receipt of the marble, carried by the principal's own calls."""
    held, failures = bench.held, bench.failures

    # a `claude` on PATH: the witness in `play` mode, claude's own arguments after the witness's
    stubs = bench.temp() / "bin"
    stubs.mkdir()
    out = bench.temp() / "claude-prompt"
    (stubs / "claude").write_text(f"#!/bin/sh\nexec {sys.executable} {h.witness} {h.engine} {h.agent_meta} play {out} \"$@\"\n",
                                  encoding="utf-8")
    (stubs / "claude").chmod(0o755)
    on_path = {"PATH": f"{stubs}{os.pathsep}{os.environ.get('PATH', '')}"}

    dry = h.call("agent", "run", "agents/ag1", "--message", "hello", "--provider", "claude", "--dry-run", extra=on_path)
    woken = h.call("agent", "run", "agents/ag1", "--message", "hello", "--provider", "claude", extra=on_path)
    prompt = h.read("", out)
    seen = h.environment(out)
    if (woken.returncode == 0 and "1 launch(es)" in woken.stderr and "▌ pp · run" in prompt
            and ORDERS not in prompt and seen.get("PP_MARBLE") == "1"
            and dry.returncode == 0 and "PP_CONDUCTED_BY_PRINCIPAL=true PP_MARBLE=1 " in dry.stdout):
        held("the receipt rides the principal's calls", f"claude's launch declares PP_MARBLE: the boot block handed to "
             f"the CLI ({len(prompt)} chars) carries no standing orders -- the marble is at the system prompt; "
             "the dry run says the receipt on the marked line")
    else:
        failures.append(f"  ✗ receipt at the principal    rc={woken.returncode}/{dry.returncode} orders={ORDERS in prompt} "
                        f"env={seen} {woken.stderr[-240:]!r} {dry.stdout[-200:]!r}")

    bare = cli(h.engine, "--instance", str(h.agent_meta), "-new", cwd=h.agent_ws, env=h.env)
    plain = h.wake("hello again")
    harnessed = h.read()
    if bare.returncode == 0 and ORDERS in bare.stdout and plain.returncode == 0 and ORDERS in harnessed:
        held("without the receipt the block carries them", "the agent's bare -new (the console, no mark) and a "
             "--harness launch (no marble channel) both serve the standing orders in the block")
    else:
        failures.append(f"  ✗ without the receipt         rc={bare.returncode}/{plain.returncode} bare={ORDERS in bare.stdout} "
                        f"harness={ORDERS in harnessed} {bare.stderr[-160:]!r}")


def documents(bench, h) -> None:
    """`--documents <dir>`: a run's root of documents, on the house's `-new` alone."""
    held, failures = bench.held, bench.failures
    root = h.ws / "teams" / "alpha"
    root.mkdir(parents=True)
    (root / "ROOTED.md").write_text(ROOTED, encoding="utf-8")
    other = h.ws / "teams" / "beta"
    other.mkdir(parents=True)

    # --- (a) an opening under --documents resolves from the directory ----------------------------------
    opened = h.wake("first ask", "play", "--documents", "teams/alpha", "--door", "ROOTED.md")
    key = h.keys()[0] if h.keys() else ""
    slot = persistence.slot_of(h.agent_meta, key) if key else None
    kept = persistence.documents_of(slot) if slot is not None and hasattr(persistence, "documents_of") else ""
    doors = [one.get("document") for one in h.trace(key) if one.get("kind") == "door"] if key else []
    if opened.returncode == 0 and kept == str(root) and doors == ["ROOTED.md"]:
        held("(a) an opening under --documents", f"run {key}: the door ROOTED.md of teams/alpha opens; the slot "
             "keeps the absolute path")
    else:
        failures.append(f"  ✗ (a) the opening               rc={opened.returncode} kept={kept!r} doors={doors} "
                        f"{opened.stderr[-300:]!r}")

    # --- (b) the harness inherits nothing -----------------------------------------------------------
    seen = h.environment()
    if opened.returncode == 0 and h.read(".env") and "PP_DOCUMENTS" not in seen:
        held("(b) the harness inherits nothing", "the witness's environment carries no PP_DOCUMENTS")
    else:
        failures.append(f"  ✗ (b) the harness's environment rc={opened.returncode} "
                        f"documents={seen.get('PP_DOCUMENTS')!r} keys={len(seen)}")

    # --- (c) a resume keeps its root -------------------------------------------------------------------
    before = h.counted()
    moved = h.call("agent", "run", "agents/ag1", "--run", key, "--message", "later", "--documents", str(other),
                   *h.harnessed("play")) if key else None
    after_moved = h.counted()
    same = h.call("agent", "run", "agents/ag1", "--run", key, "--message", "again", "--documents", str(root),
                  *h.harnessed("play")) if key else None
    bare = h.call("agent", "run", "agents/ag1", "--run", key, "--message", "once more",
                  *h.harnessed("play")) if key else None
    if (moved is not None and moved.returncode == 2 and "documents-fixed" in moved.stderr
            and after_moved == before and same.returncode == 0 and bare.returncode == 0):
        bench.refusals += 1
        held("(c) a resume keeps its root", "another root: documents-fixed before any launch, the records "
             "unchanged; the same root and none play")
    else:
        failures.append(f"  ✗ (c) documents-fixed           moved={moved and moved.returncode} "
                        f"same={same and same.returncode} bare={bare and bare.returncode} "
                        f"records={before}->{after_moved} {(moved.stderr if moved else '')[-200:]!r}")

    # --- (d) the conversation says its root ------------------------------------------------------------
    chat = h.call("agent", "chat", "agents/ag1", "--json", "--documents", "teams/alpha",
                  *h.harnessed("play"), stdin="")
    ready = {}
    for line in chat.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("kind") == "ready":
            ready = event
            break
    if chat.returncode == 0 and ready.get("documents") == str(root):
        held("(d) the conversation says its root", "chat --json --documents teams/alpha: `ready` says the "
             "absolute directory")
    else:
        failures.append(f"  ✗ (d) ready                     rc={chat.returncode} ready={ready} {chat.stderr[-200:]!r}")
