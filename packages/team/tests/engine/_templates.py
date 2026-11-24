"""Support of the scenarios `team-templates*` and `team-contract-render` (rule 10): the team presets of the package
and the teams they make, a house's own templates, a house's documents and presets, and the readings the scenarios
share -- loaded by `support(__file__, "templates")`, never collected as a scenario."""
from __future__ import annotations

import hashlib
import json
import re

from tests.harness import support

T = support(__file__, "team")

FIRST = ("supervisor-workers", "lead-reviewers", "chain", "solo", "empty")
TEMPLATES = FIRST + ("council", "triage", "cross-check", "tree")
PRESET = "teams"                     # the directory of the package's team presets
LINE_KEYS = {"template", "kind", "origin", "description", "values"}   # every line of `templates --json`
KEYS = LINE_KEYS | {"documents", "form", "members", "root", "reports", "ceremony", "limits", "intention"}   # a team preset's
LIMITS = {"budget": 5, "launches": 24, "timeout": 900}
# the first five: template -> (members, root, edges, the daily's line or None)
SHAPES = {
    "supervisor-workers": (["supervisor", "worker-1", "worker-2"], "supervisor",
                           [{"from": ["worker-1", "worker-2"], "to": "supervisor"}],
                           "daily every weekday 09:30 with worker-1 worker-2 -> supervisor"),
    "lead-reviewers": (["lead", "reviewer-1", "reviewer-2"], "lead",
                       [{"from": ["reviewer-1", "reviewer-2"], "to": "lead"}],
                       "daily every weekday 09:30 with reviewer-1 reviewer-2 -> lead"),
    "chain": (["step-1", "step-2", "step-3"], "step-1",
              [{"from": ["step-2"], "to": "step-1"}, {"from": ["step-3"], "to": "step-2"}], None),
    "solo": (["worker"], "worker", [], None),
    "empty": (["lead"], "lead", [], None),
}
# the four after them: template -> (members, root, edges, the daily's line or None, limits)
FORMS = {
    "council": (["facilitator", "expert-1", "expert-2", "expert-3"], "facilitator",
                [{"from": ["expert-1", "expert-2", "expert-3"], "to": "facilitator"}], None, LIMITS),
    "triage": (["dispatcher", "spec-a", "spec-b", "spec-c"], "dispatcher",
               [{"from": ["spec-a", "spec-b", "spec-c"], "to": "dispatcher"}], None, LIMITS),
    "cross-check": (["judge", "twin-1", "twin-2"], "judge",
                    [{"from": ["twin-1", "twin-2"], "to": "judge"}], None, LIMITS),
    "tree": (["lead", "squad-1", "squad-2", "worker-1", "worker-2", "worker-3", "worker-4"], "lead",
             [{"from": ["squad-1", "squad-2"], "to": "lead"}, {"from": ["worker-1", "worker-3"], "to": "squad-1"},
              {"from": ["worker-2", "worker-4"], "to": "squad-2"}],
             "daily every weekday 09:30 with squad-1 squad-2 -> lead", {"budget": 10, "launches": 24, "timeout": 900}),
}
# every template as `templates --json` says it: template -> (members, root)
LISTED = {**{one: shape[:2] for one, shape in SHAPES.items()}, **{one: shape[:2] for one, shape in FORMS.items()}}
# the values each template declares, as `templates --json` says them: template -> [(name, default)]
DAILY = "every weekday 09:30"
# the role keys a team preset gives, as `templates --json` and `team-started` say them: template -> {key: members}
ROLES = {**{one: {} for one in TEMPLATES},
         "supervisor-workers": {"supervisor": ["supervisor"], "workers": ["worker-1", "worker-2"]},
         "lead-reviewers": {"lead": ["lead"], "reviewers": ["reviewer-1", "reviewer-2"]},
         "council": {"experts": ["expert-1", "expert-2", "expert-3"]}, "cross-check": {"twins": ["twin-1", "twin-2"]},
         "triage": {"specialists": ["spec-a", "spec-b", "spec-c"]}}
PLACES = {**{one: {} for one in TEMPLATES},        # the same keys as each preset writes them: by place of its form
          "supervisor-workers": {"supervisor": ["{root}"], "workers": ["{others}"]},
          "lead-reviewers": {"lead": ["{root}"], "reviewers": ["{others}"]},
          "council": {"experts": ["{others}"]}, "cross-check": {"twins": ["{others}"]},
          "triage": {"specialists": ["{others}"]}}
