"""Scenario `ui-status-line` -- the gauges of a conversation: the context beside the message line, read from `context` of
`agent stats --json` alone, and the budget of the run on the status line, on ONE post of the bench's `pp-chat` witness
whose script changes by `use()`:
- before any verdict, no gauge, and no `stats` played
- after the verdict of `ag1`'s first turn, `stats ag1 w00001 --json` played and the gauge says the faces' `~17%` --
  estimated, said so -- and pp's `33%` after a bar of ten cells: pp's part and the rest of the used part in two looks, the empty cells in a third
  (`--styles`)
- a `context` the flow says during a turn (a call measured, its window and the part used) moves the gauge before
  the verdict, the measure said without `~`, no stats played (batch le-contexte-mesure)
- a run without `context` (`w00009`) says no gauge after its verdict
- a run taken up says its gauge before any message: `stats` played at its opening
- the status line of a conversation says the budget of its run, `0.42/2.00` and a bar of ten cells, read from
  `budget {cap, spent, left}` of `ready`, `opened` and `verdict`; the look says its state -- three looks for 21 %,
  85 % and 100 %, the last one bold (`--styles`); a run without a cap says none
- while a face is read (`u` on the Agents tab, the witness's statuses slow), the spinner turns and the status says
  what is read (`READING` of the palette; batch la-borne-et-le-demarrage)
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")

SIZE = ("--size", "120x30")
GAUGE = re.compile(r"[▰▱]{10} ~17%\D+33%")        # the faces' context, estimated: ~17 % used, pp's share 33 %
MEASURED = re.compile(r"[▰▱]{10} 42%")             # a call's measure said at the flow: 42 % used, no `~`
BAR = re.compile(r"[▰▱]{10}")
TURN = "i,h,i,enter,wait:waiting"
SEGMENT = re.compile(r"\x1b\[([0-9;]*)m([^\x1b]*)")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-status-line")
    render = post.render

    def stats() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("stats ")]

    # --- before any verdict: ctx —, nothing played -------------------------------------------------------------
    post.clear_journal()
    rest = render("ag1", "--render", "dialogue", *SIZE)
    if rest.returncode == 0 and not BAR.search(rest.stdout) and stats() == []:
        held("before any verdict no gauge", "no bar drawn, no stats played")
    else:
        failures.append(f"  ✗ rest                        {stats()} {rest.stdout[-600:]!r} {rest.stderr[-300:]!r}")

    # --- after the verdict: stats played, 17% · pp 33%, the bar in two looks and its empty cells -----------------
    post.clear_journal()
    turned = render("ag1", "--render", "dialogue", *SIZE, "--styles", "--press", "i,h,i,enter,wait:waiting")
    plain = P.ANSI.sub("", turned.stdout)
    row = next((one for one in turned.stdout.split("\n") if GAUGE.search(P.ANSI.sub("", one))), "")
    full = {style for style, text in SEGMENT.findall(row) if "▰" in text}
    empty = {style for style, text in SEGMENT.findall(row) if "▱" in text}
    if (turned.returncode == 0 and GAUGE.search(plain) and stats() == ["stats ag1 w00001 --json"]
            and len(full) >= 2 and empty and not empty & full):
        held("after the verdict the gauge reads the face", f"{GAUGE.search(plain).group(0)!r}; {stats()}; the used "
             f"cells in {len(full)} looks, the empty ones in another")
    else:
        failures.append(f"  ✗ gauge                       {stats()} full={full} empty={empty} {plain[-900:]!r} "
                        f"{turned.stderr[-300:]!r}")

    # --- a call measured during the turn: the gauge moves before the verdict, the measure without `~` -----------
    post.use(P.measured_script())
    post.clear_journal()
    live = render("ag1", "--render", "dialogue", *SIZE, "--press", "i,h,i,enter,wait:context")
    plain_live = P.ANSI.sub("", live.stdout)
    if live.returncode == 0 and MEASURED.search(plain_live) and "~42%" not in plain_live and stats() == []:
        held("a call measured moves the gauge during the turn", f"{MEASURED.search(plain_live).group(0)!r} at the "
             "flow's context, before any verdict and any stats played")
    else:
        failures.append(f"  ✗ measured live               {stats()} {plain_live[-700:]!r} {live.stderr[-300:]!r}")
    post.use(P.SCRIPT)

    # --- a run without context: ctx — after its verdict ----------------------------------------------------------
    post.clear_journal()
    flowless = render("ag1", "--run", "w00009", "--render", "dialogue", *SIZE, "--press", "i,h,i,enter,wait:waiting")
    if flowless.returncode == 0 and not BAR.search(flowless.stdout) and "stats ag1 w00009 --json" in stats():
        held("a run without context draws no gauge", f"{stats()}")
    else:
        failures.append(f"  ✗ flowless                    {stats()} {flowless.stdout[-600:]!r} {flowless.stderr[-300:]!r}")

    # --- a run taken up: its gauge before any message ------------------------------------------------------------
    post.clear_journal()
    taken = render("ag1", "--run", "w00001", "--render", "dialogue", *SIZE)
    if taken.returncode == 0 and GAUGE.search(taken.stdout) and stats() == ["stats ag1 w00001 --json"]:
        held("a run taken up says its gauge at once", f"{GAUGE.search(taken.stdout).group(0)!r} before any message")
    else:
        failures.append(f"  ✗ taken up                    {stats()} {taken.stdout[-600:]!r} {taken.stderr[-300:]!r}")
    # --- the budget of the run on the status line ----------------------------------------------------------
    post.use(P.budget_script([0.42, 1.7, 2.0]))
    turns = [post.render("ag1", "--render", "dialogue", "--size", "160x30", "--press", ",".join([TURN] * n), "--styles")
             for n in (1, 2, 3)]
    plain = [P.status_of(P.ANSI.sub("", one.stdout)) for one in turns]
    spent = ("0.42", "1.70", "2.00")
    looks = [P.styles_of(one.stdout, rf"{re.escape(used)}/2\.00") for one, used in zip(turns, spent)]
    bars = [re.search(rf"{re.escape(used)}/2\.00\D+([▰▱]{{10}})", line) for line, used in zip(plain, spent)]
    bold = any("1" in code.split(";")[:1] for code in looks[2])
    if (all(one.returncode == 0 for one in turns) and all(bars)
            and [bar.group(1).count("▰") for bar in bars] == [2, 9, 10]
            and len({looks[0], looks[1], looks[2]}) == 3 and bold):
        held("the status says the budget of the run", f"{[bar.group(0) for bar in bars]}; three looks, the last "
             "one bold")
    else:
        failures.append(f"  ✗ budget                      {plain} {[sorted(one) for one in looks]} "
                        f"{turns[0].stderr[-300:]!r}")
    post.use(P.budget_script([0.42], cap=None))
    free = post.render("ag1", "--render", "dialogue", "--size", "160x30", "--press", TURN)
    status = P.status_of(free.stdout)
    if free.returncode == 0 and not BAR.search(status) and "/" not in status and "prov" in status and "m1" in status:
        held("a run without a cap says no budget", status.strip()[:100])
    else:
        failures.append(f"  ✗ no cap                      rc={free.returncode} {status!r} {free.stderr[-300:]!r}")

    # --- a reading under way: the spinner turns and the status says what is read ---------------------------
    post.use({**P.SCRIPT, "faces": {**P.FACES, "slow": {"status": 2.0}}})
    loading = post.render("--render", "agents", "--size", "120x30", "--press", "u,spinning")
    spun = re.search(r"^spinning (\d+)$", loading.stdout, re.M)
    said = P.status_of("\n".join(line for line in loading.stdout.split("\n") if not line.startswith("spinning ")))
    try:
        reading = P.palette_constant("READING")
    except KeyError:
        reading = None
    if loading.returncode == 0 and spun and spun.group(1) == "1" and reading and reading in said:
        held("a reading under way is said", f"the spinner turns; the status: {said.strip()[:90]!r}")
    else:
        failures.append(f"  ✗ loading said                rc={loading.returncode} spun={spun and spun.group(1)} "
                        f"reading={reading!r} status={said!r} {loading.stderr[-300:]!r}")
    return 0
