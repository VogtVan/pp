"""Scenario `continuity-boot` -- what continuity serves at boot.initialize:
- RECALL attaches with its `continuity-recall` section: the entries of the period, oldest
  first, none older; an empty period or `continuity_recall_days: 0` renders neither the
  section nor the brief
- HISTORY, the weekly digest, is a declared cadence on the store's records `history` and
  `operations`: due after an operation newer than the last digest once the anchored day is
  crossed, with pp-continuity offered; the digest written from the block consumes the
  crossing; a stale digest with nothing since and `never` stay silent
- RECALL (a contributor) is served before HISTORY (a cadence) when both are due
- the recall-only profile: `continuity_history_day: never` and `continuity_recall_days: 7`
  together serve the recall and no digest
- a period past the bound: the section carries the 40 latest operations of the period, oldest
  first, then how many older ones are left and the `--skip` call that reads them
- the kit alone knows neither RECALL, its section, HISTORY nor pp-continuity

Two houses: the instance with continuity, and the kit alone for the absence.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from conductor import contributions, discovery, render
from tests.harness import support

C = support(__file__, "continuity")

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
SECTION = "▌ INFORMATION — continuity-recall"
BRIEF = "▌ INFORMATION — RECALL"
DIGEST = "▸ HISTORY{"


def _fresh(env):
    """The environment on a RE-DISCOVERED member: what the records say now."""
    return env.__class__(name=env.name, made=env.made,
                         member=discovery.instance_member(env.engine), engine=env.engine)


def _boot(env):
    """-> (the boot block, its rendering) of a fresh run."""
    opener = _fresh(env).conductor()
    block = opener.start(opener.boot("BOOT.md"))
    shown = render(block)
    opener.forget()
    return block, shown


def _section(shown: str) -> str:
    """-> the recall section's text, up to the next section mark."""
    at = shown.find(SECTION)
    if at < 0:
        return ""
    rest = shown[at + len(SECTION):]
    end = rest.find("\n▌ ")
    return rest if end < 0 else rest[:end]