VALUES = {**{one: [] for one in TEMPLATES}, "supervisor-workers": [("daily", DAILY)], "lead-reviewers": [("daily", DAILY)],
          "tree": [("squads", "2"), ("daily", DAILY)]}
HAND = "---\nagents: |\n  m agents/m\nroot: m\n---\nThe owner's own words.\n"


def intention_of(text: str) -> str:
    """-> the body of a TEAM.md, after its front matter; '' when it has none."""
    return text.split("---\n", 2)[-1].strip() if text.startswith("---\n") else ""


def names_all(intention: str, members: list[str]) -> bool:
    """-> whether the intention carries every member's id, as the templates mark one: `<id>`."""
    return all(f"`{one}`" in intention for one in members)


def keys_of(text: str) -> list[str]:
    """-> the keys the front matter of a TEAM.md writes, in its order."""
    front = text.split("---\n", 2)[1] if text.startswith("---\n") else ""
    return [line.split(":", 1)[0] for line in front.splitlines() if line and not line.startswith((" ", "#"))]


def declaration_of(house, team: str) -> dict:
    """-> `team declaration <team> --json` read: its one object, {} when it refuses or says no JSON."""
    played = house.call("team", "declaration", team, "--json")
    try:
        return json.loads(played.stdout.strip().splitlines()[-1]) if played.returncode == 0 else {}
    except (ValueError, IndexError):
        return {}


def templates_of(house) -> dict:
    """-> `team templates --json` read on a house: {template: its object}, {} when it refuses or says no JSON."""
    played = house.call("team", "templates", "--json")
    try:
        found = [json.loads(line) for line in played.stdout.splitlines() if line.strip()]
    except ValueError:
        return {}
    return ({one["template"]: one for one in found if isinstance(one, dict) and isinstance(one.get("template"), str)}
            if played.returncode == 0 else {})


def preset(name: str) -> str:
    """-> the name a package's team preset is said by: `teams/<name>`."""
    return f"{PRESET}/{name}"


def laid(place, files: dict) -> None:
    """The owner's files under a templates directory: {relative path: text}."""
    for relative, text in files.items():
        path = place / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def code_of(played) -> str:
    found = re.search(r"^pp-team: (\S+) --", played.stderr, re.M)
    return found.group(1) if found else ""


HOUSE_TEMPLATES = {
    "git/par-lot.md": "---\ndescription: one branch per batch\n---\nEach batch goes on its own branch.\n",
    "loose/one.md": "---\ndescription: the one template\n---\nOne.\n",
    "plans/shared.md": "---\ndescription: one shared plan\nrequires: plan\n---\nShared.\n",
    "teams/supervisor-workers.md": ("---\ndescription: the house's own\nform: star\nmembers: |\n  boss\n  hand-1\n"
                                    "  hand-2\n---\n{root} leads {others}.\n"),
    "teams/pair.md": ("---\ndescription: two members, the edge said\nmembers: |\n  a\n  b\nroot: a\n"
                      "reports: |\n  b -> a\n---\n{root} with {others}.\n"),
}


def started_from(h, team: str):
    """-> (the team's document as the start rendered it, `team start` played, the journal's `team-started`) -- ''
    when the start wrote no document."""
    started = h.call("team", "start", team, "--message", "go", "--no-tick", now="07:50")
    doc = h.teams / team / f"TEAM-{team}.md"
    text = doc.read_text(encoding="utf-8") if doc.is_file() else ""
    return text, started, next(iter(T.by_kind(h.events(team), "team-started")), {})


