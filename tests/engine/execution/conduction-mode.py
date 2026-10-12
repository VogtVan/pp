"""Scenario `conduction-mode` -- 8 case(s) (plan core, batch le-canal-du-run, 2026-10-05): a run
is conducted by the LLM (today) or by its principal, set at `-new` under
`PP_CONDUCTED_BY_PRINCIPAL=true`; in the principal's mode no ending that moves the run on
carries a command.
- (a) without the variable, or under `false`: the first outputs of two throwaways are the same
  to the byte, and neither the slot nor the trace says a mode
- (b) under `true`: `conducted_by: principal` at the slot and on the trace's `new` line
- (c) the endings: CONTINUE, FINAL and an unconsumed FREE step render their note and no
  command; a proof, a choice and a production the tool takes keep theirs
- (d) the chunks: at a cap equal to the floor of the principal's, one block past it cuts into the
  same chunks in both modes; in the
  principal's, each chunk before the last shows no command and says the next prompt
- (e) the recovery texts: the soft catch, a cut view, a renewed run, a bounced call -- none
  tells the agent to call pp in the principal's mode; today's texts in the LLM's
- (f) an upgrade's renewal keeps the mode: the mark carries it, the reopened run has it
- (g) any other value refuses `conducted-by-invalid` and leaves no slot
- (h) `-hook` serves the pending block of a run conducted by its principal
"""
from __future__ import annotations

import json
import os
import re

from conductor import persistence, render, rendering, settings
from tests.harness import cli

VARIABLE = "PP_CONDUCTED_BY_PRINCIPAL"
KEY = re.compile(r"run ([0-9a-f]{6})")
WORKS = "---\nname: WORKS\nkind: proc\ndescription: a witness\nproc: |\n  WORK\n  WORK\n  FINAL\n---\nwork\n"
PROVER = ("---\nname: PROVER\nkind: proc\ndescription: a witness\nconstraints.production: |\n"
          "  Z1  say it plainly\nproc: |\n  WORK\n---\nprove\n")
PICKER = ("---\nname: PICKER\nkind: proc\ndescription: a witness\noutput: json\nproc: |\n"
          "  INFER\n  PICK verdict\n---\nelect\n")
