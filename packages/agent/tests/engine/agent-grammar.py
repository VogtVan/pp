"""Scenario `agent-grammar` -- the grammar of `pp agent`: what a verb refuses before it acts and what it says of a
house where nothing happened yet, on one house, no launch played:
- an empty house: `list` says no agent stands yet; `responses`, `messages` and `workdirs` say nothing is on
  record -- exit 0, one line each; `calibrate` says no line; an agent just born shows no run at `status`
- `add` refuses a path it cannot give birth at, `agent-path-invalid`, nothing born: a file stands on the path;
  the path lies under an instance that carries a machine of its own
- a call a verb cannot read is refused with the usage, exit 2: a word missing, a word too many, a flag unknown
- a value a verb cannot read is refused in its own words, exit 2, the refusal opening on no code: a timeout and
  a count that are no numbers, a count under 1, a message given twice, `--new` beside `--run`, `--base` without
  `--work`
- a name a verb does not know is refused by its code: `run-unknown` (`exchanges`, `stats`, a vector verified
  without a key, a run resumed), `family-foreign` (a vector of another family), `agent-path-invalid` (the house
  removed by its own hand), `message-file-missing`, `result-missing`, `door-on-resume` (a door asked on a resume)
- the provider of a launch is read on the house's wiring: a dry run without `--provider` composes for the one
  adapter wired, its message read on stdin under `--message-file -`; `provider-ambiguous` with two wired,
  `provider-missing` with none
- what a call asks is read flag by flag (`Asked.of`): a value as typed, a flag without a value true, a flag given
  several times kept in its order, what no flag gives left unsaid; two flags that exclude each other stop the
  reading, exit 2, never the usage; the policy the flags give names its keys in the writer's order
No case launches anything: the house's records hold no line at the end, the agent no run.
"""
from __future__ import annotations

import contextlib
import io
import re
import shutil

from conductor import install
from tests.harness import INSTANCE, PRODUCT_ENGINE, support

A = support(__file__, "agent")
SKILL = A.skill()

# the calls no verb can read: each is refused with the usage
UNREAD = [("add",), ("add", "agents/n", "--kind", "member"), ("import", "agents/n"), ("start",),
          ("wait", "agents/ag1", "k", "more"), ("result", "agents/ag1", "k", "more"),
          ("workdirs", "agents/ag1", "more"), ("prune", "agents/ag1", "k", "more"), ("flow", "agents/ag1"),
          ("verify", "more"), ("remove", "agents/ag1", "more"), ("responses", "agents/ag1", "more"),
          ("list", "more"), ("providers", "more"), ("status", "agents/ag1", "more"), ("name", "agents/ag1"),
          ("exchanges", "agents/ag1"), ("stats", "agents/ag1"), ("calibrate", "--nope"),
          ("run", "agents/ag1", "--dry-run", "--message", "x", "--nope"),
          ("run", "agents/ag1", "--dry-run", "--message")]
# the values no verb can read: each is refused in the verb's own words
VALUES = [("wait", "agents/ag1", "k", "--timeout", "soon"), ("responses", "agents/ag1", "--last", "many"),
          ("responses", "agents/ag1", "--last", "0"),
          ("run", "agents/ag1", "--dry-run", "--message", "x", "--message-file", "y"),
          ("run", "agents/ag1", "--dry-run", "--message", "x", "--new", "--run", "k"),
          ("run", "agents/ag1", "--dry-run", "--message", "x", "--base", "main")]


CODE = re.compile(r"[a-z]+(-[a-z]+)+")      # what a refusal's code looks like: `run-unknown`


