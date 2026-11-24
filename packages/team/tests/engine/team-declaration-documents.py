"""Scenario `team-declaration-documents` -- 5 case(s) (split out of `team-declaration` by rule 10): the team's
documents beside `TEAM.md` -- a common document that mounts, a season's documents -- judged as `team start` judges them
and said by `team declaration`. No wake-up plays: every start is `--no-tick`.
- (i) the common document judged: a `TEAM-<name>-common.md` that mounts, its law coded outside `TM` --
  `declaration --json` says rc 0, `verdict {ok: false}`, its refusal `common-code-prefix`, the very code `team start`
  refuses with; the code turned `TM1`, `verdict {ok: true}`; the team's directory byte-identical across the reads
- (j) the season's documents declared: a `SEASON.md` naming the preset `seasons/house-flow` (`_templates.py`) --
  `season` its path, text and digest, `declared.documents` its lines by key, `declared.values` each value `from`
  `built-in`, `default` or `season`; started, `pending: []`; a value changed, `changed: true` and `pending` on
  `documents` with the start's digests and the file's; a value nothing declares, rc 0 and `verdict {ok: false}` with `value-unknown`, the
  team's directory and journal byte for byte; a team without `SEASON.md` says `season: null`
- (k) the body read in bytes (s.1603): a `TEAM.md` written with CRLF line endings, its body handed back as it stands
  by `declare --body-file <path>` and by `--body-file -` -- `written: []`, the file byte for byte
- (l) a key on two lines (s.1607): `documents:` says `all` on two lines -- `declare --document "all notes/plain"`
  leaves one line `all notes/plain` and `declaration` says `verdict {ok: true}`; `--no-document all` leaves none
- (m) an edge named by its target (A4): `reports:` says `a b -> pp` and `a c -> b` -- `declare --report "c -> b"`
  leaves `a b -> pp` and `c -> b`; from the same file, `--no-report b` leaves `a b -> pp` alone

"""
from __future__ import annotations

import json

from tests.harness import cli, support