# A house's documents and presets: documents under `notes/`, `sources/`, `review/`, `guide/` -- each declaring the
# values its holes need, `review/law` mounted with a law `TM5`, `sources/read` served with `TM6` --, and three presets
# of a season under `seasons/`: `house-flow` (a line for all, one for `make`, one for the role its value `checker`
# names), `lean` (one document for all) and `split` (one for all, one per role, `guide/both` for both).
SHELF = {
    "notes/plain.md": "---\ndescription: plain notes\n---\nNotes of {team}.\n",
    "notes/dated.md": ("---\ndescription: dated notes\nvalues: |\n  day = monday -- the day the notes are read\n---\n"
                       "Notes of {team}, read on {day}.\n"),
    "sources/by-batch.md": ("---\ndescription: one branch per batch\nvalues: |\n  remote = origin -- where the code goes\n"
                            "  branch = batch-<lot> -- the branch pattern\n---\nPush to {remote} on {branch}, named after "
                            "<lot>.\n"),
    "sources/trunk.md": ("---\ndescription: the main branch\nvalues: |\n  remote = origin -- where the code goes\n---\n"
                         "Push to {remote} on main.\n"),
    "review/pair.md": ("---\ndescription: a peer reads every change\nvalues: |\n  lead -- who merges\nserve: |\n"
                       "  TEAM-{team}-members.md\n---\n{lead} reads it; write {{braces}}.\n"),
    "review/law.md": ("---\ndescription: the inspector's law, mounted\nmount: turn.begin\nconstraints.production: |\n"
                      "  TM5  zzinspectlaw.\ntools: |\n  pp-agent\n---\nzzinspectbody\n"),
    "sources/read.md": ("---\ndescription: the maker's reading, served\nconstraints.production: |\n  TM6  zzmakelaw.\n"
                        "tools: |\n  pp-agent\n---\nzzmakebody\n"),
    "guide/both.md": "---\ndescription: for both roles\n---\nzzbothbody\n",
    "seasons/house-flow.md": ("---\ndescription: the house's flow\nvalues: |\n  checker = inspect -- the role that "
                              "reviews\ndocuments: |\n  all notes/plain\n  make sources/by-batch\n  {checker} review/pair\n"
                              "---\n"),
    "seasons/lean.md": "---\ndescription: one document\ndocuments: |\n  all sources/by-batch\n---\n",
    "seasons/split.md": ("---\ndescription: one document for all, one per role, one for both\ndocuments: |\n"
                         "  all notes/plain\n  inspect review/law guide/both\n  make sources/read guide/both\n---\n"),
}
SEASON = "---\ntemplate: seasons/house-flow\nvalues: |\n  lead = alice\n---\n"


def digest(data: bytes) -> str:
    """-> the digest a journal keeps of a file: sha256, cut to 12 characters."""
    return hashlib.sha256(data).hexdigest()[:12]


def kept(h, team: str) -> tuple[dict, bytes]:
    """-> (the team's directory {relative path: bytes}, its journal's bytes): what a refusal must leave as it stands --
    every file at any depth, `roles/` included."""
    directory = h.teams / team
    files = ({str(one.relative_to(directory)): one.read_bytes() for one in sorted(directory.rglob("*")) if one.is_file()}
             if directory.is_dir() else {})
    journal = h.journal_of(team)
    return files, journal.read_bytes() if journal.is_file() else b""



# The package's examples: its documents, by directory, and its four presets of a season -- each line `(key, documents)`,
# a key the hole of a role the preset declares with the key itself as default (`ROLE_VALUES`); the values a season
# gives each preset, those it declares without a default.
EXAMPLE_DOCUMENTS = {
    "contribution": ["copied-files", "pushed-commits"],
    "integration": ["integration-branch"],
    "remote": ["bare-remote", "review-requests"],
    "review": ["read-commits", "read-files"],
    "sources": ["plan-branch", "run-clone", "shared-folders", "worktree-per-batch"],
}
EXAMPLE_PRESETS = {
    "clone-and-integration": [("all", ["seasons/clone-and-integration-summary", "sources/run-clone", "remote/bare-remote"]),
                              ("{contributors}", ["contribution/pushed-commits"]),
                              ("{reviewers}", ["review/read-commits"]),
                              ("{integrator}", ["integration/integration-branch"])],
    "files": [("all", ["seasons/files-summary", "sources/shared-folders"]),
              ("{contributors}", ["contribution/copied-files"]), ("{reviewers}", ["review/read-files"])],
    "plan-branch": [("all", ["seasons/plan-branch-summary", "sources/plan-branch", "remote/bare-remote"]),
                    ("{contributors}", ["contribution/pushed-commits"]), ("{reviewers}", ["review/read-commits"])],
    "worktree-and-requests": [("all", ["seasons/worktree-and-requests-summary", "sources/worktree-per-batch",
                                       "remote/review-requests"]),
                              ("{contributors}", ["contribution/pushed-commits"]),
                              ("{reviewers}", ["review/read-commits"])],
}
ROLE_VALUES = {"contributors": "contributors", "reviewers": "reviewers", "integrator": "integrator"}
EXAMPLE_GIVEN = {
    "clone-and-integration": {"repository": "/srv/code"},
    "files": {"source-folder": "/srv/in", "draft-folder": "/srv/drafts", "result-folder": "/srv/out"},
    "plan-branch": {"repository": "/srv/code"},
    "worktree-and-requests": {"repository": "/srv/code", "worktrees": "/srv/trees",
                              "open-request": "request open <branch>", "show-request": "request show <request>"},
}
