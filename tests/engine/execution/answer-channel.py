"""Scenario `answer-channel` -- 2 case(s):
- the `answer` line of the trace carries the step's channel: a production a PICK consumes
  goes `tool (heredoc)`, the PICK's own value `tool`
- a stray production handed to a draft step is traced with its channel `ephemeral` -- the
  reader of the traces tells it from a value without guessing
"""
from __future__ import annotations

from conductor import instance
from conductor.state import traces


def _answers(made) -> list[dict]:
    written = sorted((made / instance.STATE).glob("session-*.jsonl"))
    events = traces.read(written[-1]) if written else []
    return [one for one in events if one.get("kind") == "answer"]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- a consumed production and the PICK that takes it ---------------------------
    env = bench.env("answer-channel")
    env.write("procs/CHOOSER.md",
              "---\nname: CHOOSER\nkind: proc\ndescription: lists, then picks\noutput: json\n"
              "proc: |\n  INFER\n  PICK member\n---\nlist the members, then pick one\n")
    chooser = env.conductor("c")
    chooser.start(chooser.boot("CHOOSER.md"))
    env.conductor("c").submit('["ada", "bob"]')
    env.conductor("c").submit("ada")
    told = [(one.get("instruction", "").split(" ")[0], one.get("channel")) for one in _answers(env.made)]
    if told == [("INFER", "tool (heredoc)"), ("PICK", "tool")]:
        held("the answer line carries its channel", "the consumed INFER `tool (heredoc)`, the "
             "PICK `tool` -- derived where the block derives it, nothing else moves")
    else:
        failures.append(f"  ✗ consumed channel            {told!r}")

    # --- a stray production on a draft step (the turn's WORK, `=> ephemeral`) -----------
    stray_env = bench.env("answer-stray")
    stray = stray_env.conductor("s")
    opening = stray.resume(stray.boot("BOOT.md"))
    bounced = stray_env.conductor("s").submit("a table nobody asked the tool for")
    lines = _answers(stray_env.made)
    if (opening.instruction.keyword == "WORK" and lines
            and lines[-1].get("channel") == "ephemeral"
            and lines[-1].get("given") == "a table nobody asked the tool for"
            and bounced.deviation and bounced.instruction.keyword == "WORK"):
        held("a stray production says its channel", "the draft step's answer line reads "
             "`ephemeral` -- the soft catch bounces it, the reader counts no value")
    else:
        failures.append(f"  ✗ stray channel               {[(l.get('instruction'), l.get('channel')) for l in lines]!r} "
                        f"{bounced and bounced.deviation!r}")
    return 0