def _lines(section: str) -> list[str]:
    """-> the operations a recall section carries: its lines that open on a date."""
    return [one for one in section.splitlines() if one[:4].isdigit()]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    now = datetime.now(timezone.utc)
    today = WEEKDAYS[now.weekday()]
    env = bench.env("boot", packages=("continuity",))

    def setting(key: str, value: str) -> None:
        if not C.setting(env, key, value):
            failures.append(f"  ✗ setting                    {key} absent from SETTINGS.md")

    # --- a fresh install: no recall, no digest ------------------------------------------------
    setting("continuity_history_day", today)
    _, first = _boot(env)
    if DIGEST not in first and BRIEF not in first and SECTION not in first:
        held("a fresh install boots silent", "no record written: no recall, the digest is not due")
    else:
        failures.append("  ✗ fresh install              HISTORY or RECALL played on records never written")

    # --- a stale digest with nothing since: silent; `never`: silent ---------------------------
    C.history(env.made, now - timedelta(days=8))
    C.operations(env.made, [(now - timedelta(days=9), "before the digest")])
    _, quiet = _boot(env)
    C.operations(env.made, [(now - timedelta(days=10), "the old one"),
                            (now - timedelta(days=3), "the recent two"),
                            (now - timedelta(days=1), "the recent one")])
    setting("continuity_history_day", "never")
    _, never = _boot(env)
    setting("continuity_history_day", today)

    # --- operations since the digest, the day crossed: the recall of the period, the digest due
    block, served = _boot(env)
    section = _section(served)
    if DIGEST not in quiet and DIGEST not in never and DIGEST in served:
        held("nothing since is silent, never is silent, a move is due",
             "a stale digest with no newer operation owes nothing; `never` switches the digest off; "
             "operations since bring it back")
    else:
        failures.append(f"  ✗ since/never                quiet={DIGEST in quiet} never={DIGEST in never} "
                        f"moved={DIGEST in served}")
    if (BRIEF in served and section and "the recent two" in section and "the recent one" in section
            and "the old one" not in section and "before the digest" not in section
            and section.find("the recent two") < section.find("the recent one")):
        held("the recall serves the period, oldest first",
             "the two operations within 7 days, the 9- and 10-day ones left out")
    else:
        failures.append(f"  ✗ recall period              brief={BRIEF in served} section={section[:120]!r}")
    if DIGEST in served and "pp-continuity" in served:
        held("the digest is due after an operation and the crossing",
             "HISTORY CALLed at boot.initialize from the manifest's cadence; pp-continuity offered")
    else:
        failures.append(f"  ✗ digest due                 {DIGEST in served} {'pp-continuity' in served}")
    if SECTION in served and block.document == "HISTORY":
        held("the recall comes before the digest",
             "RECALL (attach) is served behind, HISTORY (cadence) is the pending frame ahead -- contributors, then the cadences due")
    else:
        failures.append(f"  ✗ order at boot              recall={SECTION in served} pending={block.document!r}")

    # --- the digest written from the block: one entry, the next boot silent -----------------
    before = len(C.entries(env.made, "history"))
    rc, _, err = contributions.run_skill(
        env.made, "pp-continuity", ["history", "add", "the week in one paragraph"])
    digests = C.entries(env.made, "history")
    _, after = _boot(env)
    if (rc == 0 and len(digests) == before + 1
            and digests[-1].body == {"synthesis": "the week in one paragraph"} and DIGEST not in after):
        held("the digest lands and consumes the crossing",
             "pp-continuity history add writes ONE {synthesis} entry; the next boot carries no HISTORY")
    else:
        failures.append(f"  ✗ digest lands               rc={rc} {err.strip()[-80:]!r} digests={len(digests)} "
                        f"again={DIGEST in after}")

    # --- the key at 0: neither the section nor the brief -------------------------------------
    setting("continuity_recall_days", "0")
    _, muted = _boot(env)
    setting("continuity_recall_days", "7")
    if SECTION not in muted and BRIEF not in muted:
        held("the key at 0 recalls nothing", "no recall section, and no brief without it")
    else:
        failures.append(f"  ✗ key at 0                   section={SECTION in muted} brief={BRIEF in muted}")

    # --- the recall-only profile: the two keys together --------------------------------------
    setting("continuity_history_day", "never")
    _, alone = _boot(env)
    if (BRIEF in alone and SECTION in alone and "the recent one" in _section(alone)
            and DIGEST not in alone):
        held("the boot serves the recall alone", "RECALL and its section carry yesterday's operation; no HISTORY under `never`")
    else:
        failures.append(f"  ✗ recall-only boot           brief={BRIEF in alone} section={SECTION in alone} "
                        f"history={DIGEST in alone}")

    # --- a period past the bound: its latest page, then the rest and the call that reads it ----
    heavy = [(now - timedelta(minutes=n), f"entry {n:04d} " + "x" * 180) for n in range(300, 0, -1)]
    C.operations(env.made, heavy)
    within = 300 + 2                       # the heavy ones, `the recent two`, `the recent one`
    _, loaded = _boot(env)
    carried = _lines(_section(loaded))
    page = len(carried)
    if (page == 40 and "entry 0001" in carried[-1] and "entry 0040" in carried[0]
            and "entry 0041" not in loaded and f"{within - page} older" in _section(loaded)
            and f"recall last 7 --skip {page}`" in _section(loaded)):
        held("a period past the bound: its latest page and the rest said",
             f"{within} operations in the period: the section carries the {page} latest, oldest first, "
             f"then the {within - page} older with their `--skip {page}` call")
    else:
        failures.append(f"  ✗ recall past the bound      carried={page} first={carried[:1]!r} "
                        f"last={carried[-1:]!r} tail={_section(loaded)[-200:]!r}")

    # --- the kit alone: no recall, no digest --------------------------------------------------
    bare = bench.env("boot-kit")
    C.operations(bare.made, [(now - timedelta(days=1), "an operation the kit ignores")])
    _, kit = _boot(bare)
    if "RECALL" not in kit and SECTION not in kit:
        held("the kit alone recalls nothing", "an operation written, a boot: no RECALL, no payload section")
    else:
        failures.append("  ✗ kit alone                  RECALL or its payload appeared")
    if "HISTORY" not in kit and "pp-continuity" not in kit:
        held("the kit alone knows no digest", "an operation stamped, a boot: no HISTORY, no pp-continuity offer")
    else:
        failures.append("  ✗ kit alone                  HISTORY or pp-continuity appeared")
    return 0
