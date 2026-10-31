"""Scenario `ui-packages` -- the overlay of the packages of a run, an editor of its own (plan ui, batch
l-overlay-des-packages), on the bench's `pp-chat` witness: `ag1`'s run plays `plan`, `steering` and `ghost`; a switch
of `steering` waits for the next message, one of `plan` plays at once, `ghost` is a name the verb does not know:
- `k` then `space` on two lines: both marked `on → off`, nothing sent
- `enter` sends one `package` per line changed; `escape` sends none
- a switch that waits is seen until it plays: `⧗` on the tab's title, `packages: steering off …` on the status, `k`
  says `pending`; the next message plays it and every mark leaves
- a switch the verb refuses: the remedy says its code and its detail, nothing waits
- a package the caller holds REQUIRED, on the overlay the bench builds itself (`PackagesScreen(required=…)`, no
  caller passes one yet): its line greyed, `space` leaves it as it is, `enter` gives the other lines alone
The packages in a run's profile (`p`): `ui-packages-profile`; of a new run (`n`): `ui-profile-packages`.
"""
from __future__ import annotations

import json
import subprocess

from tests.harness import SOURCE, support

P = support(__file__, "dialogue")
SIZE = ("--size", "160x30")
SENT = "i,h,i,enter,wait:waiting,escape"
SKILL = SOURCE / "packages" / "ui" / "skills" / "pp-ui"
TEXTUAL = ("uv", "run", "--quiet", "--no-project", "--with", "textual==8.2.8", "--with", "pyyaml>=6", "python3")
PROBE = """
import asyncio, json, sys
sys.path.insert(0, sys.argv[1])
from textual.app import App
from panes.overlays import PackagesScreen


class Probe(App):
    result = "none"

    def on_mount(self):
        self.push_screen(PackagesScreen("packages of the season", {"plan": True, "team": True}, {},
                                        required={"team"}), self.given)

    def given(self, found):
        self.result = found


async def main():
    app = Probe()
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        screen = app.screen
        listed = screen.query_one("#packages")
        options = [listed.get_option_at_index(n) for n in range(listed.option_count)]
        rows, disabled = [str(one.prompt) for one in options], [one.disabled for one in options]
        help_text = str(screen.query_one("#packages-help").render())
        listed.highlighted = 1
        screen.action_toggle()
        held = dict(screen.staged)
        listed.highlighted = 0
        await pilot.press("space", "enter")
        await pilot.pause()
    print(json.dumps({"rows": rows, "disabled": disabled, "help": help_text, "held": held, "result": app.result}))


asyncio.run(main())
"""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-packages", P.held_script())
    render, tabs_of = post.render, post.tabs_of

    def sent() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("package")]

    # --- space toggles in the overlay alone ------------------------------------------------------------
    post.clear_journal()
    toggled = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},k,space,down,space", "--wait", "none:1")
    rows = [row for row in toggled.stdout.split("\n") if "→" in row]
    if (toggled.returncode == 0 and sent() == [] and any("plan" in row and "on → off" in row for row in rows)
            and any("steering" in row and "on → off" in row for row in rows) and "[space]" in toggled.stdout):
        held("space toggles in the overlay alone", "plan and steering marked on → off; the journal has no package")
    else:
        failures.append(f"  ✗ toggle                      rc={toggled.returncode} {sent()} {toggled.stdout!r} "
                        f"{toggled.stderr[-300:]!r}")

    # --- enter sends the differences, escape none --------------------------------------------------------
    post.clear_journal()
    applied = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},k,space,down,space,enter,wait:package,k")
    first = sent()
    text = applied.stdout
    status = text.rstrip("\n").split("\n")[-1]
    post.clear_journal()
    render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},k,space,escape", "--wait", "none:1")
    cancelled = sent()
    if (applied.returncode == 0 and first == [P.switched("ag1", "plan", False), P.switched("ag1", "steering", False)]
            and cancelled == []):
        held("enter sends the differences, escape none", f"enter: {first}; escape: no package")
    else:
        failures.append(f"  ✗ apply                       {first} / {cancelled} {applied.stderr[-300:]!r}")

    # --- the wait is seen until it plays ------------------------------------------------------------------
    post.clear_journal()
    played = render("ag1", "--render", "dialogue", *SIZE, "--press",
                    f"{SENT},k,down,space,enter,wait:package,i,g,o,enter", "--wait", "principal")
    status_p = played.stdout.rstrip("\n").split("\n")[-1]
    if (applied.returncode == 0 and "⧗" in tabs_of(text) and "steering" in status
            and played.returncode == 0 and "⧗" not in tabs_of(played.stdout) and "steering" not in status_p
            and sent() == [P.switched("ag1", "steering", False)]):
        held("a switch that waits is seen until it plays", f"the bar {tabs_of(text).strip()!r}, the status names "
             "steering; after the next message, no mark on the bar nor the status")
    else:
        failures.append(f"  ✗ pending                     bar={tabs_of(text)!r} status={status!r} pending={pending} / "
                        f"bar={tabs_of(played.stdout)!r} status={status_p!r} {sent()} {played.stderr[-300:]!r}")

    # --- a refusal says its code and its detail ----------------------------------------------------------
    refused = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},k,down,down,space,enter",
                     "--wait", "refused")
    lines = refused.stdout.rstrip("\n").split("\n")
    if (refused.returncode == 0 and "package-unknown" in lines[-2] and "ghost" in lines[-2]
            and "⧗" not in tabs_of(refused.stdout)):
        held("a refused switch is said with its detail", lines[-2].strip()[:100])
    else:
        failures.append(f"  ✗ refused                     rc={refused.returncode} {lines[-3:]!r} {refused.stderr[-300:]!r}")
    # --- a package required: greyed, never toggled ----------------------------------------------------------
    probe = bench.temp() / "packages-probe.py"
    probe.write_text(PROBE, encoding="utf-8")
    played = subprocess.run([*TEXTUAL, str(probe), str(SKILL)], capture_output=True, text=True, cwd=bench.temp(),
                            timeout=60)
    try:
        said = json.loads(played.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        said = {}
    rows = said.get("rows") or []
    if (played.returncode == 0 and len(rows) == 2 and "plan" in rows[0] and "team" in rows[1]
            and said.get("disabled") == [False, True] and said.get("help")
            and said.get("held") == {"plan": True, "team": True} and said.get("result") == {"plan": False}):
        held("a package required never toggles", f"rows {said['rows']}, team greyed; space on it left "
             f"{said['held']}; enter gave {said['result']}")
    else:
        failures.append(f"  ✗ required                    rc={played.returncode} {said} {played.stderr[-800:]!r}")
    return 0
