"""Scenario `ui-real-dialogue` -- a conversation at the post and the Agents tab on the REAL verb: `agent chat --json`
and the witness harness of `agent`, never a provider; one real run of two exchanges typed at the post, the model
set to `m2` between them, every case reading it:
- the two messages are two exchanges of one run: each answer (the words `responses.jsonl` keeps) once in the
  transcript, each verdict (`agent flow --json`) on its line, each conduction on its line naming the last block it
  serves; `responses.jsonl` two lines of one run, `sessions.jsonl` one, `agent status --json` at two exchanges
- between the two, `p` sets the model `m2`: the status says it, and the second line of `messages.jsonl` carries it
  -- what the verb keeps (under `--harness` no policy is spelled to the witness)
- the Agents tab's table reads the real faces: the row of `agents/ag1` says the runs of `agent list --json` and
  the state of `agent status --json`
- its run resumed from the overlay of its runs, `p` names it `demo` (the last field of its parameters):
  `names.jsonl` one line, `agent status --json` says the name
- `s` stacks the statistics of the run: its blocks and its mass as `agent stats --json` says them
- `n` opens the overlay of a new run of the agent prefilled with what it last played: the model `m2`
"""
from __future__ import annotations

import json

from tests.harness import cli, support

R = support(__file__, "real")
P = R.P
YES, LOGICAL, SEP = (P.palette_constant(name) for name in ("YES", "LOGICAL", "SEP"))
TALK = "i,h,i,enter,wait:waiting,escape,p,m,2,enter,wait:policy,i,y,o,enter"   # the keys of `RealPost.talk`
TALL = ("--size", "120x60")          # both exchanges in view, their conductions shown


def face(post, *args: str) -> list[dict]:
    """-> the objects a `--json` face of `agent` prints, one per line."""
    played = cli(post.engine, "agent", *args, "--json", cwd=post.ws)
    return [json.loads(line) for line in played.stdout.splitlines() if line.strip()]


def row_of(text: str, first: str) -> list[str]:
    """-> the cells of the table's row opening on `first`, cut on their runs of blanks."""
    for line in text.split("\n"):
        cells = [one for one in line.strip().split("  ") if one.strip()]
        if cells and cells[0].strip() == first:
            return [one.strip() for one in cells]
    return []


