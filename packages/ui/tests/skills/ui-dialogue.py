"""Scenario `ui-dialogue` -- one conversation in its tab (plan ui, batch le-poste-a-onglets), on the
bench's `pp-chat` witness replaying a scripted flow:
- a message typed and sent: the principal's block, a line per conduction (`◇`) and per answer of the agent with its launch and cost, the answer of the turn, the verdict parked -- no line of pp's output shows; the tab bar carries the conversation
- `c` hides the lines of conduction, the footer says hidden (the lines themselves are `ui-transcript`'s)
- `ctrl+g` during an exchange sends `stop`: the verdict says interrupted, the message line is back (the button is `ui-stop`'s)
- before any message the status says the run as `ready` says it (`<provider> · m1`), and the transcript shows no line for it
- with no conversation open the dialogue says where to open one, and shows no line to type in; `./pp ui nowhere` relays the verb's `agent-unknown` in one line, nothing drawn
- a conversation the verb refuses at the gesture keeps its tab: the end and the refusal in its transcript and on the remedy line; `x` alone closes it
- a run whose cap the floor of a principal's cap raised (`opened.cap`, batch le-plancher-du-mode-principal): the remedy line says
  `cap <set> lifted to <applied> for this run`, still at rest after the exchange; a cap not raised says nothing
The tabs themselves (two agents, the unread, the launches, `x`, `n`, `r`) are `ui-tabs`'s, the turn under way `ui-turn`'s.
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-dialogue")
    render, tabs_of = post.render, post.tabs_of

    # --- a message sent: the voices, the verdict; the conduction and the steps folded ---------------
    shown = render("ag1", "--render", "dialogue", "--size", "100x30", "--press", "h,i,enter", "--wait", "waiting")
    text = shown.stdout
    lines = text.rstrip("\n").split("\n")
    bar = tabs_of(text)
    if (shown.returncode == 0 and "▶" in text and "hi" in text and text.count("◀") == 3
            and "the agent says one" in text and "launch 1 · 0.01 USD" in text and "launch 2 · 0.02 USD" in text
            and text.count("◇") == 2 and "the answer" in text and "✓ parked" in text and "0.03 USD · 2 launch(es)" in text
            and "▌ pp · run" not in text and "[c] conduction: shown" in text and "ag1 · w00001" in bar
            and "ag1 · run w00001 · waiting" in lines[-1]):
        held("the dialogue shows the voices in the conversation's tab", "the bar carries `ag1 · w00001`; "
             "the principal's block, two conductions on their ◇ line, two answers with launch and cost, the answer of "
             "the turn, the verdict parked; no line of pp's output; the status says the run and waiting")
    else:
        failures.append(f"  ✗ voices                      rc={shown.returncode} {text!r} {shown.stderr[-300:]!r}")

    # --- before any message: the run as `ready` says it, no block for it -------------------------------
    early = render("ag1", "--render", "dialogue", "--size", "100x30")
    rows = early.stdout.rstrip("\n").split("\n")
    if (early.returncode == 0 and f"{P.PROVIDER} · m1" in rows[-1] and "ready" not in early.stdout
            and "▶" not in early.stdout):
        held("the run is known before any message", f"the status says {rows[-1].strip()[:70]!r}; no line for ready")
    else:
        failures.append(f"  ✗ ready                       rc={early.returncode} {rows[-1:]!r} {early.stdout!r} {early.stderr[-300:]!r}")

    # --- `c` hides the conduction (escape leaves the line first: the letters act) ---------------------------
    toggled = render("ag1", "--render", "dialogue", "--size", "100x30",
                     "--press", "h,i,enter,wait:waiting,escape,c")
    text_c = toggled.stdout
    if (toggled.returncode == 0 and "◇" not in text_c and "[c] conduction: hidden" in text_c
            and "the agent says two" in text_c and "✓ parked" in text_c):
        held("c hides the conduction", "no ◇ line left, the answers and the verdict stay, the footer says hidden")
    else:
        failures.append(f"  ✗ conduction hidden           rc={toggled.returncode} {text_c!r} {toggled.stderr[-300:]!r}")

    # --- ctrl+g during an exchange: stop -> interrupted ----------------------------------------------
    stopped = render("ag1", "--render", "dialogue", "--size", "100x30",
                     "--press", "h,i,enter,wait:waiting,g,o,enter,wait:conduction,ctrl+g", "--wait", "waiting")
    text_e = stopped.stdout
    if (stopped.returncode == 0 and "⚠ interrupted" in text_e and "1 launch(es)" in text_e and "go" in text_e
            and "✓ parked" in text_e and "ag1 · run w00001 · waiting" in text_e.rstrip("\n").split("\n")[-1]):
        held("ctrl+g stops the exchange", "after the second message, ctrl+g sent stop: ⚠ interrupted, "
             "then waiting again")
    else:
        failures.append(f"  ✗ ctrl+g                      rc={stopped.returncode} {text_e!r} {stopped.stderr[-300:]!r}")

    # --- with no conversation open, the dialogue says where to open one; no line to type in -----------
    empty = render("--render", "dialogue", "--size", "120x30", witnessed=False)
    said = " ".join(empty.stdout.split())
    if (empty.returncode == 0 and "no conversation open" in said and "`2` lists the agents" in said
            and "name an agent to talk to" in said and "./pp ui <agent path>" in said and "[n] open" in said
            and "▔" not in empty.stdout and "enter opens the conversation" not in said):
        held("the empty dialogue says where to open a conversation", "`2` lists the agents, or `./pp ui <agent path> …`; "
             "no line to type in")
    else:
        failures.append(f"  ✗ empty dialogue              rc={empty.returncode} {empty.stdout[:400]!r}")

    # --- the real verb refuses an agent nobody is: relayed in one line, nothing drawn -----------------
    nobody = render("nowhere", "--render", "dialogue", witnessed=False)
    if (nobody.returncode == 2 and nobody.stdout == "" and nobody.stderr.startswith("pp-ui: agent-unknown -- ")
            and len(nobody.stderr.strip().splitlines()) == 1):
        held("a refusal of the verb is relayed", nobody.stderr.strip()[:90])
    else:
        failures.append(f"  ✗ nowhere                     rc={nobody.returncode} {nobody.stdout[:80]!r} {nobody.stderr[-200:]!r}")

    # --- a conversation the verb refuses at the gesture keeps its tab; x alone closes it -----------------
    refused = P.Post(bench, "ui-dialogue-refused", {"agents": {"ag1": P.refusing(
        "pp-agent: run-busy -- a wake-up plays run w00001: one wake-up at a time on a run.")}, "faces": P.FACES})
    kept = refused.render("--render", "dialogue", "--size", "120x30", "--press", "2,n,enter", "--wait", "ended")
    text_k = kept.stdout
    lines_k = text_k.rstrip("\n").split("\n")
    closed = refused.render("--render", "dialogue", "--size", "120x30", "--press", "2,n,enter,wait:ended,x")
    if (kept.returncode == 0 and "ag1" in refused.tabs_of(text_k) and "✗ ended rc 2 -- pp-agent: run-busy" in text_k
            and "ag1: ended rc 2 -- pp-agent: run-busy" in lines_k[-2] and "x closes the tab" in text_k
            and closed.returncode == 0 and "no conversation open" in " ".join(closed.stdout.split())):
        held("a refused conversation keeps its tab, x closes it", "the transcript and the remedy say `ended rc 2 -- "
             "pp-agent: run-busy …`; the line says x closes the tab; after x the dialogue is empty again")
    else:
        failures.append(f"  ✗ refused kept                rc={kept.returncode} {text_k!r} / {closed.stdout!r} {kept.stderr[-300:]!r}")

    # --- a raised cap is said on the remedy line; a cap not raised says nothing -----------------------
    raised = render("ag4", "--render", "dialogue", "--size", "120x30", "--press", "h,i,enter", "--wait", "waiting")
    same = render("ag5", "--render", "dialogue", "--size", "120x30", "--press", "h,i,enter", "--wait", "waiting")
    lines_r = raised.stdout.rstrip("\n").split("\n")
    lines_s = same.stdout.rstrip("\n").split("\n")
    if (raised.returncode == 0 and "ag4: cap 20000 lifted to 200000 for this run" in lines_r[-2]
            and "✓ parked" in raised.stdout
            and same.returncode == 0 and "lifted" not in same.stdout and "✓ parked" in same.stdout):
        held("a raised cap is said, at rest too", "ag4 opened at 20000 under the floor: the remedy line says "
             "`cap 20000 lifted to 200000 for this run` after the verdict; ag5 at 200000 says nothing")
    else:
        failures.append(f"  ✗ cap said                    rc={raised.returncode}/{same.returncode} {lines_r[-3:]!r} {lines_s[-3:]!r}")
    return 0
