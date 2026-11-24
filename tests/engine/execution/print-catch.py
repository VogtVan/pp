"""Scenario `print-catch` -- what is no print is handed back, a print that misses stops the value, a
print that breaks its form is refused and the bound lifts its debt:
- (a) a text handed by the value call while prints are due and no value is asked comes back with the
  block and its DEVIATION: a `stray` on the trace, no repair, nothing captured, every print still due
- (b) a print call for a document nothing is due of comes back the same way
- (c) a print that misses stops the value: a proof piped while prints are due is not judged -- the block
  comes back, its DEVIATION naming the document of each production due, no repair counted, no `answer`
  of the proof; the principal's bare call over prints due comes back the same way, the run where it stood
- (d) a print that breaks its form is refused: an empty one, then one that misses the form of its step
  (`json`) -- the block and its DEVIATION at the return of the call, the print still due, no `answer`,
  no document replayed (no `repair`); at the bound (`work_repairs_allowed`) the debt is lifted, the
  trace says `print-waived`, the call answers the line of a print the bound lifted
  (`messages.PRINTED`, `waived`) -- never the line of a print taken --, and the proof that follows plays
- (e) a print that holds its form is captured as handed
- (f) the principal's message is never handed back: on a parked run where prints are still due -- the
  lines on `terminal` the held output says, LATE's two --, the message opens the passage and is traced
  `prompt`; the prints the passage over left due are lifted without a capture, one `print-waived` each;
  the principal's bare call there, once the held output is served, comes back with the block and its
  DEVIATION
"""
from __future__ import annotations

from conductor.core import messages
from conductor import Conductor, persistence, settings
from conductor.core import language
from tests.harness import cli, support, titled

run = support(__file__, "run")

PRINTS = getattr(persistence, "PRINTS", "prints")
MISSED = titled(language.DEVIATION)      # the line that opens a block's DEVIATION, its title the engine's
LEAF = "---\nname: {name}\nkind: proc\ndescription: a witness\nproc: |\n  INFER\n---\n{name} speaks\n"
TRIO = ("---\nname: TRIO\nkind: proc\ndescription: two callees' lines and its own, then a proof\n"
        "constraints.production: |\n  Z1  say it plainly\n"
        "proc: |\n  CALL ALPHA.md\n  CALL BRAVO.md\n  INFER\n  PROVE\n---\nTRIO speaks\n")
THREE = ("---\nname: THREE\nkind: proc\ndescription: three said steps of one document, then a proof\n"
         "constraints.production: |\n  Z1  say it plainly\n"
         "proc: |\n  WORK\n  INFER\n  INFER\n  PROVE\n---\nTHREE speaks\n")
FORMED = ("---\nname: FORMED\nkind: proc\ndescription: a said step of the form json, then a proof\noutput: json\n"
          "constraints.production: |\n  Z1  say it plainly\nproc: |\n  INFER\n  PROVE\n---\nFORMED speaks\n")
VALUE = '{"said": ["one", "two"],\n  "by": "the witness"}'
LATE = ("---\nname: LATE\nkind: proc\ndescription: two lines at the end of the turn\nattach: turn.end\n"
        "proc: |\n  INFER\n  INFER\n---\nLATE speaks\n")


def _agent(env, key: str, *words, stdin: str | None = None):
    """-> the AGENT's call on the run: under the run its launcher names."""
    return cli(env.engine, key, *words, cwd=env.root, stdin=stdin, env=run.agent(key))


def _principal(env, key: str, *words):
    """-> the principal's call on the run."""
    return cli(env.engine, key, *words, cwd=env.root)


def _printed(env, key: str, name: str, text: str):
    return _agent(env, key, "-print", name, "-", stdin=text + "\n")


def _due(env, key: str) -> list:
    return [one.get("document") for one in run.slot(env, key).get(PRINTS) or [] if isinstance(one, dict)]


def _deviation(text: str) -> str:
    """-> the DEVIATION section of a rendered block, "" when it carries none."""
    if MISSED not in text.splitlines():
        return ""
    return text.split(MISSED + "\n", 1)[1].split("\n\n", 1)[0]