def figure(text: str, field: str) -> str:
    """-> the value the overlay of statistics gives `field`, on the row it opens inside the overlay's border."""
    for line in text.split("\n"):
        for inner in line.split("┃"):
            parts = inner.split()
            if len(parts) >= 2 and parts[0] == field:
                return parts[1]
    return ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = R.RealPost(bench, "ui-real-dialogue")

    # --- the run: two messages, a set between them ------------------------------------------------------
    talked = post.render(R.AGENT, "--render", "dialogue", *TALL, "--press", TALK, "--wait", R.EXCHANGE)
    text = talked.stdout
    responses, sessions, messages = post.responses(), post.sessions(), post.messages()
    runs = post.status_json()
    key = runs[0]["run"] if runs else ""
    if talked.returncode != 0 or len(runs) != 1 or len(responses) != 2:
        failures.append(f"  ✗ real run                    rc={talked.returncode} runs={runs} {text!r} {talked.stderr[-300:]!r}")
        return 0
    flow = face(post, "flow", R.AGENT, key)
    words = [one["text"] for answer in responses for one in answer.get("words") or []]
    verdicts = [one["state"] for one in flow if one.get("kind") == "verdict"]
    served = [one["blocks"][-1]["stack"] for one in flow if one.get("kind") == "conduction" and one.get("blocks")]
    conducted = [row for row in text.split("\n") if row.strip().startswith(LOGICAL)]
    if (len(words) == 2 and all(text.count(one) == words.count(one) for one in words)
            and len(verdicts) == 2 and all(text.count(f"{YES} {one}") == verdicts.count(one) for one in verdicts)
            and len(served) == 2 and len(conducted) == 2 and all(stack in row for stack, row in zip(served, conducted))
            and len({one["run"] for one in responses}) == 1 and len(sessions) == 1 and runs[0]["exchanges"] == 2):
        held("two messages are two exchanges of one real run", f"run {key}: the words {words} each on its line, the "
             f"verdicts {verdicts}, the conductions naming {served}; responses.jsonl 2 lines, sessions.jsonl 1")
    else:
        failures.append(f"  ✗ real exchanges              words={words} verdicts={verdicts} served={served} "
                        f"conducted={conducted} sessions={len(sessions)} runs={runs} {text!r}")
    model = [(one.get("policy") or {}).get("model") for one in messages]
    fields = [one.strip() for one in P.status_of(text).split(SEP)]
    if len(messages) == 2 and model[1] == "m2" and model[0] != "m2" and "m2" in fields:
        held("p sets the model between two messages", f"messages.jsonl policies {model}; the status's fields {fields}")
    else:
        failures.append(f"  ✗ real set                    models={model} status={fields}")

    # --- the Agents tab: the table of the real faces ------------------------------------------------------
    table = post.render("--render", "agents", "--size", "120x30")
    listed = next((one for one in face(post, "list") if one.get("agent") == R.AGENT), {})
    row = row_of(table.stdout, R.AGENT)
    if table.returncode == 0 and len(row) > 3 and row[1] == str(listed.get("runs")) == "1" and row[3] == runs[0]["state"]:
        held("the table reads the real faces", f"the row {row[:4]}: list --json runs {listed.get('runs')}, "
             f"status --json state {runs[0]['state']}")
    else:
        failures.append(f"  ✗ real table                  row={row} listed={listed} {table.stdout!r} {table.stderr[-300:]!r}")

    # --- s: the statistics of the run -------------------------------------------------------------------
    measured = post.render("--render", "dialogue", "--size", "120x40", "--press", "2,down,enter,s")
    stats = (face(post, "stats", R.AGENT, key) or [{}])[0].get("conduction") or {}
    blocks, mass = figure(measured.stdout, "blocks"), figure(measured.stdout, "mass")
    if measured.returncode == 0 and stats.get("blocks") and blocks == str(stats["blocks"]) and mass == str(stats.get("mass")):
        held("s reads the real statistics", f"blocks {blocks}, mass {mass}: stats --json's")
    else:
        failures.append(f"  ✗ real stats                  blocks={blocks} mass={mass} stats={str(stats)[:300]} "
                        f"{measured.stdout!r} {measured.stderr[-300:]!r}")

    # --- n: the overlay of a new run, prefilled with what the agent last played ---------------------------
    last = post.last_policy()
    fresh = post.render("--render", "agents", "--size", "120x40", "--press", "down,n")
    title, offered = P.title_of(fresh.stdout), P.field_of(P.overlay_rows(P.on_top(fresh.stdout)), "model")
    if (fresh.returncode == 0 and (last.get("policy") or {}).get("model") == "m2" and any(R.AGENT in one for one in title)
            and offered == ["m2"]):
        held("n opens the overlay with the last real policy", f"status --json last {last}; the field model {offered}")
    else:
        failures.append(f"  ✗ real n                      last={last} title={title} model={offered} {fresh.stdout!r} "
                        f"{fresh.stderr[-300:]!r}")

    # --- p names the run, resumed from the overlay of its runs --------------------------------------------
    named = post.render("--render", "dialogue", "--size", "120x30", "--press",
                        "2,down,enter,enter,wait:waiting,escape,p,tab,tab,tab,tab,tab,d,e,m,o,enter")
    names, after = post.names(), post.status_json()
    if (named.returncode == 0 and len(names) == 1 and names[0]["name"] == "demo" and names[0]["run"] == key
            and after and after[0]["name"] == "demo"):
        held("p names the real run", f"run {key} + demo: names.jsonl one line, status --json says demo")
    else:
        failures.append(f"  ✗ real name                   names={names} after={after[:1]} {named.stdout!r} {named.stderr[-300:]!r}")
    return 0