def coded(played) -> str:
    """-> the code a refusal opens on, the first word the script says on stderr; the exit code of a call that
    did not refuse."""
    said = played.stderr.strip().removeprefix("pp-agent: ")
    return said.split(" ", 1)[0] if played.returncode == 2 else f"rc {played.returncode}"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench, born=False)
    usage = f"pp-agent: {SKILL.USAGE}"

    # --- an empty house: every reading says there is nothing yet -------------------------------------------
    empty = {verb: h.call("agent", verb) for verb in ("list", "responses", "messages", "workdirs")}
    unmeasured = h.call("agent", "calibrate")
    if (all(one.returncode == 0 and len(one.stdout.splitlines()) == 1 and not one.stderr for one in empty.values())
            and unmeasured.returncode == 0 and not unmeasured.stdout):
        held("an empty house says there is nothing yet", "list, responses, messages and workdirs: exit 0, one line "
             "each, before any agent is born; calibrate: exit 0, no line")
    else:
        failures.append(f"  ✗ an empty house              "
                        f"{ {verb: (one.returncode, one.stdout[:80], one.stderr[-80:]) for verb, one in empty.items()} } "
                        f"calibrate={unmeasured.returncode} {unmeasured.stdout[:80]!r}")

    # --- add refuses a path it cannot give birth at ---------------------------------------------------------
    (h.ws / "taken").write_text("a file, where a directory is wanted\n", encoding="utf-8")
    install.install(PRODUCT_ENGINE, h.ws / "own" / INSTANCE, [])        # an instance that carries its own machine
    births = {"taken/ag": h.call("agent", "add", "taken/ag"), "own/sub": h.call("agent", "add", "own/sub")}
    born = h.call("agent", "add", "agents/ag1")
    bare = (h.call("agent", "status", "agents/ag1"), h.call("agent", "status", "agents/ag1", "--json"))
    if ({path: coded(one) for path, one in births.items()} == {"taken/ag": "agent-path-invalid",
                                                                "own/sub": "agent-path-invalid"}
            and (h.ws / "taken").is_file() and not (h.ws / "own" / "sub").exists()
            and born.returncode == 0 and h.agent_meta.is_dir()
            and [one.returncode for one in bare] == [0, 0] and len(bare[1].stdout.splitlines()) == 1
            and not [line for line in bare[0].stdout.splitlines() if line.startswith("run ")]):
        held("add refuses a path it cannot give birth at", "a file on the path, a path under an instance with a "
             "machine of its own: agent-path-invalid, nothing born; agents/ag1 born has no run at status, and "
             "status --json says its one object, the agent's")
    else:
        failures.append(f"  ✗ add and its paths           { {path: coded(one) for path, one in births.items()} } "
                        f"born={born.returncode} {born.stderr[-160:]!r} "
                        f"status={[(one.returncode, one.stdout[:120]) for one in bare]}")

    # --- a call a verb cannot read is refused with the usage ------------------------------------------------
    unread = {call: h.call("agent", *call) for call in UNREAD}
    strays = {" ".join(call): (one.returncode, one.stderr.strip()[:60]) for call, one in unread.items()
              if one.returncode != 2 or one.stderr.strip() != usage or one.stdout}
    if not strays:
        held("a call a verb cannot read is refused with the usage", f"{len(UNREAD)} calls over 19 verbs -- a word "
             "missing, a word too many, a flag unknown: exit 2, the usage on stderr, nothing on stdout")
    else:
        failures.append(f"  ✗ the usage                   {strays}")

    # --- a value a verb cannot read is refused in its own words ----------------------------------------------
    values = {call: h.call("agent", *call) for call in VALUES}
    strays = {" ".join(call): (one.returncode, one.stderr.strip()[:60]) for call, one in values.items()
              if one.returncode != 2 or not one.stderr.strip() or one.stderr.strip() == usage or one.stdout
              or CODE.fullmatch(coded(one))}
    if not strays:
        held("a value a verb cannot read is refused in its words", "a timeout and a count that are no numbers, a "
             "count under 1, a message given twice, --new beside --run, --base without --work: exit 2, never "
             "the usage, never a refusal's code")
    else:
        failures.append(f"  ✗ the values                  {strays}")

    # --- what a call asks, read flag by flag -----------------------------------------------------------------
    read = SKILL.Asked.of(["--message", "x", "--max-budget-usd", "1.5", "--dry-run", "--package", "a=on", "--package",
                           "b=off", "--vector", "f:1", "--on-end", "true", "--run", "k"])
    fields = (read.message, read.max_budget_usd, read.dry_run, read.package, read.vector, read.on_end, read.run,
              read.new, read.model, read.conduct)
    policy = SKILL.asked_policy(SKILL.Asked.of(["--effort", "low", "--model", "m", "--max-budget-usd", "2"])).json()
    excluded = {}
    for what, words in {"a message given twice": ["--message", "x", "--message-file", "y"],
                        "--new beside --run": ["--new", "--run", "k"], "--base without --work": ["--base", "main"]}.items():
        said = io.StringIO()
        try:
            with contextlib.redirect_stderr(said):
                SKILL.asked_of(words)
            excluded[what] = "read"
        except SystemExit as stop:
            excluded[what] = (stop.code, said.getvalue().strip() == usage)
    if (fields == ("x", "1.5", True, ("a=on", "b=off"), ("f:1",), "true", "k", False, None, None)
            and list(policy.items()) == [("model", "m"), ("max_budget_usd", "2"), ("effort", "low")]
            and excluded == {what: (2, False) for what in excluded}):
        held("what a call asks is read flag by flag", "Asked.of: the values as typed, --dry-run true, --package twice "
             "kept in its order, no --new and no --model left unsaid, conduct said by no flag; a message given twice, "
             "--new beside --run, --base without --work: exit 2, never the usage; the policy of the flags names "
             "model, max_budget_usd, effort in that order")
    else:
        failures.append(f"  ✗ what a call asks            fields={fields} policy={list(policy.items())} "
                        f"excluded={excluded}")

    # --- a name a verb does not know is refused by its code --------------------------------------------------
    names = {"exchanges": h.call("agent", "exchanges", "agents/ag1", "zzzzzz"),
             "stats": h.call("agent", "stats", "agents/ag1", "zzzzzz"),
             "verify a foreign family": h.call("agent", "verify", stdin="plan:x"),
             "verify without a key": h.call("agent", "verify", stdin=f"{SKILL.FAMILY}:nokey"),
             "remove the house": h.call("agent", "remove", "."),
             "run --message-file": h.call("agent", "run", "agents/ag1", "--dry-run", "--message-file",
                                          str(bench.temp() / "absent")),
             "result": h.call("agent", "result", "agents/ag1", "zzzzzz"),
             "run --run": h.call("agent", "run", "agents/ag1", "--dry-run", "--run", "zzzzzz", "--message", "x"),
             "chat --run --door": h.call("agent", "chat", "agents/ag1", "--run", "zzzzzz", "--door", "D.md", stdin="")}
    codes = {what: coded(one) for what, one in names.items()}
    if codes == {"exchanges": "run-unknown", "stats": "run-unknown", "verify a foreign family": "family-foreign",
                 "verify without a key": "run-unknown", "remove the house": "agent-path-invalid",
                 "run --message-file": "message-file-missing", "result": "result-missing",
                 "run --run": "run-unknown", "chat --run --door": "door-on-resume"}:
        held("a name a verb does not know is refused by its code", f"{codes}")
    else:
        failures.append(f"  ✗ the names                   {codes} "
                        f"{ {what: one.stderr.strip()[-100:] for what, one in names.items()} }")

    # --- the provider of a launch, read on the house's wiring -------------------------------------------------
    dry = ("agent", "run", "agents/ag1", "--message", "x", "--dry-run")
    lone = h.call(*dry)                                    # the one adapter the house is wired with
    piped = h.call("agent", "run", "agents/ag1", "--dry-run", "--message-file", "-", stdin="said on stdin\n")
    (h.ws / ".codex").mkdir()                              # a second adapter's artifact
    two = h.call(*dry)
    shutil.rmtree(h.ws / ".codex")
    (h.ws / ".claude").rename(h.ws / ".claude-away")       # no adapter's artifact left
    none = h.call(*dry)
    (h.ws / ".claude-away").rename(h.ws / ".claude")
    if (lone.returncode == 0 and lone.stdout.strip() and piped.returncode == 0 and "said on stdin" in piped.stdout
            and coded(two) == "provider-ambiguous"
            and coded(none) == "provider-missing" and h.counted() == (0, 0, 0) and h.keys() == []):
        held("the provider is read on the house's wiring", "a dry run without --provider composes for the one "
             "adapter wired, its message read on stdin under --message-file -; two wired: provider-ambiguous; "
             "none: provider-missing; the records hold no line and "
             "the agent no run after every case")
    else:
        failures.append(f"  ✗ the provider                lone={lone.returncode} {lone.stderr[-120:]!r} "
                        f"piped={piped.returncode} {piped.stderr[-120:]!r} "
                        f"two={coded(two)} none={coded(none)} counted={h.counted()} keys={h.keys()}")
    return 0
