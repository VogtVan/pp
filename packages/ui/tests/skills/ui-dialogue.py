"""Scenario `ui-dialogue` -- one conversation in its tab, on the bench's `pp-chat` witness replaying a scripted flow:
- a message typed and sent: the principal's block, a line per conduction (`◇`), the words of each launch as a block
  under its head (`◀`, the launch) and the launch's end (`◀`, its launch and cost) -- no answer composed over the
  words --, the verdict parked -- no line of pp's output shows; the tab bar carries the conversation
- before any message the status says the run as `ready` says it (`<provider> · m1`), and the transcript shows no
  line for it
- with no conversation open the dialogue offers `./pp ui <agent path>` and `[n]`, and shows no line to type in;
  `./pp ui nowhere` relays the verb's `agent-unknown` in one line, nothing drawn
- a run whose cap the floor of a principal's cap raised (`opened.cap`): the remedy line names the agent, the cap set
  and the cap applied, still at rest after the exchange; a cap not raised says nothing
- a conversation the verb refuses at the gesture (the script swapped by `use()`) keeps its tab: the end (`ended rc
  2`) and the refusal's code in its transcript and on the remedy line; `x` alone closes it, the dialogue empty again
The tabs themselves (two agents, the unread, the launches, `x`, `n`, `r`) are `ui-tabs`'s, the turn under way
`ui-turn`'s, the folds of the transcript `ui-tools`'s.
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-dialogue")
    render, tabs_of, remedy, status = post.render, post.tabs_of, P.remedy_of, P.status_of

    # --- a message sent: the voices, the verdict; the conduction and the steps folded ---------------
    shown = render("ag1", "--render", "dialogue", "--size", "100x30", "--press", "i,h,i,enter", "--wait", "waiting")
    text = shown.stdout
    bar = tabs_of(text)
    if (shown.returncode == 0 and "▶" in text and "hi" in text and text.count("◀") == 4
            and "the agent says one" in text and "the agent says two" in text
            and "launch 1 · 0.01 USD" in text and "launch 2 · 0.02 USD" in text
            and text.count("◇") == 2 and "the answer" not in text and "✓ parked" in text and "0.03 USD · 2 launch(es)" in text
            and "▌ pp · run" not in text and "ag1 · w00001" in bar
            and "ag1 · run w00001 · waiting" in status(text)):
        held("the dialogue shows the voices in the conversation's tab", "the bar carries `ag1 · w00001`; "
             "the principal's block, two conductions on their ◇ line, the words of each launch as a block, each launch's "
             "end with its cost, no answer over them, the verdict parked; no line of pp's output; the status says the run "
             "and waiting")
    else:
        failures.append(f"  ✗ voices                      rc={shown.returncode} {text!r} {shown.stderr[-300:]!r}")

    # --- before any message: the run as `ready` says it, no block for it -------------------------------
    early = render("ag1", "--render", "dialogue", "--size", "100x30")
    if (early.returncode == 0 and f"{P.PROVIDER} · m1" in status(early.stdout) and "ready" not in early.stdout
            and "▶" not in early.stdout):
        held("the run is known before any message", f"the status says {status(early.stdout).strip()[:70]!r}; no line "
             "for ready")
    else:
        failures.append(f"  ✗ ready                       rc={early.returncode} {early.stdout!r} {early.stderr[-300:]!r}")

    # --- with no conversation open: the command and the key that open one; no line to type in ---------------
    empty = render("--render", "dialogue", "--size", "120x30", witnessed=False)
    said = " ".join(empty.stdout.split())
    if (empty.returncode == 0 and "./pp ui <agent path>" in said and P.entry_of(empty.stdout, "n")
            and "▔" not in empty.stdout and "·" not in tabs_of(empty.stdout) and " run " not in status(empty.stdout)):
        held("the empty dialogue says where to open a conversation", f"`./pp ui <agent path>` and "
             f"{P.entry_of(empty.stdout, 'n')!r}; no tab, no run on the status, no line to type in")
    else:
        failures.append(f"  ✗ empty dialogue              rc={empty.returncode} {empty.stdout!r}")

    # --- the real verb refuses an agent nobody is: relayed in one line, nothing drawn -----------------
    nobody = render("nowhere", "--render", "dialogue", witnessed=False)
    if (nobody.returncode == 2 and nobody.stdout == "" and nobody.stderr.startswith("pp-ui: agent-unknown -- ")
            and len(nobody.stderr.strip().splitlines()) == 1):
        held("a refusal of the verb is relayed", nobody.stderr.strip()[:90])
    else:
        failures.append(f"  ✗ nowhere                     rc={nobody.returncode} {nobody.stdout[:80]!r} {nobody.stderr[-200:]!r}")

    # --- a raised cap is said on the remedy line; a cap not raised says nothing -----------------------
    raised = render("ag4", "--render", "dialogue", "--size", "120x30", "--press", "i,h,i,enter", "--wait", "waiting")
    same = render("ag5", "--render", "dialogue", "--size", "120x30", "--press", "i,h,i,enter", "--wait", "waiting")
    note = remedy(raised.stdout).split()
    if (raised.returncode == 0 and note[:1] == ["ag4:"] and "20000" in note and "200000" in note
            and note.index("20000") < note.index("200000") and "✓ parked" in raised.stdout
            and same.returncode == 0 and "200000" not in remedy(same.stdout) and "✓ parked" in same.stdout):
        held("a raised cap is said, at rest too", f"ag4 opened at 20000 under the floor: {' '.join(note)!r} on the "
             f"remedy line after the verdict; ag5 at 200000: {remedy(same.stdout)!r}")
    else:
        failures.append(f"  ✗ cap said                    rc={raised.returncode}/{same.returncode} "
                        f"{remedy(raised.stdout)!r} {remedy(same.stdout)!r}")

    # --- a conversation the verb refuses at the gesture keeps its tab; x alone closes it -----------------
    post.use({"agents": {"ag1": P.refusing(
        "pp-agent: run-busy -- a wake-up plays run w00001: one wake-up at a time on a run.")}, "faces": P.FACES})
    kept = render("--render", "dialogue", "--size", "120x30", "--press", "2,n,enter", "--wait", "ended")
    text_k = kept.stdout
    told = remedy(text_k)
    closed = render("--render", "dialogue", "--size", "120x30", "--press", "2,n,enter,wait:ended,x")
    if (kept.returncode == 0 and "ag1" in tabs_of(text_k) and "ended rc 2" in text_k.replace(told, "")
            and told.startswith("ag1:") and "ended rc 2" in told and "run-busy" in told
            and closed.returncode == 0 and "ag1" not in tabs_of(closed.stdout) and "▔" not in closed.stdout):
        held("a refused conversation keeps its tab, x closes it", f"the transcript says `ended rc 2`, the remedy line "
             f"{told[:60]!r}; after x no tab, no line to type in")
    else:
        failures.append(f"  ✗ refused kept                rc={kept.returncode} {text_k!r} / {closed.stdout!r} {kept.stderr[-300:]!r}")
    return 0
