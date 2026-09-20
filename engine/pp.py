#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""The conductor's entry point: it plays a procedure, the agent infers.

The KEY leads: `-new` mints your conversation's key, and every command that
addresses the run carries it FIRST. Without a key, pp only ever LOOKS -- it
never advances, never opens a run.

  (nothing)              -> INSPECTION only: where the one run under way is --
                            never advances anything
  <key>                  -> ADVANCE your run: the one forward call -- the next
                            block, the next chunk of a reading, the after-FINAL resume
  <key> <value>          -> advance with an inline value (a PICK's choice, verbatim)
  <key> -                -> advance with a production piped on stdin (heredoc)
  <key> -compacted       -> DECLARE that the host summarized the conversation: the
                            run serves itself back -- the boot's readings, the mounted
                            documents, and the pending block with every law verbatim.
                            pp never detects a compaction; it is told.
  <key> -s <name> [a ..] -> a skill, by name: ONE reader answers, the current
                            output's offer map -- each segment keeps its OWN list,
                            the pending block among them with no precedence; the
                            single owner routes the call to ITS step (laws and
                            trace follow); offered nowhere, the pending block
                            answers and nothing plays. A SCRIPT called bare (no
                            argument) does not run: its contract is its MANUAL,
                            mounted body alone into the view -- cut at the cap,
                            the run untouched
  <key> -s <name>@<n>    -> the same call, addressed to segment [n] -- what
                            SEVERAL owners ask for, a fused boot's ordinary case
  <key> -peek [name]     -> the block that STANDS, re-rendered DRY: where the run
                            is, never a step ahead of it -- the way back from a
                            parenthesis or a compaction; with a name, whether the
                            current output offers it (rc 2 otherwise)
  <key> -disable <package> | -enable <package>
                         -> the package OUT of this run's play, or back in: nothing
                            of it is served or played and its dependents leave with
                            it, the run standing where it was; the durable switch is
                            `package.<name>: on|off` at SETTINGS
  -stats [<key>|<days>] [--blocks] [-json]
                         -> what the runs cost, read from the traces. A run's KEY is read
                            first -- six hex characters -- so a key of digits names its run;
                            anything else made of digits is a number of days: exchanges,
                            blocks and reshows, tokens (estimated) and masses, proofs, repairs,
                            refusals, script calls, durations -- keyless, never advances;
                            `--blocks` renders what each OUTPUT carried instead: one table per
                            block, its lines in the order they were served, each saying its
                            state (served, spared, forced, reserved, missing, refused), where
                            it came from, which document asked and from which package
  -new                   -> a FRESH run, opened BESIDE any other conversation's --
                            its short key is handed HERE and leads every command this
                            run prints. The first call of a conversation is always
                            `-new`: the tool cannot tell a new conversation on its own.
  -install <workspace> [pkg ..] [-slug <slug>] [-claude] [-codex] [-gemini] [-cursor]
                         -> seed `<workspace>/.pp`; each host flag wires its full
                            adapter (card, entry file, standing rules, permissions path);
                            `-install -package <name>` adds to the CURRENT instance;
                            `-install -<host>` alone (no workspace) wires that
                            adapter onto the CURRENT instance -- day 2, write-once
  -hook                  -> the pending block, for a HARNESS to inject (silent when
                            nothing pends; never fails the prompt)
  -sync | -build         -> re-materialize the pins | compile catalog and registry
  -reset [<key>] | -test [-serial|-detail] [-repeat <n>] [area|name|path ...] -> forget the runs
                            (a key: that one alone) | this tool's fixtures, always played by the
                            PRODUCT's own engine -- the count alone, `-detail` for the lines the
                            scenarios printed, `-repeat <n>` for n passes and whatever moved

The workspace script `pp` forwards here verbatim; nine BARE verbs are the
OPERATOR'S CONSOLE, resolved before any skill name:

  upgrade                -> every pin moves to the source's current version,
                            re-materialized -- the open runs close
  add <package>          -> one more package into this instance, its prerequisites pinned
  remove <package>       -> one package out -- refused while another pin requires it
  repo <name>            -> a sibling workspace, installed and wired like this one
  doctor                 -> repair in place at constant pins -- runs survive
  help | version         -> the console's usage | the source and the pins

A package's `commands:` resolve NEXT, before the run's key: `./pp <verb> [args]`
runs the declared skill in a subprocess (the manifest's args first, then yours),
relays its output and returns its exit code -- `help` lists them after the
console's own.

A document DECLARES its procedure in one `proc:` key of its front matter -- one
keyword, optionally followed by an argument, per line. Anything unresolved
REFUSES: exit 2, nothing played.
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conductor import render   # noqa: E402 -- the block's text, the console's to print

from conductor import Block, Conductor, Refusal, instance, rendering   # noqa: E402

BOOT = "BOOT.md"
INSTANCE_DIR = instance.DIRECTORY   # where `install <workspace>` puts the instance; the
                                    # engine's one name for it -- `install.install()` takes
                                    # any target verbatim, this is the console's default

CONSOLE_HELP = """The operator's console -- the workspace script (`./pp`, Windows `.\\pp`):

  ./pp upgrade          every pinned package moves to the source's current
                        version, re-materialized -- the open runs close
  ./pp add <package>    one more package into this instance, its prerequisites pinned
  ./pp remove <package> one package out -- refused while another pin requires it
  ./pp repo <name>      a sibling workspace, installed and wired like this one
  ./pp doctor           repair in place at constant pins -- runs survive
                        bare, it says who is declared
  ./pp acquit <vector>  a treated signal vector stops asking: its counter and
                        its latch fall together
  ./pp version          the source checkout and the pinned versions
  ./pp help             this text"""

CONSOLE_TAIL = """The rest passes through to the conductor verbatim: `./pp` (where the run
is, read-only), `./pp <key>` (advance), `./pp <key> -s <skill>`, `./pp -test`,
`./pp -reset`. The full story lives in REFERENCE.md, "The operator's console"."""


def _help(meta: Path | None) -> str:
    """The console's usage, COMPOSED: the verbs of its own, then every command the
    pinned packages declare (`contributes.commands`), in the requires topology then
    declaration order -- `./pp <verb>`, its package, the description its skill's
    contract carries, on one line. No instance underneath: the verbs alone."""
    sections = [CONSOLE_HELP]
    if meta is not None:
        from conductor import contributions, instance, reading
        lines = []
        for entry in contributions.commands(meta):
            contract = instance.skill_contract(meta, str(entry["skill"]))
            said = ""
            if contract is not None:
                try:
                    said = str(reading.read(contract).front.get("description") or "")
                except Refusal:
                    said = ""
            said = " ".join(said.split()) or "(no description)"
            lines.append(f"  {'./pp ' + str(entry['verb']):<22}({entry['package']}) {said}")
        if lines:
            sections.append("The packages' commands, resolved after the console's own:\n\n"
                            + "\n".join(lines))
    sections.append(CONSOLE_TAIL)
    return "\n\n".join(sections)


def ride(argv: list[str], flag: str, what: str) -> tuple[list[str], str | None]:
    """-> (argv without `flag value`, the value; None when absent) -- the one
    extractor for options that come with a call."""
    if flag not in argv:
        return argv, None
    at = argv.index(flag)
    if at + 1 >= len(argv):
        raise SystemExit(f"pp {flag} needs {what}")
    return argv[:at] + argv[at + 2:], argv[at + 1]


def _load(path: Path):
    """A module loaded by PATH, not by package -- `adapters/` sits outside `conductor`,
    optional, pulled in only when its flag asks for it. The module is registered in
    `sys.modules` under a name derived from its path BEFORE it runs, as an import would:
    a dataclass resolves its module there, and two `wire.py` keep two names."""
    import importlib.util
    name = re.sub(r"\W", "_", f"pp_load_{path.parent.name}_{path.stem}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _resolve_skill(meta: Path, name: str) -> tuple[str, Path | None]:
    """-> what `name` IS, by inspection -- ("proc"|"script"|"offer"|"unknown", where).
    A `proc:` in the front matter makes it conducted; a script beside its contract
    makes it runnable; both at once is a homonym and refuses."""
    from conductor import instance, reading
    hits = []
    document = instance.resolve(meta, f"{name}.md")
    if document.is_file():
        front = reading.read(document).front
        hits.append(("proc" if front.get("proc") else "offer", document))
    contract = instance.skill_contract(meta, name)
    if contract is not None:
        script = contract.parent / f"{name}.py"
        hits.append(("script", script) if script.is_file() else ("offer", contract))
    kinds = {kind for kind, _ in hits}
    if {"proc", "script"} <= kinds or ("proc" in kinds and len(hits) > 1):
        raise Refusal("skill-ambiguous",
                      f"`{name}` names both a conducted skill and another -- rename one")
    if not hits:
        return "unknown", None
    hits.sort(key=lambda one: one[0] != "proc")
    return hits[0]


def _product() -> Path:
    """-> the product checkout to seed from: the running engine's own -- or, when
    this engine is a VENDORED copy, the instance's declared source (a vendored
    tree carries no packages and no adapters)."""
    from conductor import discovery, install, instance
    member = discovery.instance_member(Path(__file__))
    if member is None:
        return install.product_root(Path(__file__))
    source = Path(instance.read(member.meta).get("source", ""))
    if not source.is_dir():
        raise Refusal("source-missing",
                      f"{member.meta} points at `{source}` -- not a directory")
    return source


def _wire(workspace: Path, meta: Path, providers: list[str]) -> int:
    """Runs each named adapter over `workspace` -- the shared tail of every
    install that knows its harnesses. -> how many artifacts were written."""
    adapters = _product() / "adapters"
    wrote = 0
    for name in providers:
        adapter = _load(adapters / name / "wire.py")
        for done in adapter.wire(workspace.resolve(), meta):
            print(f"pp: {done}")
            wrote += 1
    return wrote


def _add(name: str) -> int:
    """One more package into the CURRENT instance -- with the fresh-workspace way
    out when the package's user-level files would replace the operator's own."""
    from conductor import discovery, install
    member = discovery.installed_member(Path(__file__))
    clashes = install.user_clashes(member.meta, name)
    if clashes:
        print(f"pp: `{name}` installs USER-level files "
              f"({', '.join(clashes)}) -- a fresh, just-installed workspace "
              "is recommended; here, your files would be replaced and saved "
              "as `.old`.")
        fresh = ""
        if sys.stdin.isatty():
            fresh = input("pp: fresh workspace name "
                          "(empty = replace here): ").strip()
        if fresh:
            providers = install.wired_providers(member.path)
            made = install.install(_product() / "engine" / "pp.py", Path(fresh) / INSTANCE_DIR,
                                   [name], doors=not providers)
            print(f"pp: instance installed at {made}")
            _wire(Path(fresh), made, providers)
            return 0
    made = install.add_package(member, name)
    print(f"pp: `{name}` installed at {made}")
    return 0


def _console_verb(argv: list[str]) -> int:
    """The operator's console: bare verbs resolved BEFORE the skills -- the
    workspace script forwards everything here verbatim."""
    from conductor import discovery, install, instance
    verb, arguments = argv[0], argv[1:]
    if verb == "help":
        standing = discovery.instance_member(Path(__file__))
        print(_help(standing.meta if standing else None))
        return 0
    member = discovery.installed_member(Path(__file__))
    if verb == "version":
        from conductor import VERSION
        declared = instance.read(member.meta)
        print(f"source {declared.get('source', '?')}")
        at_source = install.source_version(Path(str(declared.get("source", ""))))
        moved = (f" -- the source holds {at_source}; `upgrade` moves you there"
                 if at_source != VERSION else "")
        print(f"engine {VERSION}{moved}")
        for name, version in instance.pins(member.meta).items():
            print(f"{name} {version}")
        return 0
    if verb == "upgrade":
        if arguments:
            raise SystemExit("pp upgrade takes no argument")
        told = install.upgrade(member)
        if not told:
            print("pp: already current -- nothing touched (`doctor` repairs in place).")
            return 0
        for line in told:
            print(f"pp: {line}")
        return 0
    if verb == "acquit":
        if len(arguments) != 1:
            raise SystemExit("pp acquit needs one vector")
        from conductor import events
        fell = events.acquit(member.meta, arguments[0])
        print(f"pp: `{arguments[0]}` acquitted -- {fell} entr"
              f"{'y' if fell == 1 else 'ies'} of the record fell")
        return 0
    if verb == "doctor":
        if arguments:
            raise SystemExit("pp doctor takes no argument")
        from conductor import compiling
        for line in install.doctor(member):
            print(f"pp: {line}")
        for warning in compiling.lint(member.meta):
            print(f"pp: WARNING -- {warning}")
        return 0
    if verb == "add":
        if len(arguments) != 1:
            raise SystemExit("pp add needs one package name")
        return _add(arguments[0])
    if verb == "remove":
        if len(arguments) != 1:
            raise SystemExit("pp remove needs one package name")
        for line in install.remove_package(member, arguments[0]):
            print(f"pp: {line}")
        return 0
    if len(arguments) != 1:
        raise SystemExit("pp repo needs one workspace name")
    providers = install.wired_providers(member.path)
    packages = [one for one in instance.pins(member.meta) if one != install.BASE]
    workspace = member.path.parent / arguments[0]
    made = install.install(_product() / "engine" / "pp.py", workspace / member.meta_name,
                           packages, doors=not providers)
    print(f"pp: instance installed at {made}")
    if providers:
        _wire(workspace, made, providers)
    else:
        print(f"  two entry files were written at {made.parent} — wire a harness to them (see the README)")
    return 0


def _command(member, entry: dict, arguments: list[str]) -> int:
    """A package's console verb: the declared skill runs in a SUBPROCESS (the
    engine imports no package code) with the manifest's `args` first and the
    operator's after; its stdout is relayed line by line, its stderr verbatim,
    its exit code returned as is. What it says to the bus (`::push`, `::clear`)
    is harvested by the ONE collector on a clean exit; a `::mount` has no run to
    arrive in at the console and refuses by name -- after the skill ran."""
    from conductor import contributions, events, instance
    skill = str(entry["skill"])
    contract = instance.skill_contract(member.meta, skill)
    script = contract.parent / f"{skill}.py" if contract else None
    if script is None or not script.is_file():
        raise Refusal("command-broken",
                      f"`{entry['verb']}` -> `{skill}` -- the manifest of `{entry['package']}` "
                      "declares it, no script answers: `doctor` repairs the instance")
    args = [str(one) for one in (entry.get("args") or [])] + arguments
    rc, out, err = contributions.run_skill(member.meta, skill, args)
    mounted = [line for line in out.splitlines() if line.startswith("::mount ")]
    rest = (events.harvest(member.meta, out) if rc == 0 else out.splitlines())
    for line in rest:
        # a failed skill pushed nothing (its directives stay unharvested), and no
        # directive ever reaches the operator's screen -- the same rule as `-s`
        if not line.startswith(("::push ", "::clear ", "::mount ")):
            print(line)
    if err:
        sys.stderr.write(err)
    if rc == 0 and mounted:
        # said HERE, not through the console's catch-all: the skill DID play --
        # its lines and its pushes stand -- only its mount found no run
        refusal = Refusal("mount-without-run",
                          f"`{entry['verb']}` printed a `::mount` directive -- the console has "
                          "no run to host it; a mount needs a keyed call (`-s`)")
        sys.stderr.write(f"pp: REFUSED — {refusal}\n  the skill ran; its mount did not.\n")
        return 2
    return rc


def denied(conductor: Conductor, block: Block, name: str) -> int:
    """The out-of-turn catch: the pending block answers, the ask named as not played --
    dry, no repair counted (a repair is for a WATCHED answer that missed). Exit 2.
    A stranger -- a name declared nowhere -- is caught here too: the pending block
    answers, never the console's usage."""
    import dataclasses
    block = dataclasses.replace(
        block, deviation=(f"`{name}` is not offered at this step -- "
                          "the floor resumes below; the work was NOT done."))
    print(conductor.shown(block))     # a view: cut under the cap, nothing kept
    return 2


def report(conductor: Conductor, block: Block | None) -> int:
    if block:
        # the engine hands over its own text: it measures what it prints and closes
        # under the host's cap, the rest waiting at the run for the next bare call
        print(conductor.rendered(block))
        return 0
    print("pp: the procedure is complete — nothing more to do.")
    return 0


def conductor_pending(key: str) -> bool:
    """-> whether the run `key` still holds the matter of a cut block."""
    try:
        return Conductor.here(Path(__file__), key).pending()
    except Refusal:
        return False


def _standing_keys(script: Path) -> set[str]:
    """-> the keys of every run under way -- the finite set a positional key
    resolves against; a first token in it addresses THAT run."""
    from conductor import discovery, persistence
    member = discovery.installed_member(script)
    return {persistence.run_id_of(slot) for slot in persistence.slots(member.meta)}


def main(argv: list[str]) -> int:
    conductor = None
    # a run is designated by the KEY of the command, never by the shell: whatever the
    # environment inherited is dropped here, and a keyed call names its run again
    os.environ.pop("PP_RUN", None)
    try:
        if argv and argv[0] == "-install":
            from conductor import install
            if "-package" in argv[1:]:
                rest, name = ride(argv[1:], "-package", "a name")
                if rest:                        # anything else -- a workspace, another
                    raise Refusal("install-ambiguous",  # flag -- this form takes ONLY the name
                                  "`-package <name>` targets the current instance alone")
                return _add(name)
            if len(argv) < 2:
                raise SystemExit("pp -install <workspace> [package ...] [-slug <slug>] "
                                 "[-claude] [-codex] [-gemini] [-cursor]")
            if argv[1].startswith("-"):
                # the DAY-2 form: no workspace leads -- host flags alone, and the
                # adapters wire the CURRENT instance's workspace (the `-package` motif)
                from conductor import discovery
                allowed = tuple(f"-{name}" for name in ("claude", "codex", "gemini", "cursor"))
                strange = [a for a in argv[1:] if a not in allowed]
                if strange:
                    raise Refusal("install-ambiguous",
                                  f"`{' '.join(strange)}` -- the day-2 form takes host "
                                  "flags alone: `-install -claude|-codex|-gemini|-cursor`")
                member = discovery.instance_member(Path(__file__))
                if member is None:
                    raise Refusal("instance-missing",
                                  "nothing to wire -- the day-2 form runs from an "
                                  "installed instance")
                wired = [name for name in ("claude", "codex", "gemini", "cursor")
                         if f"-{name}" in argv[1:]]
                if "gemini" in wired:
                    import shutil
                    if shutil.which("gemini") is None:
                        raise Refusal("gemini-missing",
                                      "`-gemini` needs the gemini CLI on PATH -- the standing "
                                      "rules compose over its baseline")
                if not _wire(member.path, member.meta, wired):
                    print("pp: nothing to write -- already wired")
                return 0
            workspace = Path(argv[1])
            rest, slug = ride(argv[2:], "-slug", "a value")
            wired = [name for name in ("claude", "codex", "gemini", "cursor")
                     if f"-{name}" in rest]
            if "gemini" in wired:
                import shutil
                if shutil.which("gemini") is None:
                    raise Refusal("gemini-missing",
                                  "`-gemini` needs the gemini CLI on PATH -- the standing "
                                  "rules compose over its baseline")
            packages = [a for a in rest if not a.startswith("-")]
            made = install.install(_product() / "engine" / "pp.py", workspace / INSTANCE_DIR, packages,
                                   slug=slug, doors=not wired)
            print(f"pp: instance installed at {made}")
            if wired:
                _wire(workspace, made, wired)
            else:
                print(f"  two entry files were written at {made.parent} — wire a harness to them (see the README)")
            return 0
        from conductor import compiling
        if argv and argv[0] in compiling.RESERVED:
            # the operator's console -- bare verbs, resolved before any skill name
            return _console_verb(argv)
        if argv and not argv[0].startswith("-"):
            # the packages' commands -- resolved AFTER the console's verbs and
            # BEFORE the run's key (a verb never takes a key's form: the build
            # refuses it); an installed engine alone carries a composition
            from conductor import contributions, discovery
            standing = discovery.instance_member(Path(__file__))
            if standing is not None:
                entry = contributions.command(standing.meta, argv[0])
                if entry is not None:
                    return _command(standing, entry, argv[1:])
        if argv and argv[0] == "-test":
            # the bench lives at the PRODUCT checkout (tests/ beside engine/, kit/, packages/):
            # a vendored engine reaches it through the instance's declared source -- and HANDS
            # the call over to the product's own engine, so the conductor the scenarios import
            # and the one they install from are one code; the source engine plays it itself
            product = _product()
            source_engine = (product / "engine" / "pp.py").resolve()
            if Path(__file__).resolve() != source_engine:
                import subprocess
                return subprocess.run([sys.executable, str(source_engine), *argv]).returncode
            sys.path.insert(0, str(product))
            from tests.harness import run as run_bench
            return run_bench(argv[1:])
        if argv and argv[0] in ("-sync", "-build"):
            # the REPAIR calls stand on the member alone -- a conductor needs the
            # vendored bundles, which is exactly what `sync` exists to (re)materialize
            from conductor import compiling, discovery, install
            from conductor import Member
            if len(argv) > 1:      # repair FROM OUTSIDE: an instance whose own engine is stale
                meta = Path(argv[1]).resolve()
                member = Member(path=meta.parent, name=meta.parent.name, meta_name=meta.name)
            else:
                member = discovery.installed_member(Path(__file__))
            if argv[0] == "-sync":
                for made in install.sync(member):
                    print(f"pp: {made} materialized.")
            else:
                compiling.render_registry(member.meta)   # validates; writes nothing
                for made in filter(None, (compiling.build_tools(member.meta),
                                          compiling.build_system(member.meta))):
                    print(f"pp: {made} compiled.")
                for made in install.console(member.meta):
                    print(f"pp: {made} rewritten.")
                for warning in compiling.lint(member.meta):
                    print(f"pp: WARNING -- {warning}")
            return 0
        if argv and argv[0] == "-hook":
            # a harness channel (e.g. a per-message hook) injects where the run stands:
            # the conduction arrives WITH the operator's message, from the harness's own
            # trusted config -- the agent never has to decide to execute-and-obey.
            try:
                conductor = Conductor.here(Path(__file__))
                block = conductor.resume(conductor.boot(BOOT))
                # documentary: the hook feeds the host's PROMPT, not a tool result -- the
                # cap is the tool's (a fact of the host), so the block goes whole here: the
                # one bare render of the engine, on purpose
                text = render(block) if block and block.next_call else ""
            except Refusal as refusal:
                if conductor is not None:
                    conductor.noted(refusal)
                # several conversations: the hook cannot know whose message this is
                text = ("" if refusal.code == "run-ambiguous"
                        else f"pp: REFUSED — {refusal}")   # context for the agent to repair
            if text:
                print(text)
            return 0
        if argv and argv[0] == "-new":
            # ALWAYS starts fresh -- never resume()'s "continue if something's pending".
            # Destructive by construction: called once, at the true start of a
            # conversation, never replayed once a run is under way. Silent about
            # whatever it discarded -- that belongs in a log, never in the session.
            conductor = Conductor.here(Path(__file__))
            return report(conductor, conductor.start(conductor.boot(BOOT)))
        if argv and argv[0] == "-reset":
            conductor = Conductor.here(Path(__file__), argv[1] if len(argv) > 1 else None)
            dropped = conductor.forget()
            print(f"pp: {dropped} run(s) forgotten — `-new` opens a fresh one.")
            return 0
        if argv and argv[0] in ("-run", "-answer"):
            raise SystemExit("pp: `-run` and `-answer` are gone -- the key leads: "
                             "`./pp <key> [value|-|-s <name> [args]|-peek]`")
        if not argv:
            # keyless = INSPECTION only: shows where the single run stands --
            # never advances anything, never opens a run; the first line says the
            # effort in force -- a display for the operator, the agent owes it no
            # reading (the first call of a conversation is `-new`, always)
            conductor = Conductor.here(Path(__file__))
            print(f"pp: effort — {conductor.effort() or '—'}")
            block = conductor.peek()
            if block is None:
                said = rendering.packages(conductor.switch_state())
                if said:
                    print(said)          # the DURABLE state: what SETTINGS switches off
                print("pp: no run is under way -- `-new` opens one.")
                return 0
            print(conductor.shown(block))     # a view: cut under the cap, nothing kept
            return 0
        key = (argv[0] if not argv[0].startswith("-")
               and argv[0] in _standing_keys(Path(__file__)) else None)
        if key is not None:
            rest = argv[1:]
            if (rest[:1] not in (["-peek"], ["-compacted"], ["-disable"], ["-enable"])
                    and conductor_pending(key)):
                # a block cut under the cap: its next chunk comes BEFORE the flow moves --
                # the bare call serves it; any other call BOUNCES: the chunk is served, the
                # call is said not played, nothing is lost and nothing is recorded
                conductor = Conductor.here(Path(__file__), key)
                print(conductor.next_chunk())
                if rest:
                    print(f"pp: chunk-pending -- `{' '.join(rest)}` was not played: a reading "
                          "continues; the bare call serves it, play yours after the last chunk")
                return 0
            if rest[:1] == ["-s"]:
                if len(rest) < 2:
                    raise SystemExit("pp -s needs a skill name")
                return _skill(key, rest[1], rest[2:])
            if rest[:1] and rest[0].startswith("-") \
                    and rest[0] not in ("-", "-s", "-peek", "-mount", "-compacted",
                                        "-disable", "-enable"):
                # a dash-word the console does not know is no value: named, nothing played
                raise Refusal("verb-unknown",
                              f"`{rest[0]}` is no verb of the console -- `./pp help` lists them")
            if rest[:1] == ["-compacted"]:
                if len(rest) > 1:
                    raise SystemExit("pp -compacted takes no other argument -- it declares "
                                     "that the host summarized the conversation")
                conductor = Conductor.here(Path(__file__), key)
                return report(conductor, conductor.compacted())
            if rest[:1] in (["-disable"], ["-enable"]):
                # the SOFT switch: the operator's word, said to the agent and written at
                # the run -- one package out of the play (its dependents with it) or back
                # in, and the block that stands comes back; the run never moves
                if len(rest) != 2:
                    raise SystemExit(f"pp {rest[0]} takes one package name -- "
                                     "the durable switch is `package.<name>: on|off` at SETTINGS")
                conductor = Conductor.here(Path(__file__), key)
                print(conductor.switch(rest[1], rest[0] == "-disable"))
                return 0
            if rest[:1] == ["-peek"]:
                conductor = Conductor.here(Path(__file__), key)
                block = conductor.peek()
                if block is None:
                    return 0
                # `-peek <name>` asks the same reader as a call would: the offer map
                # of the current output, never the block's own list
                if len(rest) > 1 and conductor.route(rest[1]) is None:
                    return denied(conductor, block, rest[1])
                print(conductor.shown(block))     # a view: cut under the cap, nothing kept
                return 0
            if rest[:1] == ["-mount"]:
                # the HOSTING verb: documents of the instance enter the current
                # view until the exchange ends -- bare paths take the defaults
                # (constraints+tools); ONE JSON array picks per document
                if len(rest) < 2:
                    raise SystemExit(
                        "pp -mount takes documents: paths, or one JSON array of "
                        '{"doc"[, "body": true|false|["<start>..<end>", ...], '
                        '"constraints", "tools": true|false]}')
                raw = rest[1:]
                if len(raw) == 1 and raw[0].lstrip().startswith("["):
                    import json as mount_json
                    try:
                        entries = mount_json.loads(raw[0])
                    except ValueError as wrong:
                        raise Refusal("mount-invalid", f"not one valid JSON array -- {wrong}")
                else:
                    entries = [{"doc": one} for one in raw]
                conductor = Conductor.here(Path(__file__), key)
                print(conductor.mount(entries))
                return 0
            given = " ".join(rest)
            if given == "-":
                given = sys.stdin.read().strip()
            conductor = Conductor.here(Path(__file__), key)
            return report(conductor, conductor.forward(given))
        if argv[0] == "-s":
            if len(argv) < 2:
                raise SystemExit("pp -s needs a skill name")
            return _skill(None, argv[1], argv[2:])
        if argv[0] == "-compacted":
            raise Refusal("no-run",
                          "`-compacted` declares the compaction of YOUR run, so it "
                          "leads with the key: `./pp <key> -compacted`; with the key "
                          "gone too, `-new` opens a run")
        if argv[0] == "-stats":
            # INSPECTION of the traces: what the runs cost -- keyless, reads the
            # state directory, opens nothing, advances nothing
            from conductor import discovery, instance
            from conductor.state import traces
            member = discovery.installed_member(Path(__file__))
            rest = list(argv[1:])
            as_json = "-json" in rest
            # `--blocks` reads the LEDGER the engine writes with every block: what each
            # output carried, in the order it was served, where it came from and who asked
            per_block = "--blocks" in rest
            rest = [one for one in rest if one not in ("-json", "--blocks")]
            if len(rest) > 1:
                raise SystemExit("pp -stats [<days>|<key>] [--blocks] [-json]")
            days, key = None, None
            if rest:
                # a run's KEY is read first: six hex characters is a shape, and one key
                # in seventeen is all digits ((10/16)^6) -- read as a count of days it
                # would answer with every run of the instance instead of the one asked
                if re.fullmatch(r"[0-9a-f]{6}", rest[0]):
                    key = rest[0]
                elif rest[0].isdigit():
                    days = int(rest[0])
                else:
                    raise SystemExit("pp -stats takes a number of days or a run's key")
            found = traces.runs(member.meta / instance.STATE, days=days, key=key)
            if per_block:
                if as_json:
                    import json as stats_json
                    print(stats_json.dumps({"scope": {"days": days, "key": key},
                                            "blocks": traces.blocks(found)},
                                           indent=1, ensure_ascii=False))
                else:
                    print(traces.render_blocks(found, days, key))
                return 0
            print(traces.render_json(found, days, key) if as_json
                  else traces.render(found, days, key))
            return 0
        if argv[0] == "-et":
            # the END-TURN stamp: keyless and INERT -- one `turn-end` line on the most
            # recently written run trace, so the agent's tail becomes deducible; the
            # harness Stop hook plays it, and so does the operator's top in a spare
            # console -- the engine reads no policy key here (the switch gates the
            # hook's installation, never the fact)
            from conductor import discovery, instance
            from conductor.state import log
            member = discovery.installed_member(Path(__file__))
            state = member.meta / instance.STATE
            traced = sorted(state.glob("session-*.jsonl"), key=lambda p: p.stat().st_mtime)
            if not traced:
                raise Refusal("no-run", "no run trace to stamp -- `-new` opens a run")
            log.record(traced[-1], "turn-end")
            print(f"pp: turn-end -- {traced[-1].name}")
            return 0
        if argv[0] == "-peek":
            conductor = Conductor.here(Path(__file__))
            block = conductor.peek()
            if block is None:
                return 0
            if len(argv) > 1 and conductor.route(argv[1]) is None:
                return denied(conductor, block, argv[1])
            print(conductor.shown(block))     # a view: cut under the cap, nothing kept
            return 0
        if not argv[0].startswith("-"):
            if re.fullmatch(r"[0-9a-f]{6}", argv[0]):
                raise Refusal("run-unknown",
                              f"`{argv[0]}` -- no run holds that key; your "
                              "conversation's key was handed at `-new`")
        raise SystemExit(__doc__)
    except Refusal as refusal:
        if conductor is not None:      # best-effort: a refusal with no run resolved has no home
            conductor.noted(refusal)
        sys.stderr.write(f"pp: REFUSED — {refusal}\n  nothing played.\n")
        return 2


def _played(runner, where, arguments: list[str], base: str,
            entry: dict | None = None, head: str = "", anchor: str = "") -> int:
    """Runs a script call and HARVESTS its directives: the script owns the
    moment the state changed, so it owns the push -- a `::push <signal> <vector>
    <text>` line replaces the held entry, a `::clear <signal> <vector>` removes
    it, and a `::mount <json>` line MOUNTS the documents it names in the same
    call (the deterministic macro's channel: the script derives, pp hosts);
    every other line is the script's TEXT. The text leaves through the seam of
    every output: under the host's cap as the script wrote it, over it in chunks
    (`head` opens each), the rest waiting at the run -- and a mount's view joins
    the same output, so one call leaves one rest. The trace weighs the text.
    Declared call signals still push after a clean run."""
    import contextlib
    import io
    import json as mount_json
    from conductor import events
    buffer = io.StringIO()
    rc = 1
    try:
        with contextlib.redirect_stdout(buffer):
            rc = _load(where).main(arguments) or 0
    finally:
        lines = buffer.getvalue().splitlines()
        text = "\n".join(line for line in lines
                         if not line.startswith(("::push ", "::clear ", "::mount ")))
        runner.gesture_trace(base, entry or {}, said=text)
    mounts = [line[len("::mount "):] for line in lines if line.startswith("::mount ")]
    # the anchor line of a fused output opens the text: it counts under the same cap
    shown = f"{anchor}\n\n{text}" if anchor else text
    if rc != 0 or not mounts:
        if shown:
            print(runner.gestured(shown, head))
        if rc != 0:
            return rc
    # the harvest runs only on a CLEAN call: a failed script pushed nothing --
    # the bus's ONE collector stands the pushes and clears, the mounts stay here
    events.harvest(runner.member.meta, buffer.getvalue())
    for rank, raw in enumerate(mounts):
        # a clean call's mounts play LAST: the pushes stood first, and the mount's own
        # output closes the call on the freshly hosted block -- the script's text leads it
        try:
            entries = mount_json.loads(raw)
        except ValueError as wrong:
            raise Refusal("mount-invalid",
                          f"`::mount` payload is not one valid JSON array -- {wrong}")
        print(runner.mount(entries, lead=shown if rank == 0 else ""))
    for source, signal in events.gesture_signals(runner.member.meta, base):
        runner._signal(source, signal, evidence=" ".join(arguments))
    return rc


def _skill(run: str | None, name: str, arguments: list[str]) -> int:
    """The `-s` call: pp inspects what the name resolves to and does the right
    thing -- the agent's reflex IS the call. Conducted, executed, or served.
    ONE reader answers: the current output's offer map, where each segment keeps
    its own closed list and the pending block is a segment like the others -- the
    single owner routes, several owners refuse by name, `name@<n>` says which."""
    conductor = None
    try:
        base, sep, tail = name.partition("@")
        if sep and not tail.isdigit():
            raise Refusal("address-invalid",
                          f"`{name}` -- what follows `@` is the segment number: "
                          f"`-s {base}@<n>`")
        at = int(tail) if sep else None
        conductor = Conductor.here(Path(__file__), run)
        kind, where = _resolve_skill(conductor.member.meta, base)
        block = conductor.peek()
        entry = None
        if block is not None:
            # ONE order, said and applied: the addressed segment when `@n` names it,
            # else the single owner among ALL the output's segments -- the pending one
            # competes like any other, so a name offered twice REFUSES instead of
            # silently taking the pending branch
            entry = conductor.route(base, at) if at is not None else conductor.route(base)
        if kind == "unknown" and block is not None and entry is not None:
            # ADOPTION ON OFFER: the offer is the consent -- an offered name may
            # resolve at a harness home; an unoffered copy stays invisible.
            from conductor import instance
            contract = instance.adopted(conductor.member.meta, base)
            if contract is not None:
                kind, where = "offer", contract
        # a name declared nowhere is no different from a name not offered here: with a
        # run, the pending block answers (`denied`); without one, the refusal names -new --
        # the console's usage is for the operator's console, never a reply to a skill call
        if block is None:
            raise Refusal("no-run", "no run is under way -- call `-new` first")
        if entry is None:
            return denied(conductor, block, name)
        if kind == "proc":
            player = Conductor.here(Path(__file__), run)   # the peeked one is dry-tainted
            return report(player, player.play(base, route=entry))
        if kind == "script":
            # a GESTURE, never a step: the call plays the script and the run stays
            # exactly where it stood -- position, pending block and offer map all
            # untouched. What it renders is the anchor line (a fused output only),
            # then the skill's own output; the skill's guard refuses by name.
            runner = Conductor.here(Path(__file__), run)
            if not arguments:
                runner.gesture_trace(base, entry or {})
                # called BARE, a script does not run: its contract is its MANUAL,
                # mounted body alone into the current view through the one reader --
                # cut at the cap, proven by its hash, in the ledger, swept with the
                # exchange; the standing block renders under it, the run untouched
                contract = (where.parent / "SKILL.md").relative_to(runner.member.meta)
                print(runner.mount([{"doc": str(contract), "body": True,
                                     "constraints": False, "tools": False}]))
                return 0
            return _played(runner, where, arguments, base, entry,
                           rendering.head(block), runner.anchor_line(entry))
        if kind == "offer" and where is not None:
            from conductor import compiling
            if not compiling.conductible(where):
                # the skill IS a CALL: its constraints enter force with its frame,
                # its body is the brief, an implicit INFER carries the work -- the
                # close resumes the flow (`proc:` present plays the declared one)
                player = Conductor.here(Path(__file__), run)
                return report(player, player.play(base, route=entry))
            # found, not pp-compatible: INDIFFERENT -- offered name-only, nothing
            # conducted; the build's warning names what it lacks
        print(f"pp: `{base}` is offered here, and pp has nothing to run for "
              "it -- it is yours, through your harness.")
        return 0
    except Refusal as refusal:
        if conductor is not None:      # best-effort: a refusal with no run resolved has no home
            conductor.noted(refusal)
        sys.stderr.write(f"pp: REFUSED — {refusal}\n  nothing played.\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
