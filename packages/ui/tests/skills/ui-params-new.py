"""Scenario `ui-params-new` -- the overlay of a NEW run's parameters, on the bench's `pp-chat` witness and its faces
(`ag1` last played the fixture's provider and `{model: m1}`; `providers --json` names two models of it):
- `n` on the Agents tab opens the overlay prefilled with what the agent last played: its title names the agent, the
  provider, model m1, the models of `providers --json` (read once as it opens), the fields provider, model, budget,
  effort and permissions on one screen, a `▼` on each field that lists
- `down` on `model` unrolls the models the adapter declares, each on a row of the list; the list floats over the
  overlay: the arrow turns `▲` and the row of `budget`'s example stays where it was
- `enter` opens the conversation with the flags filled in after those of `--`: the journal says
  `open ag1 --harness x --provider <the fixture's> --model m2`; the status says what the run plays
- the list is filtered by the line's prefix: the prefix of the second model lists it alone, `enter` fills the line;
  `effort` the same, `escape` in its list folds it and leaves the line as it was
- `ag1` having last played the second model, `down` on that exact name lists every model, the cursor on it: `up`
  reaches the name above, `enter` fills the line with it
"""
from __future__ import annotations

import copy

from tests.harness import support

P = support(__file__, "dialogue")
SIZE = ("--size", "110x40")
OPEN = "2,n,wait:none"                # the overlay of a new run of ag1, a pause for the providers' face: an
                                     # inline wait is bound by the seconds of `--wait`
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the providers' face
FIELDS = ("provider", "model", "budget", "effort", "permissions")


def row_of(rows: list[str], words: str) -> int:
    """-> the row `words` stands on, -1 when absent."""
    return next((n for n, line in enumerate(rows) if words in line), -1)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-params-new")
    render = post.render
    example = P.palette_constant("BUDGET_EXAMPLE")

    def journal(prefix: str) -> list[str]:
        return [one for one in post.journal_lines() if one.startswith(prefix)]

    # --- n: the overlay at rest, prefilled with what the agent last played; down unrolls the models -----
    post.clear_journal()
    rest = render("--render", "dialogue", *SIZE, "--press", OPEN, *PAUSE)
    read = journal("providers")
    unrolled = render("--render", "dialogue", *SIZE, "--press", f"{OPEN},down", *PAUSE)
    inside, listed = P.overlay_rows(rest.stdout), P.overlay_rows(unrolled.stdout)
    firsts = [row.split()[0] for row in inside if row.split()]       # a title, or a field's value before its arrow
    titles = [P.field_title(one) for one in FIELDS]
    if (rest.returncode == 0 and "ag1" in " ".join(P.title_of(rest.stdout)) and P.PROVIDER in firsts and "m1" in firsts
            and P.MODELS[0] in rest.stdout and all(one in firsts for one in titles) and read == ["providers --json"]):
        held("n opens the overlay prefilled", f"the title names ag1; provider {P.PROVIDER}, model m1, the models of "
             f"providers --json (read once); {', '.join(titles)} on one screen")
    else:
        failures.append(f"  ✗ overlay                     rc={rest.returncode} {read} {inside!r} {rest.stderr[-300:]!r}")
    arrows, before, after = rest.stdout.count("▼"), row_of(inside, example), row_of(listed, example)
    if (unrolled.returncode == 0 and P.MODELS[0] in listed and P.MODELS[1] in listed and arrows == 4
            and "▲" in unrolled.stdout and before > 0 and before == after):
        held("down unrolls the models, the list floats", f"{P.MODELS[0]} and {P.MODELS[1]} each on a row; 4 ▼ at rest "
             f"(provider, model, effort, permissions), ▲ unrolled; budget's example on row {before} both times")
    else:
        failures.append(f"  ✗ unrolled                    ▼={arrows} budget={before}/{after} {listed!r} "
                        f"{unrolled.stderr[-300:]!r}")

    # --- enter: the flags filled in, after those of `--` ---------------------------------------------
    post.clear_journal()
    opened = render("--render", "dialogue", *SIZE, "--press", "2,n,m,2,enter,wait:waiting,i,h,i,enter",
                    "--wait", "waiting", "--", "--harness", "x")
    status = P.status_of(opened.stdout)
    if (opened.returncode == 0 and journal("open") == [f"open ag1 --harness x --provider {P.PROVIDER} --model m2"]
            and "ag1" in status and "w00001" in status and f"{P.PROVIDER} · m1 · — · —" in status):
        held("enter opens the run with the flags", f"the journal says {journal('open')}; the status says ag1, w00001, "
             f"{P.PROVIDER} · m1 · — · — (what the witness's opened plays)")
    else:
        failures.append(f"  ✗ open                        rc={opened.returncode} {post.journal_lines()} {status!r} {opened.stderr[-300:]!r}")

    # --- the lists filtered by their prefix; escape folds the effort's list, the line as it was -------
    post.clear_journal()
    filtered = render("--render", "dialogue", *SIZE, "--press",
                      f"{OPEN},{','.join(P.MODELS[1][:6])},down,enter,tab,tab,h,down,escape,down,enter,enter",
                      "--wait", "waiting:2")
    opens = journal("open")
    if filtered.returncode == 0 and opens == [f"open ag1 --provider {P.PROVIDER} --model {P.MODELS[1]} --effort high"]:
        held("the lists are filtered by their line", f"{P.MODELS[1][:6]} lists the second model alone, enter fills it; "
             f"h lists high alone, escape folds it and leaves h: {opens}")
    else:
        failures.append(f"  ✗ filtered                    {opens} {filtered.stdout[-1500:]!r} {filtered.stderr[-300:]!r}")

    # --- ag1 last played the second model: the exact name lists them all, the cursor on it ------------
    script = copy.deepcopy(P.SCRIPT)
    script["faces"]["status"]["ag1"][-1]["last"] = {"provider": P.PROVIDER, "policy": {"model": P.MODELS[1]}}
    post.use(script)
    post.clear_journal()
    kept = render("--render", "dialogue", *SIZE, "--press", f"{OPEN},down,up,enter,enter", "--wait", "waiting:2")
    opens = journal("open")
    if kept.returncode == 0 and opens == [f"open ag1 --provider {P.PROVIDER} --model {P.MODELS[0]}"]:
        held("an exact name lists every name, the cursor on it", f"down, up, enter, enter from {P.MODELS[1]}: {opens}")
    else:
        failures.append(f"  ✗ cursor                      {opens} {kept.stderr[-300:]!r}")
    return 0