LONGRUN = "---\nname: LONGRUN\nkind: proc\ndescription: a witness\nproc: |\n  SERVE LONG.md\n  WORK\n---\nread\n"
CAP = "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 2000\n---\n"
AT_FLOOR = f"---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {settings.PRINCIPAL_CAP}\n---\n"
PAST = ("---\nname: LONG\nkind: doc\n---\n\n"   # past the floor of a principal's cap: it cuts whatever the setting
        + "long line of matter\n" * (2 * settings.PRINCIPAL_CAP // 20) + "\n")


def _under(value: str | None, call):
    """-> what `call` returns with the mode variable set to `value` (None: absent) in THIS process."""
    spot = os.environ.get(VARIABLE)
    if value is None:
        os.environ.pop(VARIABLE, None)
    else:
        os.environ[VARIABLE] = value
    try:
        return call()
    finally:
        if spot is None:
            os.environ.pop(VARIABLE, None)
        else:
            os.environ[VARIABLE] = spot


def _slot(env, key: str) -> dict:
    path = persistence.slot_of(env.made, key)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _new_line(env, key: str) -> dict:
    log = _slot(env, key).get("log") or ""
    trace = env.made / persistence.DIRECTORY / log
    if not log or not trace.is_file():
        return {}
    lines = [json.loads(one) for one in trace.read_text(encoding="utf-8").splitlines() if one.strip()]
    return next((one for one in lines if one.get("kind") == "new"), {})


def _closing(text: str) -> list[str]:
    """-> the lines from the closing's arrow to the end."""
    lines = text.splitlines()
    at = max((i for i, one in enumerate(lines) if one.startswith("▶ ")), default=len(lines))
    return lines[at:]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- (a) the LLM's mode is today's, to the byte -------------------------------------------------
    plain, falsy = bench.env("mode-plain"), bench.env("mode-false")
    first = cli(plain.engine, "-new", cwd=plain.root)
    second = cli(falsy.engine, "-new", cwd=falsy.root, env={VARIABLE: "false"})
    keys = [KEY.search(one.stdout).group(1) if KEY.search(one.stdout) else "?" for one in (first, second)]
    lines = [one.stdout.replace(key, "KEY").replace(str(env.root), "WS").splitlines()[1:]
             for one, key, env in ((first, keys[0], plain), (second, keys[1], falsy))]
    said = [("conducted_by" in _slot(env, key)) or ("conducted_by" in _new_line(env, key))
            for env, key in ((plain, keys[0]), (falsy, keys[1]))]
    if first.returncode == 0 and second.returncode == 0 and lines[0] and lines[0] == lines[1] and not any(said):
        held("(a) the LLM's mode is today's", f"{len(lines[0])} lines identical without the variable "
             "and under `false`; no mode at the slot nor on the `new` line")
    else:
        drift = next((i for i, (a, b) in enumerate(zip(*lines)) if a != b), None)
        failures.append(f"  ✗ (a) the LLM's mode            rc={first.returncode}/{second.returncode} "
                        f"drift={drift} said={said} {second.stderr[-200:]!r}")

    # --- (b) the principal's mode at the slot and the trace ------------------------------------------
    led = bench.env("mode-principal")
    opened = cli(led.engine, "-new", cwd=led.root, env={VARIABLE: "true"})
    key = KEY.search(opened.stdout).group(1) if KEY.search(opened.stdout) else ""
    if (opened.returncode == 0 and key and _slot(led, key).get("conducted_by") == "principal"
            and _new_line(led, key).get("conducted_by") == "principal"):
        held("(b) the mode is the run's", f"run {key}: `conducted_by: principal` at its slot and on its "
             "`new` line")
    else:
        failures.append(f"  ✗ (b) the mode at the run       rc={opened.returncode} key={key!r} "
                        f"slot={_slot(led, key).get('conducted_by') if key else None} {opened.stderr[-200:]!r}")

    # --- (c) the endings ----------------------------------------------------------------------------
    ends = bench.env("mode-ends")
    works, prover, picker = (ends.write(f"{name}.md", text)
                             for name, text in (("WORKS", WORKS), ("PROVER", PROVER), ("PICKER", PICKER)))

    def opened_on(path, value="true"):
        ends.conductor().forget()
        conductor = ends.conductor()
        block = _under(value, lambda: conductor.start(path))
        return conductor.run_id, block

    run, working = opened_on(works)
    finishing = ends.conductor(run).submit("")
    run_v, proving = opened_on(prover)
    if proving.output != "proof":
        proving = ends.conductor(run_v).submit("")
    run_p, inferring = opened_on(picker)
    picking = ends.conductor(run_p).submit('["a", "b"]')
    texts = {name: render(one) for name, one in (("work", working), ("final", finishing),
                                                  ("prove", proving), ("infer", inferring),
                                                  ("pick", picking))}
    tails = {name: "\n".join(_closing(text)) for name, text in texts.items()}
    bare = [name for name in ("work", "final") if "./pp" in tails[name]]
    kept = [name for name in ("prove", "infer", "pick") if "./pp" not in tails[name]]
    noted = ("end your message" in tails["work"] and "your next message IS the response" in tails["final"])
    _, llm_work = opened_on(works, None)
    if not bare and not kept and noted and "./pp" in "\n".join(_closing(render(llm_work))):
        held("(c) no ending that moves the run carries a command",
             "CONTINUE and FINAL render their note alone; the proof, the choice and the production the "
             "tool takes keep `./pp <key>`; the LLM's CONTINUE keeps its command")
    else:
        failures.append(f"  ✗ (c) the endings              commanded={bare} uncommanded={kept} noted={noted} "
                        f"{tails['work']!r} {tails['final']!r}")

    # --- (d) the chunks ----------------------------------------------------------------------------
    long = bench.env("mode-chunks")
    long.write("SETTINGS.md", AT_FLOOR)   # one cap in both modes: the floor itself
    long.write("LONG.md", PAST)
    longrun = long.write("LONGRUN.md", LONGRUN)

    def read_whole(value):
        # the host carries the standing orders (`PP_MARBLE`): each mode has its own marble,
        # and the block compared in both modes is the reading alone
        long.conductor().forget()
        conductor = long.conductor()
        os.environ["PP_MARBLE"] = "1"
        try:
            block = _under(value, lambda: conductor.start(longrun))
        finally:
            os.environ.pop("PP_MARBLE", None)
        run_key = conductor.run_id
        chunks = [long.conductor(run_key).rendered(block)]
        while long.conductor(run_key).pending() and len(chunks) < 100:
            chunks.append(long.conductor(run_key).next_chunk())
        return chunks

    by_llm, by_principal = read_whole(None), read_whole("true")

    def matter(chunks):
        return [one.split("\n▶ CONTINUE")[0].split("\n", 1)[-1] for one in chunks[:-1]]

    middles = by_principal[:-1]
    if (len(by_llm) > 1 and len(by_llm) == len(by_principal) and matter(by_llm) == matter(by_principal)
            and all("./pp" not in "\n".join(_closing(one)) and "next prompt" in one for one in middles)
            and all("the bare call alone" in one for one in by_llm[:-1])):
        held("(d) the same chunks, a new injunction",
             f"{len(by_llm)} chunks in both modes, the same matter; the principal's {len(middles)} "
             "intermediate chunks show no command and say the next prompt; the reading takes "
             f"{len(by_llm)} calls either way")
    else:
        failures.append(f"  ✗ (d) the chunks               llm={len(by_llm)} principal={len(by_principal)} "
                        f"{middles[-1][-260:] if middles else ''!r}")

    # --- (e) the recovery texts --------------------------------------------------------------------
    catch_run, _ = opened_on(works)
    caught = render(ends.conductor(catch_run).submit("a draft handed to the tool"))
    llm_run, _ = opened_on(works, None)
    llm_caught = render(ends.conductor(llm_run).submit("a draft handed to the tool"))
    long.conductor().forget()
    viewer = long.conductor()
    viewed_block = _under("true", lambda: viewer.start(longrun))
    view = long.conductor(viewer.run_id).shown(viewed_block)
    renewed = rendering.renewed("abcdef", {"renewed": {"from": {}, "to": {}}, "conducted_by": "principal"})
    bounce_env = bench.env("mode-bounce")
    bounce_env.write("SETTINGS.md", CAP)
    bounce_env.write("LONG.md", PAST)
    bounce_env.write("LONGRUN.md", LONGRUN)
    bounce_open = cli(bounce_env.engine, "-new", cwd=bounce_env.root,
                      env={VARIABLE: "true", "PP_DOOR": "LONGRUN.md"})   # a reading past the floor
    bounce_key = KEY.search(bounce_open.stdout).group(1) if KEY.search(bounce_open.stdout) else ""
    bounced = cli(bounce_env.engine, bounce_key, "a value", cwd=bounce_env.root) if bounce_key else None
    said = {"soft catch": caught, "view": view, "renewed": renewed,
            "bounce": bounced.stdout if bounced is not None else ""}
    calling = {name: [word for word in ("call back", "keyed call", "its next call", "the bare call")
                      if word in text] for name, text in said.items()}
    if (not any(calling.values()) and "call back" in llm_caught and bounced is not None
            and "chunk-pending" in bounced.stdout and "cut under the host's cap" in view):
        held("(e) no recovery text says to call pp",
             "the soft catch, the cut view, the renewed run and the bounced call speak of the message "
             "and the next prompt; the LLM's soft catch still says `call back`")
    else:
        failures.append(f"  ✗ (e) the recovery texts       {calling} bounced={bounced is not None and bounced.stdout[-200:]!r}")

    # --- (f) the renewal keeps the mode -------------------------------------------------------------
    renew_run, _ = opened_on(works)
    slot = persistence.slot_of(ends.made, renew_run)
    persistence.renew(slot, {"kit": "0"}, {"kit": "1"}, "2026-10-05T00:00:00Z")
    mark = persistence.renewed(slot) or {}
    reopened = ends.conductor(renew_run).resume(ends.conductor(renew_run).boot("BOOT.md"))
    if (mark.get("conducted_by") == "principal" and reopened is not None
            and _slot(ends, renew_run).get("conducted_by") == "principal"):
        held("(f) the renewal keeps the mode", f"run {renew_run}: the mark carries `conducted_by`, "
             "the reopened run is conducted by its principal")
    else:
        failures.append(f"  ✗ (f) the renewal              mark={mark} slot={_slot(ends, renew_run).get('conducted_by')}")

    # --- (g) any other value refuses ----------------------------------------------------------------
    odd = bench.env("mode-odd")
    before = len(persistence.slots(odd.made))
    refused = cli(odd.engine, "-new", cwd=odd.root, env={VARIABLE: "yes"})
    if refused.returncode == 2 and "conducted-by-invalid" in refused.stderr and len(persistence.slots(odd.made)) == before:
        held("(g) any other value refuses", "`PP_CONDUCTED_BY_PRINCIPAL=yes`: conducted-by-invalid, "
             "exit 2, no slot")
    else:
        failures.append(f"  ✗ (g) the odd value            rc={refused.returncode} {refused.stderr[-200:]!r} "
                        f"slots={len(persistence.slots(odd.made))}/{before}")

    # --- (h) -hook serves the principal's pending block ----------------------------------------------
    hooked_env = bench.env("mode-hook")
    hooked_env.write("WORKS.md", WORKS)
    cli(hooked_env.engine, "-new", cwd=hooked_env.root, env={VARIABLE: "true"})
    hooked = cli(hooked_env.engine, "-hook", cwd=hooked_env.root)
    if hooked.returncode == 0 and "▶ " in hooked.stdout and "./pp" not in "\n".join(_closing(hooked.stdout)):
        held("(h) -hook serves the principal's block", "the pending block rendered, its closing without a command")
    else:
        failures.append(f"  ✗ (h) the hook                 rc={hooked.returncode} {hooked.stdout[-200:]!r}")
    return 0
