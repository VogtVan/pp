"""Scenario `tags` -- the pattern `context/tags`, played from its demonstration:
- `@<Doc>.<field>` in a law's text takes that field's value in that document's front matter: a
  document of the instance, the MEMBER and SETTINGS; a mounted document's law reads its tag the same
- a field a document lacks, or a document no name answers, refuses `tag-unresolved`, the member's
  absent field too
- a SETTINGS key left to its default reads its default in a law, as a guard reads it
The member, SETTINGS and the trees are written at the test's time.
"""
from __future__ import annotations

from conductor import reading, settings
from tests.harness import codes, demonstrated, demos, law, plant

DRAWER, PATTERN = "context", "tags"
DEMO = demos(DRAWER, PATTERN)
DEMOS = ("ABSENT.md", "BRIEF.md", "CITED.md", "DEFAULTED.md", "DESK.md", "NOTED.md", "UNKNOWN.md")
NAME = "Sextant"                        # what `@MEMBER.name` reads
CHARACTER = "curt, dry wit"             # what `@MEMBER.character` reads
BODY_SERVE = "once"                     # what `@SETTINGS.proc_body_serve` reads
DEFAULTED = "work_repairs_allowed"      # the SETTINGS key DEFAULTED.md cites, left to its default


def _said(name: str, code: str, values: dict[str, str]) -> str:
    """-> the law `code` of the demonstration `name` without its code, each tag replaced by its value."""
    text = law(DRAWER, PATTERN, name, code).split(None, 1)[1]
    for tag, value in values.items():
        text = text.replace(tag, value)
    return text


def _texts(block) -> dict[str, str]:
    return {one.code: one.text for one in block.constraints} if block is not None else {}


def _opened(env, name: str):
    runner = env.conductor("t")
    runner.forget()
    return runner.start(env.made / "procs" / name)


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    env = bench.env("tags", bare=True)
    plant(env, DRAWER, PATTERN, DEMOS)
    env.write("SETTINGS.md", f"---\nname: SETTINGS\nkind: doc\nproc_body_serve: {BODY_SERVE}\n---\n")
    env.write_member(f"character: {CHARACTER}\n", name=NAME)
    brief = reading.read(DEMO / "BRIEF.md").front
    values = {"@BRIEF.mode": str(brief["mode"]), "@BRIEF.owner": str(brief["owner"]), "@MEMBER.name": NAME,
              "@MEMBER.character": CHARACTER, "@SETTINGS.proc_body_serve": BODY_SERVE}

    # --- a law's tags read the front matter of a document, the member and SETTINGS -----------------
    cited = _texts(_opened(env, "CITED.md"))
    owed = {code: _said("CITED.md", code, values) for code in ("TG1", "TG2", "TG3")}
    if cited and all(cited.get(code) == text for code, text in owed.items()) and "@" not in "".join(cited.values()):
        held("a tag reads another document's front matter", "CITED's laws: BRIEF's mode, the member's name "
             "and character, SETTINGS' proc_body_serve, each in place of its tag")
    else:
        failures.append(f"  ✗ the tags                    {cited} -- owed {owed}")

    # --- a mounted document's law reads as the engine plays it ---------------------------------------
    opener = env.conductor("m")
    opener.forget()
    opener.start(env.made / "procs" / "DESK.md")
    env.conductor("m").mount([{"doc": "NOTED.md"}])
    mounted = _texts(env.conductor("m").peek())
    owed_mount = _said("NOTED.md", "TG4", values)
    if "TG4" in codes(env.conductor("m").peek()) and mounted.get("TG4") == owed_mount:
        held("a mounted document's law reads its tag", "NOTED mounted on DESK: TG4 in force, BRIEF's owner "
             "in place of its tag -- a law reads its tags wherever it is in force")
    else:
        failures.append(f"  ✗ the mounted law             {mounted} -- owed {owed_mount!r}")
    env.conductor("m").forget()

    # --- what a tag cannot read refuses ---------------------------------------------------------------
    expect("tag-unresolved", lambda: _opened(env, "ABSENT.md"))
    expect("tag-unresolved", lambda: _opened(env, "UNKNOWN.md"))
    env.write_member("", name=NAME)
    expect("tag-unresolved", lambda: _opened(env, "CITED.md"))
    env.write_member(f"character: {CHARACTER}\n", name=NAME)

    # --- a SETTINGS key left to its default ------------------------------------------------------------
    default = settings.default_of(env.made, DEFAULTED)
    defaulted = _texts(_opened(env, "DEFAULTED.md"))
    owed_default = _said("DEFAULTED.md", "TG5", {f"@SETTINGS.{DEFAULTED}": default})
    if default and defaulted.get("TG5") == owed_default:
        held("a key left to its default", f"`@SETTINGS.{DEFAULTED}` in a law reads the default ({default}), "
             "as a guard reads it")
    else:
        failures.append(f"  ✗ the default                 {defaulted} -- owed {owed_default!r}")
    env.conductor("t").forget()
    return 0
