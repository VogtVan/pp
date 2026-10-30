"""Scenario `ui-real-runs` -- the runs of an agent at the post on the REAL verb: `agent chat --json` and the witness
harness of `agent`, never a provider; two conversations with `agents/ag1` in two tabs, one real exchange each, are
two runs, every case reading them:
- the post keeps both in the space `ui` of the house's metadata, each with its agent and its run
- `./pp ui` with no agent named gives both back, nothing launched: the active tab's exchange in history (its
  words, no verdict, no line of conduction, no head of a lived turn); `u` shows its kept flow (`agent flow --json`)
  as it was lived: its head, its conduction, its verdict
- `enter` on the agent, then on one run of the two in the overlay of its runs (picked by its key, the overlay
  listing them in the order of `agent status --json`), resumes it in a tab: its kept flow replayed as lived, then
  one more message: two verdicts, two heads of lived turns, `responses.jsonl` two lines of that run, `agent
  status --json` at two exchanges, the other run untouched
- the overlay of the runs says the other run's weight, as `agent status --json` weighs it; `P` on it, its key
  typed, `enter`: `agent status --json` no longer says it, `responses.jsonl` keeps none of its lines
"""
from __future__ import annotations

import json

from tests.harness import cli, support

R = support(__file__, "real")
P = R.P
YES, LOGICAL = (P.palette_constant(name) for name in ("YES", "LOGICAL"))
WIDE = ("--size", "160x40")


def flow(post, key: str) -> list[dict]:
    """-> the events the run's exchanges kept, as `agent flow --json` says them."""
    played = cli(post.engine, "agent", "flow", R.AGENT, key, "--json", cwd=post.ws)
    return [json.loads(line) for line in played.stdout.splitlines() if line.strip()]


def weighed(weight: dict) -> str:
    """-> the weight a row of runs gives a run: the bytes the engine keeps of it and those of its flow, as one size."""
    size = int(weight.get("bytes") or 0) + int(weight.get("flow") or 0)
    for bound, unit in ((1_000_000_000, "GB"), (1_000_000, "MB"), (1_000, "kB")):
        if size >= bound:
            return f"{size / bound:.1f} {unit}"
    return f"{size} B"


def lived(text: str) -> tuple[int, int, int]:
    """-> what a transcript shows of turns as lived: the heads of the principal's turns, the lines of conduction,
    the verdicts."""
    rows = [row.strip() for row in text.split("\n")]
    return (len(P.heads_of(text)), sum(row.startswith(LOGICAL) for row in rows),
            sum(row.split()[1:2] == [YES] for row in rows if row))


def picked(post, key: str) -> str:
    """-> the keys that open the overlay of the agent's runs and set its cursor on the run `key`."""
    order = [one["run"] for one in post.status_json()]
    return ",".join(["2", "down", "enter"] + ["down"] * order.index(key))


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = R.RealPost(bench, "ui-real-runs")

    # --- two conversations, one exchange each: two runs, both kept --------------------------------------
    two = post.render(R.AGENT, R.AGENT, "--render", "dialogue", *WIDE, "--press",
                      "i,h,i,enter,wait:waiting,ctrl+left,i,y,o,enter", "--wait", R.EXCHANGE)
    kept = post.remembered()
    runs = post.status_json()
    keys = sorted(one["run"] for one in runs)
    pairs = sorted((str(one[0]), str(one[1])) if isinstance(one, (list, tuple)) else (str(one.get("agent")), str(one.get("run")))
                   for one in kept)
    if two.returncode != 0 or len(keys) != 2 or len(post.responses()) != 2:
        failures.append(f"  ✗ real runs                   rc={two.returncode} runs={runs} {two.stdout!r} {two.stderr[-300:]!r}")
        return 0
    if [run for _, run in pairs] == keys and {agent for agent, _ in pairs} == {R.AGENT}:
        held("two conversations are two runs, both kept", f"the metadata's space ui keeps {pairs}")
    else:
        failures.append(f"  ✗ real memory                 kept={kept} runs={keys}")

    # --- ./pp ui with no agent: both back in history, u shows the kept flow as lived ----------------------
    again = post.render("--render", "dialogue", *WIDE, keep=True)
    shown = post.render("--render", "dialogue", *WIDE, "--press", "u", keep=True)
    bar = P.Post.tabs_of(again.stdout)
    words = {one["text"] for key in keys for one in flow(post, key) if one.get("kind") == "words"}
    if (again.returncode == 0 and all(key in bar for key in keys) and all(one in again.stdout for one in words)
            and lived(again.stdout) == (0, 0, 0) and shown.returncode == 0 and all(one in shown.stdout for one in words)
            and lived(shown.stdout) == (1, 1, 1)):
        held("./pp ui with no agent gives both back", f"the bar {bar.strip()!r}; the active tab's words {sorted(words)} in "
             "history; after u its head, its conduction and its verdict as lived")
    else:
        failures.append(f"  ✗ real reopen                 words={words} history={lived(again.stdout)} lived={lived(shown.stdout)} "
                        f"{again.stdout!r} {shown.stdout!r} {shown.stderr[-300:]!r}")

    # --- one run of the two resumed from the overlay of its runs, one more message --------------------------
    first = min(runs, key=lambda one: one["first_at"])["run"]
    other = next(key for key in keys if key != first)
    resumed = post.render("--render", "dialogue", "--size", "120x60", "--press",
                          f"{picked(post, first)},enter,wait:waiting,i,h,e,y,enter", "--wait", R.EXCHANGE)
    mine = [one for one in post.responses() if one["run"] == first]
    after = {one["run"]: one for one in post.status_json()}
    if (resumed.returncode == 0 and lived(resumed.stdout) == (2, 2, 2) and len(mine) == 2
            and after.get(first, {}).get("exchanges") == 2 and after.get(other, {}).get("exchanges") == 1):
        held("enter resumes the real run picked by its key", f"run {first}: its exchange replayed as lived, then one more; "
             f"responses.jsonl 2 lines of it, status --json at 2 exchanges, {other} at 1")
    else:
        failures.append(f"  ✗ real resume                 lived={lived(resumed.stdout)} responses={len(mine)} after={after} "
                        f"{resumed.stdout!r} {resumed.stderr[-300:]!r}")

    # --- the other run's weight on its row, then P purges it -------------------------------------------
    weight = after.get(other, {}).get("weight") or {}
    listed = post.render("--render", "dialogue", *WIDE, "--press", picked(post, other))
    row = next((line for line in P.overlay_rows(listed.stdout) if other in line.split()), "")
    purged = post.render("--render", "dialogue", *WIDE, "--press", f"{picked(post, other)},P,{','.join(other)},enter")
    left, answered = [one["run"] for one in post.status_json()], [one["run"] for one in post.responses()]
    if (listed.returncode == 0 and weight.get("bytes") and weighed(weight) in row and purged.returncode == 0
            and left == [first] and other not in answered):
        held("P purges a real run", f"its weight {weighed(weight)} on its row ({weight.get('bytes')} bytes and its flow); "
             f"after P: status --json says {left} alone, responses.jsonl none of its lines")
    else:
        failures.append(f"  ✗ real purge                  weight={weight} row={row!r} left={left} responses={answered} "
                        f"{purged.stdout[-1500:]!r} {purged.stderr[-300:]!r}")
    return 0
