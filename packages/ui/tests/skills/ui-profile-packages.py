"""Scenario `ui-profile-packages` -- the packages of a new run in its profile (plan ui, batch le-profil-de-lancement),
on the bench's `pp-chat` witness: `ag1`'s `status --json` says `packages` (`plan` and `steering`, both on), `ag2`'s
says none, as a face before agent 0.24.1:
- `n` on `ag1`: the profile shows a line `packages`, the state of each package; `enter` on it opens them in their
  overlay; `space` on `plan`, `enter` -- the line says `plan on → off · steering on`, and `enter` opens the run with
  `--package plan=off` after the other flags
- nothing toggled: no `--package`
- `n` on `ag2`, whose face says no packages: no line
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the providers' face
TO_PACKAGES = "tab,tab,tab,tab"      # from the model, down to the packages: budget, effort, permissions, packages


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-profile-packages")
    render = post.render

    def opened() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("open")]

    # --- the line of the packages, read from the face; one toggled in their overlay, composed after the flags ------
    staged = render("--render", "agents", "--size", "110x45", "--press",
                    f"n,wait:none:1.5,{TO_PACKAGES},enter,space,enter", *PAUSE)
    marked = [row for row in staged.stdout.split("\n") if "plan on → off" in row and "steering on" in row]
    post.clear_journal()
    toggled = render("--render", "dialogue", "--size", "110x45", "--press",
                     f"2,n,wait:none:1.5,{TO_PACKAGES},enter,space,enter,enter,wait:waiting", "--wait", "none:1")
    wanted = [f"open ag1 --provider {P.PROVIDER} --model m1 --package plan=off"]
    if staged.returncode == 0 and marked and toggled.returncode == 0 and opened() == wanted:
        held("a package toggled opens the run without it", f"the line of the face says {marked[0].strip(' ┃│▊▎')!r}; "
             f"the journal says {opened()}")
    else:
        failures.append(f"  ✗ toggled                     {marked} {opened()} {staged.stdout[-1500:]!r} "
                        f"{toggled.stderr[-300:]!r}")

    # --- nothing toggled, no --package ---------------------------------------------------------------------
    post.clear_journal()
    plain = render("--render", "dialogue", "--size", "110x45", "--press", "2,n,wait:none:1.5,enter,wait:waiting",
                   "--wait", "none:1")
    if plain.returncode == 0 and opened() == [f"open ag1 --provider {P.PROVIDER} --model m1"]:
        held("nothing toggled, no --package", f"the journal says {opened()}")
    else:
        failures.append(f"  ✗ untouched                   {opened()} {plain.stderr[-300:]!r}")

    # --- a face without packages: no line ------------------------------------------------------------------
    bare = render("--render", "agents", "--size", "110x45", "--press", "down,n", *PAUSE)
    if bare.returncode == 0 and "a new run of ag2" in bare.stdout and "steering on" not in bare.stdout:
        held("a face without packages shows no line", "ag2's profile: no packages")
    else:
        failures.append(f"  ✗ bare                        rc={bare.returncode} {bare.stdout!r}")
    return 0