T = support(__file__, "team")
S = support(__file__, "templates")
code = T.refusal_code


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={}, packages=("agent", "team", "steering", "plan"))

    def declaration(name: str) -> dict:
        return T.declaration_read(h, name)

    h.declare("new", T.judged_team("lead", "dev"))         # a team without SEASON.md, the one (j) reads last

    # --- (i) the common document judged: its verdict said, never refused ------------------------------------------
    h.declare("cm", "---\nagents: |\n  cw agents/cw\nroot: cw\nschedule: off\n---\nHold it.\n")
    common = h.teams / "cm" / "TEAM-cm-common.md"
    common.write_text("---\nmount: turn.begin\nconstraints.behavior: |\n  KX1  keep it short.\n---\nHold.\n",
                      encoding="utf-8")
    before = {one.name: one.read_bytes() for one in (h.teams / "cm").iterdir()}
    face_bad = declaration("cm")
    refused = h.call("team", "start", "cm", "--message", "go", "--no-tick")
    common.write_text(common.read_text(encoding="utf-8").replace("KX1", "TM1"), encoding="utf-8")
    face_good = declaration("cm")
    unchanged = {one.name: one.read_bytes() for one in (h.teams / "cm").iterdir()}
    unchanged["TEAM-cm-common.md"] = unchanged["TEAM-cm-common.md"].replace(b"TM1", b"KX1")
    bad = face_bad.get("verdict") or {}
    if (bad.get("ok") is False and code(bad.get("refusal") or "") == "common-code-prefix"
            and refused.returncode == 2 and code(refused.stderr) == "common-code-prefix"
            and (face_good.get("verdict") or {}) == {"ok": True, "refusal": None}
            and unchanged == before and not h.journal_of("cm").exists() and not h.agent_stands("agents/cw")):
        bench.refusals += 1
        held("(i) the common document judged", "a mounted common coded KX1: declaration says verdict ok false, "
             "common-code-prefix, the code start refuses with, nothing written; coded TM1: verdict ok; the team's "
             "directory byte-identical")
    else:
        failures.append(f"  ✗ (i) the common judged       bad={bad} good={face_good.get('verdict')} "
                        f"start={refused.returncode}:{refused.stderr.strip()[-200:]!r} same={unchanged == before} "
                        f"journal={h.journal_of('cm').exists()}")

    # --- (j) the season's documents declared -----------------------------------------------------------------
    S.laid(h.house / "teams" / "templates", S.SHELF)
    h.declare("ct", "---\nagents: |\n  cx agents/cx\nroot: cx\nschedule: off\nroles: |\n  make cx\n  inspect cx\n---\n"
                    "Under a season.\n")
    season = h.teams / "ct" / "SEASON.md"
    season.write_text(S.SEASON, encoding="utf-8")
    first = declaration("ct")
    begun = h.call("team", "start", "ct", "--no-tick")
    settled = declaration("ct")
    season.write_text(S.SEASON.replace("alice", "bob"), encoding="utf-8")
    moved = declaration("ct")
    season.write_text(S.SEASON.replace("  lead = alice\n", "  lead = alice\n  ghost = x\n"), encoding="utf-8")
    before = S.kept(h, "ct")
    bad_call = h.call("team", "declaration", "ct", "--json")
    bad = declaration("ct")
    same = S.kept(h, "ct") == before
    lines = [{"key": "all", "team": [], "season": ["notes/plain"]},
             {"key": "make", "team": [], "season": ["sources/by-batch"]},
             {"key": "inspect", "team": [], "season": ["review/pair"]}]
    values = [{"name": "team", "value": "ct", "from": "built-in"},
              {"name": "checker", "value": "inspect", "from": "default"},
              {"name": "remote", "value": "origin", "from": "default"},
              {"name": "branch", "value": "batch-<lot>", "from": "default"},
              {"name": "lead", "value": "alice", "from": "season"}]
    pending = {one.get("key"): one for one in moved.get("pending") or []}
    shift = pending.get("documents") or {}
    pair = "roles/TEAM-ct-pair.md"
    if (first.get("season") == {"path": "teams/ct/SEASON.md", "text": S.SEASON, "digest": S.digest(S.SEASON.encode())}
            and (first.get("declared") or {}).get("documents") == lines
            and (first.get("declared") or {}).get("values") == values
            and begun.returncode == 0 and settled.get("pending") == [] and settled.get("changed") is False
            and moved.get("changed") is True and list(pending) == ["documents"]
            and ((shift.get("started") or {}).get("rendered") or {}).get(pair)
            != ((shift.get("declared") or {}).get("rendered") or {}).get(pair) is not None
            and bad_call.returncode == 0 and (bad.get("verdict") or {}).get("ok") is False
            and code((bad.get("verdict") or {}).get("refusal") or "") == "value-unknown" and same
            and "season" in (declaration("new")) and declaration("new")["season"] is None):
        held("(j) the season's documents declared", "season path, text, digest; declared.documents house-flow's "
             "three lines, values from built-in, default and season; started: pending []; lead bob: changed, pending "
             "documents, the pair's digest moved; ghost: verdict value-unknown, rc 0, nothing written; no SEASON.md: null")
    else:
        failures.append(f"  ✗ (j) the documents declared season={first.get('season')} "
                        f"documents={(first.get('declared') or {}).get('documents')} values={(first.get('declared') or {}).get('values')} "
                        f"rc={begun.returncode} settled={settled.get('pending')}/{settled.get('changed')} "
                        f"moved={moved.get('changed')}/{pending} bad={bad_call.returncode}/{bad.get('verdict')} same={same} "
                        f"{begun.stderr.strip()[-200:]!r}")

    # --- (k) the body read in bytes (s.1603) ---------------------------------------------------------------------
    body = "Hold it.\r\nTwo lines.\r\n"
    crlf = ("---\r\nagents: |\r\n  bw agents/bw\r\nroot: bw\r\nschedule: off\r\n---\r\n" + body).encode("utf-8")
    h.declare("cb", "")
    team_md = h.teams / "cb" / "TEAM.md"
    team_md.write_bytes(crlf)
    same = h.bench.temp() / "body.md"
    same.write_bytes(body.encode("utf-8"))

    def written_by(*args: str, stdin: str | None = None) -> list | None:
        played = cli(h.engine, "--instance", str(h.house), "team", "declare", "cb", *args, "--json", cwd=h.ws,
                     stdin=stdin, env=h.env)
        try:
            return json.loads(played.stdout.strip().splitlines()[-1]).get("written")
        except (ValueError, IndexError):
            return None

    by_file = written_by("--body-file", str(same))
    file_kept = team_md.read_bytes() == crlf
    team_md.write_bytes(crlf)
    by_stdin = written_by("--body-file", "-", stdin=body)
    stdin_kept = team_md.read_bytes() == crlf
    if by_file == [] and file_kept and by_stdin == [] and stdin_kept:
        held("(k) the body read in bytes", "a CRLF TEAM.md, its body handed back by --body-file <path> and by "
             "--body-file -: written [], the file byte for byte")
    else:
        failures.append(f"  ✗ (k) the body in bytes       file={by_file}/{file_kept} stdin={by_stdin}/{stdin_kept}")

    # --- (l) a key on two lines (s.1607) -------------------------------------------------------------------------
    h.declare("dk", "---\nagents: |\n  dw agents/dw\nroot: dw\nschedule: off\ndocuments: |\n  all notes/plain\n"
                    "  all notes/dated\n---\nTwo lines of one key.\n")
    keyed = h.teams / "dk" / "TEAM.md"

    def all_lines() -> list[str]:
        block = keyed.read_text(encoding="utf-8").split("documents: |\n", 1)
        rows = block[1].split("---\n", 1)[0].splitlines() if len(block) == 2 else []
        return [row.strip() for row in rows if row.startswith("  ") and row.split()[0] == "all"]

    joined = h.call("team", "declare", "dk", "--document", "all notes/plain")
    one_line, joined_verdict = all_lines(), declaration("dk").get("verdict") or {}
    keyed.write_text(keyed.read_text(encoding="utf-8").replace("  all notes/plain\n",
                                                               "  all notes/plain\n  all notes/dated\n"),
                     encoding="utf-8")
    twice = all_lines()
    dropped = h.call("team", "declare", "dk", "--no-document", "all")
    if (joined.returncode == 0 and one_line == ["all notes/plain"] and joined_verdict.get("ok") is True
            and twice == ["all notes/plain", "all notes/dated"] and dropped.returncode == 0 and all_lines() == []):
        held("(l) a key on two lines", "documents: all on two lines -- --document \"all notes/plain\" leaves one line, "
             "verdict ok; --no-document all leaves none")
    else:
        failures.append(f"  ✗ (l) a key on two lines     joined={joined.returncode} {one_line} {joined_verdict} "
                        f"twice={twice} dropped={dropped.returncode} {all_lines()} "
                        f"{(joined.stderr or dropped.stderr).strip()[-200:]!r}")

    # --- (m) an edge named by its target (A4) ---------------------------------------------------------------------
    edged = ("---\nagents: |\n  pp agents/pp\n  a agents/a\n  b agents/b\n  c agents/c\nroot: pp\nschedule: off\n"
             "reports: |\n  a b -> pp\n  a c -> b\n---\nTwo edges, one first source.\n")
    h.declare("rp", edged)
    edges_md = h.teams / "rp" / "TEAM.md"

    def edges() -> list[str]:
        block = edges_md.read_text(encoding="utf-8").split("reports: |\n", 1)
        rows = block[1].split("---\n", 1)[0].splitlines() if len(block) == 2 else []
        return [row.strip() for row in rows if row.startswith("  ")]

    moved = h.call("team", "declare", "rp", "--report", "c -> b")
    after_report = edges()
    edges_md.write_text(edged, encoding="utf-8")
    cut = h.call("team", "declare", "rp", "--no-report", "b")
    after_cut = edges()
    if (moved.returncode == 0 and after_report == ["a b -> pp", "c -> b"]
            and cut.returncode == 0 and after_cut == ["a b -> pp"]):
        held("(m) an edge named by its target", "a b -> pp and a c -> b: --report \"c -> b\" leaves a b -> pp and "
             "c -> b; --no-report b leaves a b -> pp")
    else:
        failures.append(f"  ✗ (m) an edge by its target   report={moved.returncode} {after_report} "
                        f"no-report={cut.returncode} {after_cut} {(moved.stderr or cut.stderr).strip()[-200:]!r}")

    return 0
