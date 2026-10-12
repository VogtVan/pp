"""Scenario `ui-real-dialogue` -- a conversation at the post on the REAL verb (plan ui, batch
le-reel-du-poste-recadre): `agent chat --json` and the witness harness of `agent`, never a provider:
- two messages typed at the post are two exchanges of one run: four answers of the witness (2 then 2
  launches: the boot whole, the floor of a principal's cap) on their lines and the two answers in their blocks,
  two verdicts parked, each conduction on its line naming the block it serves (`◇ … launch n · BOOT ▸ …`);
  `responses.jsonl` two lines of one run, `sessions.jsonl` one
- between the two, `p` sets the model `m2`: the status says it, and the second line of `messages.jsonl`
  carries it -- what the verb keeps (under `--harness` no policy is spelled to the witness)
- while an exchange runs (the witness thinking 1.6 s at its first launch), the tab's title carries the
  glyph of the turn
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real")
SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = R.RealPost(bench, "ui-real-dialogue")

    # --- two messages, a set between them -------------------------------------------------------------
    talked = post.render(R.AGENT, "--render", "dialogue", "--size", "120x60", "--press",
                         "h,i,enter,wait:waiting,escape,p,m,2,enter,wait:policy,i,y,o,enter", "--wait", R.EXCHANGE)
    text = talked.stdout
    status = text.rstrip("\n").split("\n")[-1]
    responses, sessions, messages = post.responses(), post.sessions(), post.messages()
    runs = post.status_json()
    key = runs[0]["run"] if runs else ""
    if (talked.returncode == 0 and text.count("witness answer: play") == 6 and text.count("✓ parked") == 2
            and text.count("◇") == 4 and text.count("· BOOT ▸ MEMBER ▸ ") == 4
            and len(responses) == 2 and len({one["run"] for one in responses}) == 1 and len(sessions) == 1
            and len(runs) == 1 and runs[0]["exchanges"] == 2):
        held("two messages are two exchanges of one real run", f"run {key}: four answers (2 then 2 launches: the boot whole), two "
             "verdicts parked, four ◇ lines naming their BOOT block, the two answers; responses.jsonl 2 lines, sessions.jsonl 1")
    else:
        failures.append(f"  ✗ real exchanges              rc={talked.returncode} {text!r} responses={len(responses)} "
                        f"sessions={len(sessions)} runs={runs} {talked.stderr[-300:]!r}")
    model = [(one.get("policy") or {}).get("model") for one in messages]
    if talked.returncode == 0 and len(messages) == 2 and model[1] == "m2" and model[0] != "m2" and " · m2 · " in status:
        held("p sets the model between two messages", f"messages.jsonl policies {model}; the status says {status.strip()[:90]!r}")
    else:
        failures.append(f"  ✗ real set                    models={model} status={status!r}")

    # --- the glyph of the turn while an exchange runs: a run of its own, the witness pausing --------------
    turning = post.render(R.AGENT, "--render", "dialogue", "--size", "120x30", "--press", "h,i,enter,wait:principal,y", mode="pause")
    bar = R.P.Post.tabs_of(turning.stdout)
    if turning.returncode == 0 and any(glyph in bar for glyph in SPINNER):
        held("the turn under way shows its glyph", f"the bar {bar.strip()!r} once the principal's line came back")
    else:
        failures.append(f"  ✗ real turn                   rc={turning.returncode} {bar!r} {turning.stderr[-300:]!r}")
    return 0
