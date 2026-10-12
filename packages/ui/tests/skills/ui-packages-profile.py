"""Scenario `ui-packages-profile` -- the packages in a run's profile (plan ui, batch le-profil-de-lancement; cut from
`ui-packages`, rule 10), on the bench's `pp-chat` witness: `ag1`'s run plays `plan`, `steering` and `ghost`:
- `p` carries the packages: its line, toggled in their overlay, sends one `package` per line changed at the profile's
  `enter`, no `set`
- a package the caller holds REQUIRED, on the overlay the bench builds itself (`PackagesScreen(required=…)`, no
  caller passes one yet): its line greyed and marked `required`, `space` leaves it as it is, `enter` gives the other
  lines alone; the help says why
The packages of a new run (`n`) are `ui-profile-packages`'s.
"""
from __future__ import annotations

import json
import subprocess

from tests.harness import SOURCE, support

P = support(__file__, "dialogue")
SIZE = ("--size", "160x30")
SENT = "h,i,enter,wait:waiting,escape"
TO_PACKAGES = "tab,tab,tab,tab"      # from the model, down to the packages: budget, effort, permissions, packages
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
    post = P.Post(bench, "ui-packages-profile", P.held_script())
    render = post.render

    def sent() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("package")]

    # --- p carries the packages: one `package` per line changed at the profile's enter -------------------------
    post.clear_journal()
    profiled = render("ag1", "--render", "dialogue", *SIZE, "--press",
                      f"{SENT},p,wait:none:1.5,{TO_PACKAGES},enter,space,enter,enter", "--wait", "package")
    sets = [one for one in post.journal_lines() if one.startswith("set")]
    if profiled.returncode == 0 and sent() == ['package ag1 {"name": "plan", "on": false}'] and sets == []:
        held("p sends the packages changed", f"{sent()}; no set")
    else:
        failures.append(f"  ✗ p packages                  rc={profiled.returncode} {post.journal_lines()} "
                        f"{profiled.stdout[-1200:]!r} {profiled.stderr[-300:]!r}")

    # --- a package required: greyed, never toggled ----------------------------------------------------------
    probe = bench.temp() / "packages-probe.py"
    probe.write_text(PROBE, encoding="utf-8")
    played = subprocess.run([*TEXTUAL, str(probe), str(SKILL)], capture_output=True, text=True, cwd=bench.temp(),
                            timeout=60)
    try:
        said = json.loads(played.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        said = {}
    if (played.returncode == 0 and said.get("rows") == ["plan  on", "team  on · required"]
            and said.get("disabled") == [False, True] and "required" in said.get("help", "")
            and said.get("held") == {"plan": True, "team": True} and said.get("result") == {"plan": False}):
        held("a package required never toggles", f"rows {said['rows']}, team greyed; space on it left "
             f"{said['held']}; enter gave {said['result']}")
    else:
        failures.append(f"  ✗ required                    rc={played.returncode} {said} {played.stderr[-800:]!r}")
    return 0
