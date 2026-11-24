"""Scenario `ui-real-capture` -- the thread of a conversation renders what the agent HANDED to pp, on the REAL
verb: `agent chat --json` under the witness of `agent` in its printing mode, which writes a text before each print
call, hands every production the conduction says due on `terminal` by that call and says its answer last:
- the productions handed are the ones the trace says due (`print-due`), in their order; each stands in the thread
  once, read at its last row; the exchange's `words` (`responses.jsonl`) are the productions as the trace holds them
- the model's other texts in blocks of their own (ui 1.11.0): each text written before a call stands once in the
  thread under its own head (`ASIDE`), one head per aside; the answer, the launch's last message, once under its own
  (`FINAL`) -- neither in the productions' blocks
"""
from __future__ import annotations

import re

from tests.harness import support

R = support(__file__, "real")
P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = R.RealPost(bench, "ui-real-capture")
    talked = post.render(R.AGENT, "--render", "dialogue", "--size", "120x60", "--press", "i,h,i,ctrl+enter",
                         "--wait", R.EXCHANGE, mode="printing")
    text, handed, responses = talked.stdout, post.prints(), post.responses()
    runs = post.status_json()
    key = runs[0]["run"] if runs else ""
    trace = post.trace(key) if key else []
    given = R.A.captures_of(trace)
    due = [one.get("document") for one in trace if one.get("kind") == "print-due"]   # said on `terminal` by the conduction
    words = [one.get("text") for answer in responses for one in answer.get("words") or []]
    rows = [one.split("\n")[-1] for one in given]       # its last row: the line of the call shows the first ones;
                                                        # a row the productions share stands once per production
    asides = [one["aside"] for one in handed]
    answer = "witness answer: printing"                 # the witness's last message
    heads = {name: len(re.findall(rf"{re.escape(P.palette_constant(name))} \d\d:\d\d:\d\d · launch", text))
             for name in ("ASIDE", "FINAL")}
    if (talked.returncode == 0 and len(responses) == 1 and due and len(given) == len(due)
            and [one["document"] for one in handed] == due and given == [one["text"] for one in handed]
            and words == given
            and all(text.count(one) == rows.count(one) for one in rows)
            and asides and all(text.count(one) == 1 for one in asides + [answer])
            and not any(one in production or answer in production for one in asides for production in given)
            and heads == {"ASIDE": len(asides), "FINAL": 1}):
        held("the thread renders the productions handed, each aside and the answer in their own", f"run {key}: the "
             f"{len(due)} production(s) the conduction said due, printed by the witness, each once in the thread; "
             f"the {len(asides)} aside(s) and the answer once each under their own heads {heads}; the words are the "
             "trace's capture")
    else:
        failures.append(f"  ✗ the thread                  rc={talked.returncode} responses={len(responses)} "
                        f"due={due!r} given={given!r} words={words!r} asides={asides!r} heads={heads} "
                        f"counts={[text.count(one) for one in rows + asides + [answer]]} {text!r} "
                        f"{talked.stderr[-300:]!r}")
    return 0
