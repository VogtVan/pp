"""Scenario `agent-dry-run` -- 7 case(s) (batches la-cle-avant-le-lancement and le-mode-de-permission,
2026-09-27, la-politique-du-lancement, rework 2026-10-03, le-rythme-et-les-entrees; split out of
`agent-home` by les-scenarios-par-maison, 2026-10-07): the launch composed and judged, nothing launched.
Every line a provider bears on is the one `conductor.adapters.launch` composes, and every provider is chosen by
what its adapter declares (`SPELLS`, `COST`): FULL spells the four keys of a policy, BARE lacks the regime, FLAT
the effort -- never a provider's literal (KA12).
- `--provider <FULL> --dry-run` composes the opening: the marked `-new` line, the line `launch` composes for the
  policy -- the marble of the mode (`system.common.md`) and the house's wiring with it --, no `PP_NEW_KEY`; a cap
  under an adapter whose `COST` is None refuses `budget-unmeasured`, then `--- stdin (<n> chars) ---` and the head
  of the first prompt; `--dry-run --run <key>` composes the resume: the marked `<key> "<message>"` line and the line
  `launch` composes for the recorded session -- nothing launched
- `--dry-run` says the prompt apart: the composed line without the message, the variables, then the
  stdin line and the head of the first prompt
- `--door <name>` rides an opening alone: the dry run says `PP_DOOR=<name>` on the `-new` line; `--door`
  with `--run` refuses `door-on-resume` before anything is launched
- `--permissions` names the regime: the line is the one `launch` composes without it, under `strict`, under
  `bypass`, three lines apart; a word outside the three refuses `policy-invalid`, BARE relays
  `policy-unsupported` -- nothing launched
- the record keeps the policy the face judged: `--max-budget-usd 1.00 --permissions strict`
  is kept as `{"max_budget_usd": 1.0, "permissions": "strict"}`, never the typed text
- `--effort` names the model's effort: the dry run says the line `launch` composes under `high`, a word outside
  the five refuses `policy-invalid`, FLAT relays `policy-unsupported` -- nothing launched; a wake-up
  keeps `{"effort": "high"}` in its policy
- an opening the adapter refuses (`policy-unsupported`) leaves no slot, no wake lock file,
  no run in `status`
"""
from __future__ import annotations

import json
import re
import shlex
from pathlib import Path

from conductor import adapters, persistence
from tests.harness import support

A = support(__file__, "agent")
HEAD = A.HEAD


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
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

    # --- --dry-run composes, launches nothing (i) ------------------------------------------------------
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
    return 0