def _answers(env, key: str, channel: str | None = None) -> list:
    return [one for one in run.trace(env, key) if one.get("kind") == "answer"
            and (channel is None or one.get("channel") == channel)]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("print-catch")
    for name in ("ALPHA", "BRAVO"):
        env.write(f"procs/{name}.md", LEAF.format(name=name))
    for name, text in (("TRIO", TRIO), ("THREE", THREE), ("FORMED", FORMED)):
        env.write(f"procs/{name}.md", text)
    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 60000\n"
                             "instructions_fusion: max\n---\n")
    names = ["ALPHA", "BRAVO", "TRIO"]

    # --- (a) a text handed by the value call, prints due, no value asked --------------------------------
    key, _ = run.opened(env, "TRIO.md")
    strays = run.kinds(env, key).count("stray")
    handed = _agent(env, key, "a production handed as a value")
    kinds = run.kinds(env, key)
    if (key and _due(env, key) == names and handed.returncode == 0 and _deviation(handed.stdout)
            and kinds.count("stray") == strays + 1 and "repair" not in kinds
            and not _answers(env, key, language.TERMINAL)):
        held("(a) a production handed as a value comes back", f"run {key}: the block and its DEVIATION, one "
             "`stray`, no repair, nothing captured, the three prints still due")
    else:
        failures.append(f"  ✗ (a) handed as a value        rc={handed.returncode} due={_due(env, key)} "
                        f"deviation={bool(_deviation(handed.stdout))} stray={kinds.count('stray')}/{strays} "
                        f"repair={'repair' in kinds} {handed.stdout[-200:]!r}")

    # --- (b) a print for a document nothing is due of ---------------------------------------------------
    strays = kinds.count("stray")
    nowhere = _printed(env, key, "NOBODY", "a print of nothing due")
    kinds = run.kinds(env, key)
    if (_due(env, key) == names and nowhere.returncode == 0 and _deviation(nowhere.stdout)
            and kinds.count("stray") == strays + 1 and "repair" not in kinds
            and not _answers(env, key, language.TERMINAL)):
        held("(b) a print of nothing due comes back", "the block and its DEVIATION, one `stray`, no repair, "
             "nothing captured, the three prints still due")
    else:
        failures.append(f"  ✗ (b) a print of nothing due   rc={nowhere.returncode} {nowhere.stderr[-120:]!r} "
                        f"due={_due(env, key)} deviation={bool(_deviation(nowhere.stdout))} "
                        f"stray={kinds.count('stray')}/{strays}")

    # --- (c) a print that misses stops the value, the agent's then the principal's ------------------------
    key, first = run.opened(env, "THREE.md")
    proved = _agent(env, key, "-", stdin=run.proof_of(first.stdout))
    kinds = run.kinds(env, key)
    key_p, first_p = run.opened(env, "THREE.md")
    before = run.slot(env, key_p).get("frames")
    advanced = _principal(env, key_p)
    kinds_p = run.kinds(env, key_p)
    if (key and proved.returncode == 0 and "THREE" in _deviation(proved.stdout)
            and "repair" not in kinds and "repair-in-place" not in kinds and not _answers(env, key)
            and _due(env, key) == ["THREE"] * 3
            and key_p and advanced.returncode == 0 and "THREE" in _deviation(advanced.stdout)
            and "repair" not in kinds_p and _due(env, key_p) == ["THREE"] * 3
            and run.slot(env, key_p).get("frames") == before):
        held("(c) a print that misses stops the value", f"run {key}: the proof piped over three prints due is "
             "not judged -- the block and a DEVIATION naming the document, no repair, no answer traced; the "
             f"principal's bare call (run {key_p}) comes back the same way, the frames where they stood")
    else:
        failures.append(f"  ✗ (c) a print that misses      proved={proved.returncode} {_deviation(proved.stdout)[:80]!r} "
                        f"repair={'repair' in kinds} answers={len(_answers(env, key))} due={_due(env, key)} "
                        f"principal={advanced.returncode} {_deviation(advanced.stdout)[:80]!r} "
                        f"repair={'repair' in kinds_p} moved={run.slot(env, key_p).get('frames') != before}")

    # --- (d) a print that breaks its form, up to the bound ------------------------------------------------
    bound = settings.REPAIRS_ALLOWED
    key, first = run.opened(env, "FORMED.md")
    tries = [_printed(env, key, "FORMED", "" if n == 0 else "{not one json value") for n in range(bound)]
    refused = [bool(_deviation(one.stdout)) for one in tries[:-1]]
    kinds, left = run.kinds(env, key), _due(env, key)
    proved = _agent(env, key, "-", stdin=run.proof_of(first.stdout))
    waived_line = messages.printed("waived")
    if (key and left == [] and all(one.returncode == 0 for one in tries) and all(refused)
            and kinds.count("print-waived") == 1 and "repair" not in kinds
            and tries[-1].stdout.strip() == waived_line
            and not _answers(env, key, language.TERMINAL)
            and proved.returncode == 0 and "repair" not in run.kinds(env, key)
            and len(_answers(env, key)) == 1):
        held("(d) a print that breaks its form is refused, the bound lifts its debt", f"run {key}: an empty "
             f"print then {bound - 1} that miss the form `json` -- each before the last comes back with its "
             "DEVIATION, no document replayed, nothing captured; at the bound the trace says `print-waived`, "
             "the call answers the waived line of messages.PRINTED, nothing is due, and the proof plays")
    else:
        failures.append(f"  ✗ (d) the form and the bound   rc={[one.returncode for one in tries]} refused={refused} "
                        f"due={left} waived={kinds.count('print-waived')} repair={'repair' in kinds} "
                        f"captured={len(_answers(env, key, language.TERMINAL))} proved={proved.returncode} "
                        f"last={tries[-1].stdout.strip()[:80]!r} "
                        f"{tries[0].stderr[-120:]!r}")

    # --- (e) a print that holds its form is captured as handed ---------------------------------------------
    key, first = run.opened(env, "FORMED.md")
    missed = _printed(env, key, "FORMED", "{not one json value")
    still = _due(env, key)
    formed = _printed(env, key, "FORMED", VALUE)
    captured = [one.get("given") for one in _answers(env, key, language.TERMINAL)]
    if (key and bool(_deviation(missed.stdout)) and still == ["FORMED"] and formed.returncode == 0
            and not _deviation(formed.stdout) and captured == [VALUE] and _due(env, key) == []
            and "print-waived" not in run.kinds(env, key)):
        held("(e) a print that holds its form is captured", f"run {key}: refused once, still due; the json "
             "value of two lines then captured as handed, byte for byte, nothing due left")
    else:
        failures.append(f"  ✗ (e) a formed print           missed={bool(_deviation(missed.stdout))} still={still} "
                        f"formed={formed.returncode} captured={captured!r} due={_due(env, key)}")

    # --- (f) the principal's message on a parked run where a print is due --------------------------------
    late = bench.env("print-parked")
    late.write("procs/LATE.md", LATE)
    late.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 60000\n"
                              "instructions_fusion: max\n---\n")
    key, first = run.opened(late)
    ended = _printed(late, key, "TURN", "the work of the turn")       # the last print due: the run moves to its end
    parked = _due(late, key)
    served = run.said(_principal(late, key).stdout)                      # the principal's bare call serves what is held
    bare = _principal(late, key)
    after_bare = (_due(late, key), run.kinds(late, key).count("prompt"))
    message = "the principal's next message"
    opened = _principal(late, key, message)
    events = run.trace(late, key)
    prompts = [one.get("text") for one in events if one.get("kind") == "prompt"]
    waived = [one.get("document") for one in events if one.get("kind") == "print-waived"]
    lines = served.count("LATE")                                      # LATE's lines the held output says
    if (key and ended.returncode == 0 and lines and parked == served == ["LATE"] * lines
            and run.slot(late, key) and bare.returncode == 0
            and _deviation(bare.stdout) and after_bare == (parked, 0)
            and opened.returncode == 0 and not _deviation(opened.stdout) and prompts == [message]
            and waived == parked and "LATE" not in _due(late, key)
            and not _answers(late, key, language.TERMINAL)[1:]):
        held("(f) the principal's message is never handed back", f"run {key}: parked with LATE's {lines} lines "
             "still due, as the held output says them -- a bare call comes back with its DEVIATION, the prints "
             "still due, no `prompt`; the message opens the passage, traced `prompt`, the debt lifted by one "
             "`print-waived` per line, nothing captured for them")
    else:
        failures.append(f"  ✗ (f) the message on a parked run  ended={ended.returncode} {ended.stdout[-160:]!r} "
                        f"parked={parked} served={served} bare={(bare.returncode, bool(_deviation(bare.stdout)))} {after_bare} "
                        f"opened={(opened.returncode, _deviation(opened.stdout)[:60])} prompts={prompts} "
                        f"waived={waived} due={_due(late, key)}")
    return 0
