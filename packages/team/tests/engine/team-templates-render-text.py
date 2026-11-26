"""Scenario `team-templates-render-text` -- 4 case(s): a document rendered dry on a CANDIDATE text (batch
l-apercu-du-texte-tape, s.1598 s.1599) -- `team templates --render <d>/<n> --team <t> [--season] --text-file <path>|-`
renders with the values the start would take if the text were written: the text in the place of `TEAM.md` (of
`SEASON.md` under `--season`), the other file read on the disk. The sibling of `team-templates-house` (n), its shelf
shared in `_templates.py`. Nothing written.
- (a) s.1598: `rn`'s TEAM.md gives `day = friday`; a candidate TEAM.md without the line renders `day` at the template's
  default `monday`, never the disk's `friday`; a candidate giving `day = sunday` renders `sunday`; a path given as
  `--text-file <path>` reads the same
- (b) s.1599: SEASON.md gives `day = saturday`; a candidate TEAM.md without `day` renders `saturday`, the season's
- (c) `--season --text-file -`: a candidate SEASON.md without `values:` renders `friday`, TEAM.md's on the disk; one
  giving `day = sunday` renders `sunday`
- (d) the usage: `--text-file -` or `--season` without `--team`, `--season` without `--text-file`; nothing written
"""
from __future__ import annotations

import json

from tests.harness import cli, support

T = support(__file__, "team")
S = support(__file__, "templates")
laid, kept = S.laid, S.kept

TEAM_TEXT = ("---\nagents: |\n  m agents/m\nroot: m\nschedule: off\ndocuments: |\n  all notes/dated\nvalues: |\n"
             "  day = friday\n---\n")
WITHOUT = TEAM_TEXT.replace("values: |\n  day = friday\n", "")
SUNDAY = TEAM_TEXT.replace("friday", "sunday")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    c = T.House(bench, script={}, slug="typed")
    laid(c.house / "teams" / "templates", S.SHELF)
    c.declare("rn", TEAM_TEXT)
    before = kept(c, "rn")

    def rendered(text: str | None, *args: str) -> tuple:
        played = cli(c.engine, "--instance", str(c.house), "team", "templates", "--render", "notes/dated", *args,
                     "--json", cwd=c.ws, env=c.env, stdin=text)
        try:
            return played, json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return played, {}

    def day(face: dict) -> tuple:
        return next(((one.get("value"), one.get("from")) for one in face.get("values") or [] if one.get("name") == "day"),
                    None)

    # --- (a) s.1598: the typed TEAM.md, not the disk's ----------------------------------------------------------------
    without, face_w = rendered(WITHOUT, "--team", "rn", "--text-file", "-")
    sunday, face_s = rendered(SUNDAY, "--team", "rn", "--text-file", "-")
    path = bench.temp() / "typed-TEAM.md"
    path.write_text(WITHOUT, encoding="utf-8")
    by_path, face_p = rendered(None, "--team", "rn", "--text-file", str(path))
    if (without.returncode == 0 and day(face_w) == ("monday", "default") and "read on monday" in face_w.get("text", "")
            and sunday.returncode == 0 and day(face_s) == ("sunday", "default") and "read on sunday" in face_s.get("text", "")
            and by_path.returncode == 0 and face_p == face_w):
        held("(a) s.1598: the candidate TEAM.md's values", f"without day: {day(face_w)}; day = sunday: {day(face_s)}; "
             "by path: the same")
    else:
        failures.append(f"  ✗ (a) candidate TEAM.md       rc={without.returncode}/{sunday.returncode}/{by_path.returncode} "
                        f"{face_w} {face_s} {(without.stderr or sunday.stderr or by_path.stderr).strip()[-200:]!r}")

    # --- (b) s.1599: SEASON.md's value stays when TEAM.md's is emptied -------------------------------------------------
    (c.teams / "rn" / "SEASON.md").write_text("---\nvalues: |\n  day = saturday\n---\n", encoding="utf-8")
    seasoned, face_b = rendered(WITHOUT, "--team", "rn", "--text-file", "-")
    if seasoned.returncode == 0 and day(face_b) == ("saturday", "default") and "read on saturday" in face_b.get("text", ""):
        held("(b) s.1599: SEASON.md's value over the candidate TEAM.md", f"{day(face_b)}")
    else:
        failures.append(f"  ✗ (b) season's value kept     rc={seasoned.returncode} {face_b} "
                        f"{seasoned.stderr.strip()[-200:]!r}")

    # --- (c) --season: the candidate SEASON.md, TEAM.md on the disk -----------------------------------------------------
    bare, face_c = rendered("---\n---\n", "--team", "rn", "--season", "--text-file", "-")
    given, face_g = rendered("---\nvalues: |\n  day = sunday\n---\n", "--team", "rn", "--season", "--text-file", "-")
    if (bare.returncode == 0 and day(face_c) == ("friday", "default") and given.returncode == 0
            and day(face_g) == ("sunday", "default")):
        held("(c) --season: the candidate SEASON.md", f"without values: {day(face_c)}; day = sunday: {day(face_g)}")
    else:
        failures.append(f"  ✗ (c) candidate SEASON.md     rc={bare.returncode}/{given.returncode} {face_c} {face_g} "
                        f"{(bare.stderr or given.stderr).strip()[-200:]!r}")

    # --- (d) the usage -------------------------------------------------------------------------------------------------
    after = kept(c, "rn")
    misused = [rendered(WITHOUT, "--text-file", "-")[0], rendered(None, "--season")[0],
               rendered(None, "--team", "rn", "--season")[0]]
    if (all(one.returncode == 2 and one.stderr.startswith("pp-team: usage:") for one in misused)
            and kept(c, "rn") == after and before[1] == after[1]):
        bench.refusals += 3
        held("(d) the usage", "--text-file without --team, --season without --team, --season without --text-file; "
             "nothing written")
    else:
        failures.append(f"  ✗ (d) usage                   {[(one.returncode, one.stderr.strip()[:60]) for one in misused]}")
    return 0
