"""Scenario `principal-cap` -- 4 case(s) (plan ui, batch le-plancher-du-mode-principal, 2026-10-09):
in a run its principal conducts, an output is cut under a FLOOR of the cap -- the larger of the
instance's `max_harness_tool_output` and `settings.PRINCIPAL_CAP` -- since the output reaches the
harness on its standard input and one output is one launch; the LLM's mode keeps the setting.
- (a) under the mark, on an instance at 20000, an opening that serves a reading of 60000 characters
  comes in ONE output: nothing waits at the run
- (b) a twin instance without the mark cuts as the setting says: the output waits, every chunk
  under 20000, three chunks at least
- (c) a setting above the floor holds under the mark: at 300000 a reading of 250000 characters comes
  whole, and the LLM's mode serves it whole too
- (d) `settings.served_cap` is the one rule: raised to the floor under the mark alone, a higher
  setting kept, a cap of 0 cutting nothing in either mode
"""
from __future__ import annotations

import re

from conductor import persistence, settings
from tests.harness import cli

MARK = {"PP_CONDUCTED_BY_PRINCIPAL": "true"}
KEY = re.compile(r"run ([0-9a-f]{6})")
LINE = "long line of matter\n"
LONGRUN = "---\nname: LONGRUN\nkind: proc\ndescription: a witness\nproc: |\n  SERVE LONG.md\n  WORK\n---\nread\n"
CONTINUES = "a reading continues"


def _long(chars: int) -> str:
    return "---\nname: LONG\nkind: doc\n---\n\n" + LINE * (chars // len(LINE)) + "\n"


def _settings(cap: int) -> str:
    return f"---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {cap}\n---\n"


def _house(bench, name: str, cap: int, chars: int):
    env = bench.env(name)
    env.write("SETTINGS.md", _settings(cap))
    env.write("LONG.md", _long(chars))
    env.write("procs/LONGRUN.md", LONGRUN)
    return env


def _opened(env, marked: bool):
    """-> (the key, the first output, what waits at the run): the run opened on the LONGRUN door."""
    variables = {"PP_DOOR": "LONGRUN.md", **(MARK if marked else {})}
    out = cli(env.engine, "-new", cwd=env.root, env=variables)
    found = KEY.search(out.stdout)
    key = found.group(1) if found else ""
    waiting = persistence.pending_of(persistence.slot_of(env.made, key)).get("matter", "") if key else ""
    return key, out, waiting


def _drained(env, key: str, first: str) -> list[str]:
    """-> every output of the reading: the first, then each chunk the bare call serves."""
    outputs = [first]
    while persistence.pending_of(persistence.slot_of(env.made, key)).get("matter") and len(outputs) < 50:
        outputs.append(cli(env.engine, key, cwd=env.root).stdout)
    return outputs


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- (a) the floor under the mark ------------------------------------------------------------------
    low = _house(bench, "cap-low", 20000, 60000)
    key_a, out_a, waiting_a = _opened(low, True)
    if out_a.returncode == 0 and key_a and not waiting_a and CONTINUES not in out_a.stdout \
            and out_a.stdout.count(LINE.strip()) >= 2900 and len(out_a.stdout) > 20000:
        held("(a) the floor under the mark", f"run {key_a} at 20000: the opening serves "
             f"{len(out_a.stdout)} characters in one output, nothing waits")
    else:
        failures.append(f"  ✗ (a) the floor               rc={out_a.returncode} key={key_a!r} "
                        f"waiting={len(waiting_a)} chars={len(out_a.stdout)} {out_a.stderr[-200:]!r}")

    # --- (b) the LLM's mode keeps the setting ------------------------------------------------------------
    # a twin: an unmarked `-new` beside a principal's run mid-exchange opens nothing
    twin = _house(bench, "cap-low-llm", 20000, 60000)
    key_b, out_b, waiting_b = _opened(twin, False)
    chunks = _drained(twin, key_b, out_b.stdout) if key_b else []
    if (out_b.returncode == 0 and waiting_b and CONTINUES in out_b.stdout and len(chunks) >= 3
            and all(len(one) <= 20000 for one in chunks)):
        held("(b) the LLM's mode keeps the setting", f"run {key_b} unmarked at 20000: {len(chunks)} outputs, "
             f"the longest {max(len(one) for one in chunks)} characters")
    else:
        failures.append(f"  ✗ (b) the LLM's cut           rc={out_b.returncode} waiting={len(waiting_b)} "
                        f"chunks={[len(one) for one in chunks]}")

    # --- (c) a setting above the floor holds -------------------------------------------------------------
    high = _house(bench, "cap-high", 300000, 250000)
    key_c, out_c, waiting_c = _opened(high, True)
    key_l, out_l, waiting_l = _opened(_house(bench, "cap-high-llm", 300000, 250000), False)
    if (out_c.returncode == 0 and key_c and not waiting_c and len(out_c.stdout) > 250000
            and out_l.returncode == 0 and key_l and not waiting_l and len(out_l.stdout) > 250000):
        held("(c) a setting above the floor holds", f"at 300000 the reading comes whole in both modes: "
             f"{len(out_c.stdout)} characters marked, {len(out_l.stdout)} unmarked")
    else:
        failures.append(f"  ✗ (c) above the floor         marked={len(out_c.stdout)}/{len(waiting_c)} "
                        f"unmarked={len(out_l.stdout)}/{len(waiting_l)}")

    # --- (d) the one rule ----------------------------------------------------------------------------------
    floor = settings.PRINCIPAL_CAP
    ruled = {(20000, True): floor, (20000, False): 20000, (300000, True): 300000, (300000, False): 300000,
             (0, True): 0, (0, False): 0}
    got = {pair: settings.served_cap(*pair) for pair in ruled}
    if floor == 200000 and got == ruled:
        held("(d) served_cap is the one rule", f"floor {floor}: raised under the mark alone, a higher setting "
             "kept, 0 cuts nothing in either mode")
    else:
        failures.append(f"  ✗ (d) served_cap              floor={floor} {got}")
    return 0
