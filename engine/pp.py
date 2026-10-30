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
                            block, the next chunk of a reading, the resume of a parked run
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
  <key> -skip            -> DROP the rest of a reading cut under the cap: its block's
                            closing comes at once, the readings it carried stay unproven
  <key> -peek [name]     -> the block that STANDS, re-rendered DRY: where the run
                            is, never a step ahead of it -- the way back from a
                            parenthesis or a compaction; with a name, whether the
                            current output offers it (rc 2 otherwise)
  <key> -disable <package> | -enable <package>
                         -> the package OUT of this run's play, or back in: nothing
                            of it is served or played and its dependents leave with
                            it, the run standing where it was; the durable switch is
                            `package.<name>: on|off` at SETTINGS
  (every keyed call but -peek HOLDS the run's call lock while it plays: a second
   call on the same run waits `call_lock_wait` seconds -- SETTINGS, 30 by default --
   then refuses `call-busy`: replay it once the first has answered; a process a
   call launched that calls its own run back refuses `call-reentrant`)
  (every call that resolves an instance HOLDS its machine's maintenance lock SHARED
   for its whole life; `upgrade`, `doctor`, `add`, `remove` and `-sync` try it
   EXCLUSIVE: a pp process active under the machine refuses them `maintenance-busy`,
   and while one holds it every other call refuses `maintenance-in-progress`)
  (a run an `upgrade` RENEWED keeps its key: its next keyed call reopens it on its boot,
   the trace continued; the text the call carries plays as the message the run waited
   for, anything else is said not played; `-peek` and `./pp` say the renewal and write
   nothing)
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
  -new [<message> ..]    -> a FRESH run, opened BESIDE any other conversation's --
                            its short key is handed HERE and leads every command this
                            run prints; the words after it are the principal's message,
                            joined by a blank and traced `prompt` before the first block
                            (the grammar of `<key> <message>`, at the opening). The first
                            call of a conversation is always `-new`: the tool cannot
                            tell a new conversation on its own. A LAUNCHER may
                            name the run's ENTRY: `PP_DOOR=<document>`
                            opens that document as a CALL above the boot -- the first
                            exchange carries it; an unknown name refuses and leaves
                            nothing. A launcher may name the run's MATERIAL, the tree
                            it works on: `PP_WORKDIR=<path>` (relative to the
                            workspace or absolute), kept at the run as the material
                            `work` -- a serve row reads it by `@work`; `material.<name>:
                            <path>` at SETTINGS declares the others, a row names one by
                            `@<name>`, a document by `material: <name>`, and a row that
                            names none reads as it always did. A launcher may give the
                            run one more ROOT of documents: `PP_DOCUMENTS=<absolute
                            directory>`, kept at the run -- for that run alone its
                            documents resolve, declare (`attach:`, `mount:`) and overlay
                            between the instance's space and the packages', at every
                            later call and through an upgrade's renewal; a path that is
                            not an absolute directory refuses `documents-unknown`, a
                            keyed call naming another root `documents-fixed`, nothing
                            played. A launcher that makes the run advance itself
                            says so: `PP_CONDUCTED_BY_PRINCIPAL=true` opens a run its
                            principal conducts -- an output that owes no call carries
                            no closing, a chunk ends on its matter
                            (`conducted-by-invalid` for any value but `true`, `false`
                            or empty). In such a run the launcher carries the same
                            mark on each of ITS keyed calls, never in the agent's
                            environment: a marked call is the principal's, any other
                            the agent's. The agent's bare call refuses
                            `principal-advances`; its value is judged as in any run,
                            and every block a call of the agent renders -- the step
                            after its value, a mount, a manual, a routed skill, a
                            re-serve, a switch's block, a peek, a denied offer -- is
                            HELD at the run: the agent gets what the act answers and
                            one line (`value judged`, `mounted`, `opened`...); the
                            principal's bare call serves the
                            held output (cut under the cap as any output), else
                            advances; a marked call with a text while an output is
                            held refuses `output-held`; any call of the agent while
                            one is held bounces, nothing played. A `-new` without the mark while
                            such a run is mid-exchange opens nothing and says so.
  -install <workspace> [pkg ..] [-slug <slug>] [-base <package>] [-own] [-claude] [-codex] [-gemini] [-cursor]
                         -> seed `<workspace>/.pp`; `-base` names the package the instance
                            is built on (the kit by default -- `base:` at instance.yaml);
                            played by an installed engine, a workspace under an instance
                            that carries a machine BORROWS it (no engine, no vendor, no
                            pins of its own: the machine's versions and composition) --
                            `-own` gives it a copy of the machine instead;
                            each host flag wires its full
                            adapter (card, entry file, standing rules, permissions path);
                            `-install -package <name>` adds to the CURRENT instance;
                            `-install -<host>` alone (no workspace) wires that
                            adapter onto the CURRENT instance -- day 2, write-once
  -hook                  -> the pending block, for a HARNESS to inject (silent when
                            nothing pends; never fails the prompt)
  -sync | -build         -> re-materialize the pins | compile catalog and registry
  -purge <key> ... | --before <YYYY-MM-DD> [--yes] [-json]
                         -> remove for good what the engine keeps of runs -- the slot or
                            renewal mark, every `session-<key>.*`, every trace of the key --
                            the runs named, or every run and keyless trace last written
                            before the date; without `--yes` it says what it would remove
                            and writes nothing; a run a call holds refuses `call-busy`,
                            nothing removed (`purge-invalid`: a malformed date)
  -reset [<key>] | -test [-serial|-detail] [-repeat <n>] [area|name|path ...] -> forget the runs,
                            renewed ones included (a key: that one alone; a run a call holds refuses `call-busy`,
                            nothing forgotten) | this tool's fixtures, always played by the
                            PRODUCT's own engine -- the count alone, `-detail` for the lines the
                            scenarios printed, `-repeat <n>` for n passes and whatever moved

Every call may say WHICH instance it addresses: `--instance <dir>` (the instance
directory itself, anywhere in the call) first; then an INSTALLED engine conducts the
instance it lives in; the `PP_HOME` variable serves an engine that has none -- the
product's -- and never redirects an installed one (a script launched under one
instance may run another's console). A directory carrying no instance refuses
`instance-missing`.

The workspace script `pp` forwards here verbatim; eight BARE verbs are the
OPERATOR'S CONSOLE, resolved before any skill name:

  upgrade                -> every pin moves to the source's current version,
                            re-materialized -- the open runs are renewed: each keeps
                            its key and reopens at its next call
  add <package>          -> one more package into this instance, its prerequisites pinned
  remove <package>       -> one package out -- refused while another pin requires it
  repo <name>            -> a sibling workspace, installed and wired like this one
  doctor                 -> repair in place at constant pins -- runs survive
  help | version [-json] -> the console's usage | the source and the pins

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

from conductor import Block, Conductor, Refusal, adapters, instance, rendering   # noqa: E402
from conductor.state import context, lock   # noqa: E402 -- the run a call holds, its lock

BOOT = "BOOT.md"
HOME: Path | None = None            # the instance this call ADDRESSES (`--instance`, `PP_HOME`),
                                    # resolved once at `main`; None = the engine's own location
INSTANCE_DIR = instance.DIRECTORY   # where `install <workspace>` puts the instance; the
                                    # engine's one name for it -- `install.install()` takes
                                    # any target verbatim, this is the console's default

CONSOLE_HELP = """The operator's console -- the workspace script (`./pp`, Windows `.\\pp`):

  ./pp upgrade          every pinned package moves to the source's current
                        version, re-materialized -- the open runs are renewed:
                        each keeps its key and reopens at its next call
  ./pp add <package>    one more package into this instance, its prerequisites pinned
  ./pp remove <package> one package out -- refused while another pin requires it
  ./pp repo <name>      a sibling workspace, installed and wired like this one
  ./pp doctor           repair in place at constant pins -- runs survive
  ./pp acquit <vector>  a treated signal vector stops asking: its counter and
                        its latch fall together
  ./pp version [-json]  the source checkout and the pinned versions; -json: one object
  ./pp help             this text"""

CONSOLE_TAIL = """The rest passes through to the conductor verbatim: `./pp` (where the run
is, read-only), `./pp <key>` (advance), `./pp <key> -s <skill>`, `./pp -test`,
`./pp -reset`. A keyed call holds the run's call lock while it plays: a second call on
the same run waits `call_lock_wait` seconds then refuses `call-busy` (replay it); a
process a call launched that calls its own run back refuses `call-reentrant`. The full
story lives in docs/reference/console.md."""


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


def _home(argv: list[str]) -> tuple[list[str], Path | None]:
    """-> (argv without `--instance <dir>`, the instance addressed): the flag first,
    wherever it stands in the call; None for an INSTALLED engine (its own location
    decides -- a `PP_HOME` inherited from another instance's script never redirects
    it); `PP_HOME` for an engine that has no instance of its own (the product's).
    The variable is read here and nowhere else."""
    from conductor import discovery
    argv, given = ride(argv, "--instance", "an instance directory")
    if given is None and discovery.instance_member(Path(__file__)) is None:
        given = os.environ.get("PP_HOME") or None
    return argv, (Path(given) if given else None)


def _member():
    """-> the member this call works on: the instance addressed, else the one the
    engine is installed in (`engine-uninstalled` when it is not)."""
    from conductor import discovery
    if HOME is not None:
        return discovery.member_at(HOME)
    return discovery.installed_member(Path(__file__))


def _standing():
    """-> the member this call works on, or None when the engine runs uninstalled and
    no instance was addressed -- what the keyless readers ask before composing."""
    from conductor import discovery
    if HOME is not None:
        return discovery.member_at(HOME)
    return discovery.instance_member(Path(__file__))


def _here(run: str | None = None) -> Conductor:
    """The facade on the member this call works on -- the ONE constructor the console
    uses; the engine invoked stays the script (its card, its bench)."""
    return Conductor.here(Path(__file__), run, home=HOME)


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


def _wire(workspace: Path, meta: Path, providers: list[str]) -> int:
    """Runs each named adapter over `workspace` -- the shared tail of every
    install that knows its harnesses. -> how many artifacts were written."""
    wrote = 0
    for name in providers:
        adapter = adapters.load(name, HOME)
        for done in adapter.wire(workspace.resolve(), meta):
            print(f"pp: {done}")
            wrote += 1
    return wrote


def _add(name: str) -> int:
    """One more package into the CURRENT instance -- with the fresh-workspace way
    out when the package's user-level files would replace the operator's own."""
    from conductor import discovery, install
    member = _member()
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
            made = install.install(adapters.product_of(HOME) / "engine" / "pp.py", Path(fresh) / INSTANCE_DIR,
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
        standing = _standing()
        print(_help(standing.meta if standing else None))
        return 0
    member = _member()
    if verb == "version":
        from conductor import VERSION
        if arguments not in ([], ["-json"]):
            raise SystemExit("pp version takes no argument but `-json`")
        machine = instance.borrowed(member.meta)     # a borrower plays its machine's source
        declared = instance.read(machine or member.meta)
        if arguments:
            import json as version_json
            at_source = install.source_version(Path(str(declared.get("source", ""))))
            print(version_json.dumps({"source": declared.get("source"), "machine": str(machine) if machine else None,
                              "engine": VERSION, "at_source": at_source if at_source != VERSION else None,
                              "packages": dict(instance.pins(member.meta))}))
            return 0
        print(f"source {declared.get('source', '?')}")
        if machine is not None:
            print(f"machine {machine}")
        at_source = install.source_version(Path(str(declared.get("source", ""))))
        where = f"`{machine.parent / 'pp'} upgrade`" if machine is not None else "`upgrade`"
        moved = (f" -- the source holds {at_source}; {where} moves you there"
                 if at_source != VERSION else "")
        print(f"engine {VERSION}{moved}")
        for name, version in instance.pins(member.meta).items():
            print(f"{name} {version}")
        return 0
    if verb == "upgrade":
        if arguments and (arguments[0] != "--from" or len(arguments) != 2):
            raise SystemExit("pp upgrade takes no argument but `--from <checkout>`")
        if arguments and instance.borrowed(member.meta) is None:
            checkout = Path(arguments[1]).expanduser().absolute()
            if not (checkout / "engine" / "conductor" / "core" / "version.py").is_file():
                raise Refusal("source-missing", f"`{checkout}` holds no engine -- `--from` names a "
                                                "checkout of the product")
            declared = instance.read(member.meta)
            declared["source"] = str(checkout)     # the source named anew, then followed
            instance.write(member.meta, declared)
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
    packages = [one for one in instance.pins(member.meta) if one != instance.base_of(member.meta)]
    workspace = member.path.parent / arguments[0]
    made = install.install(adapters.product_of(HOME) / "engine" / "pp.py", workspace / member.meta_name,
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
    operator's after; its stderr reaches the caller as the skill writes it, its
    stdout is relayed line by line once it ends, its exit code returned as is. What it says to the bus (`::push`, `::clear`)
    is harvested by the ONE collector on a clean exit; a `::mount` has no run to
    arrive in at the console and refuses by name -- after the skill ran. An entry
    declared `tty: true` hands the skill the terminal instead: the three streams are
    the console's own, nothing is captured nor harvested, its exit code is the answer --
    but `RELAUNCH`, which asks the verb its package's metadata names (`_relaunched`) -- once: a command
    played again after its verb (`PP_RELAUNCHED` set) that asks again gets its code back as is."""
    from conductor import contributions, events, instance
    skill = str(entry["skill"])
    contract = instance.skill_contract(member.meta, skill)
    script = contract.parent / f"{skill}.py" if contract else None
    if script is None or not script.is_file():
        raise Refusal("command-broken",
                      f"`{entry['verb']}` -> `{skill}` -- the manifest of `{entry['package']}` "
                      "declares it, no script answers: `doctor` repairs the instance")
    args = [str(one) for one in (entry.get("args") or [])] + arguments
    if entry.get("tty"):
        # the skill owns the terminal: no stream read back, so no harvest and no
        # mount to judge -- what it prints is the operator's screen
        rc = contributions.run_at_terminal(member.meta, skill, args)
        if rc == contributions.RELAUNCH and not os.environ.get(RELAUNCHED):   # one relaunch per console: a
            # command played again that asks again gets its code back, never a loop
            from conductor.state import metadata
            raise _Relaunch(str(metadata.of_package(member.meta, str(entry["package"])).get("then") or ""))
        return rc
    rc, out, err = contributions.run_skill(member.meta, skill, args, stderr_live=True)
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
    the conductor's own face (`denied`: the deviation, the trace, the seam). Exit 2.
    A stranger -- a name declared nowhere -- is caught here too: the pending block
    answers, never the console's usage."""
    print(conductor.denied(block, name, _mark(conductor)))
    return 2


_ALREADY = "call already done"     # the fact a call over a held output, or a bare one, meets
_HELD_BOUNCE = f"pp: not played -- {_ALREADY}"


def _mark(conductor: Conductor) -> bool:
    """-> whether THIS call carries the principal's mark, read only in a run its principal
    conducts -- in a run the LLM conducts no call after `-new` reads it."""
    return conductor.principal() and context.by_principal()


def _agents_call(key: str) -> bool:
    """-> whether this keyed call is the AGENT's in a run its principal conducts: the run's
    mode says principal and the call carries no mark."""
    return _here(key).principal() and not context.by_principal()


def _moves_nothing(key: str, rest: list[str]) -> bool:
    """-> whether the keyed call `rest` MOVES NOTHING of the run: a view (`-peek`, a switch, a name
    not offered at this step) or a GESTURE (a script called with its arguments, or bare for its
    manual) -- what plays while an output is held or a reading waits, in both modes, because the
    agent loses nothing by playing it. A value, a mount, a door, a re-serve and `-skip` move the run
    or its reading: they wait for the output the agent has not read."""
    if rest[:1] in (["-peek"], ["-disable"], ["-enable"]):
        return True
    if rest[:1] != ["-s"] or len(rest) < 2:
        return False
    base = rest[1].partition("@")[0]
    conductor = _here(key)
    kind, _ = _resolve_skill(conductor.member.meta, base)
    if kind == "script":
        return True
    block = conductor.peek()
    try:
        entry = conductor.route(base) if block is not None else None
    except Refusal:
        return False          # an ambiguous address: the call plays and refuses by its own name
    return entry is None      # a name not offered: the pending block answers, nothing moves


def report(conductor: Conductor, block: Block | None, act: str = "value", lead: str = "") -> int:
    if block:
        # the engine hands over its own text through its one seam: measured and closed
        # under the host's cap, the rest waiting at the run -- or held for the principal's
        # call when the agent's call serves it in a run its principal conducts
        print(conductor.delivered(block, _mark(conductor), act=act, lead=lead))
        return 0
    print("pp: the procedure is complete — nothing more to do.")
    return 0


def conductor_pending(key: str) -> bool:
    """-> whether the run `key` still holds the matter of a cut block."""
    try:
        return _here(key).pending()
    except Refusal:
        return False


def _standing_keys() -> set[str]:
    """-> the keys of every run under way -- the finite set a positional key
    resolves against; a first token in it addresses THAT run."""
    from conductor import persistence
    member = _member()
    return {persistence.run_id_of(slot) for slot in persistence.slots(member.meta)}


def _renewal(key: str) -> dict | None:
    """-> the renewal mark the slot of `key` holds when an upgrade renewed that run, None
    for a run -- read straight off the slot, before any facade is built."""
    from conductor import persistence
    return persistence.renewed(persistence.slot_of(_member().meta, key))


def _call_lease(key: str, launched_by: str | None):
    """The CALL lock of one keyed call: taken before the run's saved state is read, held to
    the call's exit. A second call on the run WAITS for it within `call_lock_wait` seconds,
    then refuses `call-busy` -- exit 2, nothing played, the replay named. A process this
    call launches -- a skill -- inherits `PP_CALL` naming this run; one that calls the run
    back would wait for the lock its parent holds, for ever: it refuses `call-reentrant`
    before any wait. -> the lease, released by `main` whatever the call did."""
    from conductor.state import settings
    member = _member()
    own = f"{member.meta}:{key}"
    if launched_by == own:
        raise Refusal("call-reentrant",
                      f"this process was launched by a call on run {key} of this very instance "
                      f"(`{context.CALL}`) and calls it back -- a skill never calls its own run: "
                      "it prints, pp plays")
    wait = settings.of(member.meta).call_lock_wait
    lease = lock.acquire(lock.call_of(member.meta, key), wait=wait)
    if lease is None:
        raise Refusal("call-busy",
                      f"another call holds run {key} and has not answered within {wait}s "
                      "(`call_lock_wait` at SETTINGS) -- replay your call once it has")
    os.environ[context.CALL] = own
    return lease


MAINTAINS = ("upgrade", "doctor", "add", "remove", "-sync")   # the verbs that rewrite the machine
RELAUNCHED = "PP_RELAUNCHED"      # said to a command played again after the maintenance verb it asked: `<verb> <rc>`


class _Relaunch(Exception):
    """A command at the terminal ended on `RELAUNCH`: the verb its package's metadata names, played once
    this process has left its hold on the machine."""

    def __init__(self, verb: str) -> None:
        super().__init__(verb)
        self.verb = verb


def _guard(argv: list[str]):
    """-> the hold this process takes on its MACHINE for its whole life, before anything
    reads the instance: EXCLUSIVE for a verb that rewrites the machine (`maintaining`,
    `maintenance-busy` while a pp process is active under it), SHARED for every other call
    (`serving`, `maintenance-in-progress` while a maintenance holds it) -- readers
    included; none when the call resolves no instance (the product's engine, bare)."""
    import contextlib
    verb = argv[0] if argv else ""
    if verb == "-install" and "-package" in argv[1:]:
        verb = "add"
    if verb == "-sync" and len(argv) > 1:          # a repair from outside names its instance
        return lock.maintaining(Path(argv[1]).resolve(), verb)
    standing = _standing()
    if standing is None:
        return contextlib.nullcontext()
    if verb in MAINTAINS:
        return lock.maintaining(standing.meta, verb)
    return lock.serving(standing.meta)


def _unknown(word: str) -> str:
    """-> what an unknown word refuses with: where the verbs are listed, and the package of the
    source that declares the word as a command, when one does."""
    from conductor import instance
    hint = ""
    standing = _standing()
    if standing is not None:
        try:
            machine = instance.borrowed(standing.meta) or standing.meta
            source = Path(str(instance.read(machine).get("source", "")))
            for manifest in sorted(source.glob("packages/*/package.yaml")):
                declared = instance.manifest_of(manifest.parent)
                commands = (declared.get("contributes") or {}).get("commands") or []
                if any(isinstance(one, dict) and one.get("verb") == word for one in commands):
                    hint = f"; the package `{declared.get('name')}` declares it -- `./pp add {declared.get('name')}`"
        except Refusal:
            hint = ""
    return (f"`{word}` is no verb of the console, no command of a pinned package and no run's key "
            f"-- `./pp help` lists them{hint}")


def _relaunched(verb: str, asked: list[str]) -> int:
    """The verb a command at the terminal asked, played by this engine on the instance addressed -- the hold on
    the machine left, the maintenance verb takes its own --, then the command played again, told the verb and its
    exit code (`PP_RELAUNCHED`). A verb outside `RELAUNCHES` refuses `relaunch-invalid`, nothing played.
    -> the exit code of the command played again."""
    import subprocess
    from conductor import contributions
    if verb not in contributions.RELAUNCHES:
        refusal = Refusal("relaunch-invalid", f"`{verb or '(none)'}` -- a command at the terminal may ask "
                                              f"{' or '.join(contributions.RELAUNCHES)} alone")
        sys.stderr.write(f"pp: REFUSED — {refusal}\n  nothing played.\n")
        return 2
    addressed = ["--instance", str(HOME)] if HOME is not None else []
    played = subprocess.run([sys.executable, str(Path(__file__).resolve()), *addressed, verb]).returncode
    again = {**os.environ, RELAUNCHED: f"{verb} {played}"}
    return subprocess.run([sys.executable, str(Path(__file__).resolve()), *asked], env=again).returncode


def main(argv: list[str]) -> int:
    # a run is designated by the KEY of the command, never by the shell: whatever the
    # environment inherited is dropped here, and a keyed call names its run again; the
    # call that launched this process is read once -- the reentrance guard -- and dropped
    os.environ.pop("PP_RUN", None)
    launched_by = os.environ.pop(context.CALL, None)
    asked = list(argv)                # the command as typed: what a relaunch plays again
    global HOME
    try:
        argv, HOME = _home(argv)     # the instance addressed, before anything reads one
        try:
            with _guard(argv):       # the machine held for this process's whole life
                code = _dispatch(argv, launched_by)
        except _Relaunch as relaunch:
            return _relaunched(relaunch.verb, asked)
        sys.stdout.flush()           # written NOW: a reader gone is met here, not at the interpreter's exit
        return code
    except Refusal as refusal:
        sys.stderr.write(f"pp: REFUSED — {refusal}\n  nothing played.\n")
        return 2
    except BrokenPipeError:
        # the reader of stdout left before the output was written (`| head -c 0`): the run
        # MOVED -- its state is saved before anything prints -- and the output
        # is lost to the caller alone. Said on stderr, the exit clean: no traceback at the
        # interpreter's last flush
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.stderr.write("pp: the output was lost -- its reader closed before it was written; the run "
                         "played, its pending block stands.\n")
        return 0


def _reset(key: str | None) -> int:
    """`-reset [<key>]`: forgets the runs -- the one named, all otherwise -- each under ITS
    call lock, tried without waiting: a run a call holds refuses `call-busy` and nothing is
    forgotten; a run with no call under way (a chat or a wake-up between two calls) is
    forgotten, and its next call meets `run-unknown`."""
    from conductor import persistence
    member = _member()
    targets = [persistence.slot_of(member.meta, key)] if key else persistence.slots(member.meta)
    leases = []
    try:
        for slot in targets:
            run = persistence.run_id_of(slot)
            lease = lock.try_(lock.call_of(member.meta, run))
            if lease is None:
                raise Refusal("call-busy", f"a call holds run {run} -- `-reset` forgets no run under a "
                              "call: replay once it has answered")
            leases.append(lease)
        dropped = _here(key).forget()
    finally:
        for lease in leases:
            lock.release(lease)
    print(f"pp: {dropped} run(s) forgotten — `-new` opens a fresh one.")
    return 0


_PURGE_USAGE = "pp -purge <key> [<key> ...] | --before <YYYY-MM-DD> [--yes] [-json]"


def _purge(arguments: list[str]) -> int:
    """`-purge`: removes for good what the engine keeps of runs -- each one's slot or renewal
    mark, every `session-<key>.*`, every trace of its key -- the runs named, or every run and
    every trace that names no run last written before `--before`. Without `--yes` it says what it
    would remove and writes nothing. Each run under ITS call lock, tried without waiting: one
    held refuses `call-busy` and nothing is removed."""
    import json as purge_json
    from datetime import datetime, timezone
    from conductor import persistence
    from conductor.state import purge
    as_json, confirmed = "-json" in arguments, "--yes" in arguments
    rest = [one for one in arguments if one not in ("-json", "--yes")]
    before = None
    if "--before" in rest:
        at = rest.index("--before")
        value = rest[at + 1] if at + 1 < len(rest) else ""
        try:
            before = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            raise Refusal("purge-invalid", f"`--before {value}` -- a date is written YYYY-MM-DD")
        del rest[at:at + 2]
    if (before is None) == (not rest) or any(one.startswith("-") for one in rest):
        raise SystemExit(_PURGE_USAGE)
    member = _member()
    keys = list(dict.fromkeys(rest))
    if before is None:
        unknown = [key for key in keys if not purge.files_of(member.meta, key)]
        if unknown:
            raise Refusal("run-unknown", f"`{' '.join(unknown)}` -- no file of this instance "
                          "belongs to that run; nothing removed")
    entries = purge.planned(member.meta, keys, before)
    leases = []
    try:
        for entry in entries:
            if not entry["key"]:
                continue
            path = lock.call_of(member.meta, entry["key"])
            if not confirmed:
                taken = lock.held(path)            # a look: it creates no lock file
            else:
                lease = lock.try_(path)
                taken = lease is None
                if lease is not None:
                    leases.append(lease)
            if taken:
                raise Refusal("call-busy", f"a call holds run {entry['key']} -- `-purge` removes no "
                              "run under a call, and nothing was removed: replay once it has answered")
        if confirmed:
            purge.removed(member.meta, entries)
    finally:
        for lease in leases:
            lock.release(lease)
    files = sum(len(entry["files"]) for entry in entries)
    weight = sum(entry["bytes"] for entry in entries)
    if as_json:
        print(purge_json.dumps({"dry": not confirmed, "runs": [
            {"key": entry["key"], "files": [one.name for one in entry["files"]], "bytes": entry["bytes"]}
            for entry in entries], "files": files, "bytes": weight}, ensure_ascii=False))
        return 0
    head = (f"pp: {len(entries)} run(s) purged -- {files} file(s), {weight} bytes" if confirmed else
            f"pp: -purge would remove {len(entries)} run(s) -- {files} file(s), {weight} bytes")
    lines = [head]
    for entry in entries:
        name = entry["key"] or entry["files"][0].name
        lines.append(f"  {name}  {len(entry['files'])} file(s)  {entry['bytes']} bytes")
    if not confirmed and entries:
        lines.append("  nothing removed -- replay with --yes to remove them")
    print("\n".join(lines))
    return 0


def _dispatch(argv: list[str], launched_by: str | None) -> int:
    conductor = None
    lease = None
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
                                 "[-base <package>] [-claude] [-codex] [-gemini] [-cursor]")
            if argv[1].startswith("-"):
                # the DAY-2 form: no workspace leads -- host flags alone, and the
                # adapters wire the CURRENT instance's workspace (the `-package` motif)
                allowed = tuple(f"-{name}" for name in ("claude", "codex", "gemini", "cursor"))
                strange = [a for a in argv[1:] if a not in allowed]
                if strange:
                    raise Refusal("install-ambiguous",
                                  f"`{' '.join(strange)}` -- the day-2 form takes host "
                                  "flags alone: `-install -claude|-codex|-gemini|-cursor`")
                member = _standing()
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
            rest, base = ride(rest, "-base", "a package name")
            wired = [name for name in ("claude", "codex", "gemini", "cursor")
                     if f"-{name}" in rest]
            if "gemini" in wired:
                import shutil
                if shutil.which("gemini") is None:
                    raise Refusal("gemini-missing",
                                  "`-gemini` needs the gemini CLI on PATH -- the standing "
                                  "rules compose over its baseline")
            packages = [a for a in rest if not a.startswith("-")]
            target = (workspace / INSTANCE_DIR).resolve()
            from conductor import discovery, instance as machines
            borrow = False
            if "-own" not in rest and discovery.instance_member(Path(__file__)) is not None:
                try:                                 # an installed engine: a machine above the
                    machines.machine_of(target)      # target lends it -- borrowed, not copied
                    borrow = True
                except Refusal:
                    borrow = False
            if borrow and (packages or base):
                raise Refusal("install-borrowed",
                              "an instance that borrows a machine plays its composition -- "
                              "packages and `-base` are the machine's (`-own` for a copy of yours)")
            made = install.install(adapters.product_of(HOME) / "engine" / "pp.py", target, packages,
                                   slug=slug, doors=not wired, base=base, borrow=borrow)
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
            from conductor import contributions
            standing = _standing()
            if standing is not None:
                entry = contributions.command(standing.meta, argv[0])
                if entry is not None:
                    return _command(standing, entry, argv[1:])
        if argv and argv[0] == "-test":
            # the bench lives at the PRODUCT checkout (tests/ beside engine/, kit/, packages/):
            # a vendored engine reaches it through the instance's declared source -- and HANDS
            # the call over to the product's own engine, so the conductor the scenarios import
            # and the one they install from are one code; the source engine plays it itself
            product = adapters.product_of(HOME)
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
            from conductor import compiling, install
            from conductor import Member
            if len(argv) > 1:      # repair FROM OUTSIDE: an instance whose own engine is stale
                meta = Path(argv[1]).resolve()
                member = Member(path=meta.parent, name=meta.parent.name, meta_name=meta.name)
            else:
                member = _member()
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
                conductor = _here()
                block = conductor.resume(conductor.boot(BOOT))
                # documentary: the hook feeds the host's PROMPT, not a tool result -- the
                # cap is the tool's (a fact of the host), so the block goes whole here: the
                # one bare render of the engine, on purpose
                text = render(block) if block else ""
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
            # The words after `-new` are the principal's message, joined by a blank
            # (the grammar of `<key> <message>`, at the opening): traced `prompt`
            # before the first block, served by the base that consumes it. An opening
            # holds the machine shared from its entry, as every call does.
            conductor = _here()
            if not context.by_principal():
                # the agent's `-new` under a launcher that conducts a run of this instance
                # (`PP_CONDUCTED_RUN` names it) while that run stands mid-exchange: that
                # agent IS that run's -- softly, nothing opens. Unnamed, the call is another
                # conversation's (an editor beside the post): it opens
                from conductor import persistence
                named = os.environ.get(context.CONDUCTED_RUN, "").strip()
                busy = persistence.under_way(conductor.member.meta) if named else []
                if named in busy:
                    print(f"pp: a run is already open -- {named}")
                    return 0
            return report(conductor, conductor.start(conductor.boot(BOOT), " ".join(argv[1:])))
        if argv and argv[0] == "-reset":
            return _reset(argv[1] if len(argv) > 1 else None)
        if argv and argv[0] == "-purge":
            return _purge(argv[1:])
        if argv and argv[0] in ("-run", "-answer"):
            raise SystemExit("pp: `-run` and `-answer` are gone -- the key leads: "
                             "`./pp <key> [value|-|-s <name> [args]|-peek]`")
        if not argv:
            # keyless = INSPECTION only: shows where the single run stands --
            # never advances anything, never opens a run; the first line says the
            # effort in force -- a display for the operator, the agent owes it no
            # reading (the first call of a conversation is `-new`, always)
            conductor = _here()
            print(f"pp: effort — {conductor.effort() or '—'}")
            mark = conductor.renewal()
            if mark is not None:            # an upgrade renewed the run: said, never reopened here
                print(rendering.renewed(conductor.run_id, mark))
                return 0
            block = conductor.peek()
            if block is None:
                said = rendering.packages(conductor.switch_state())
                if said:
                    print(said)          # the DURABLE state: what SETTINGS switches off
                print("pp: no run is under way -- `-new` opens one.")
                return 0
            print(conductor.delivered(block, _mark(conductor), act="view", view=True))
            return 0
        key = (argv[0] if not argv[0].startswith("-")
               and argv[0] in _standing_keys() else None)
        if key is not None:
            rest = argv[1:]
            if rest[:1] != ["-peek"]:
                # every keyed call but a peek WRITES the run: it holds the run's CALL lock
                # from here to its exit (released at the bottom of this function) and
                # names itself to what it launches -- a peek reads, and takes nothing
                lease = _call_lease(key, launched_by)
            mark = _renewal(key)
            if mark is not None:
                # a RENEWED run: an upgrade left its key, not its state -- a peek says so and
                # writes nothing; any other call reopens the run under its key, on its boot,
                # and what it carried plays only as the message the run waited for
                if rest[:1] == ["-peek"]:
                    print(rendering.renewed(key, mark))
                    return 0
                given = " ".join(rest) if rest and not rest[0].startswith("-") else ""
                if rest == ["-"]:
                    given = sys.stdin.read().strip()
                verb = " ".join(rest) if rest and rest[0].startswith("-") and rest != ["-"] else ""
                conductor = _here(key)
                return report(conductor, conductor.reopen(conductor.boot(BOOT), given, verb),
                              act="reopened")
            if (rest[:1] != ["-compacted"] and conductor_pending(key)
                    and not (rest and _moves_nothing(key, rest))):
                # a block cut under the cap: its next chunk comes BEFORE the flow moves --
                # the bare call serves it; a call that MOVES the run bounces: the fact said
                # first, the chunk served after, nothing lost and nothing recorded. A view or a
                # gesture moves nothing: it plays below, the chunk untouched
                conductor = _here(key)
                if conductor.principal() and not context.by_principal():
                    # the agent's call in a run its principal conducts: the chunk is the
                    # principal's to serve -- a bare call refuses, a value bounces unserved;
                    # the rest of a VIEW is the agent's own, served first
                    if not rest and conductor.viewing():
                        print(conductor.next_view())
                        return 0
                    if not rest:
                        raise Refusal("principal-advances", _ALREADY)
                    print(f"pp: chunk-pending -- `{' '.join(rest)}` was not played")
                    return 0
                if rest == ["-skip"]:
                    print(conductor.drop_pending())
                    return 0
                if rest:
                    print(f"pp: chunk-pending -- `{' '.join(rest)}` was not played")
                print(conductor.next_chunk())
                return 0
            if rest and _agents_call(key) and _here(key).held() and not _moves_nothing(key, rest):
                # ONE output held at a time: the agent has not read it, so nothing that MOVES
                # the run -- a value, a mount, a door, a re-serve -- plays over it; a view or a
                # gesture moves nothing and plays, a gesture's `::mount` joining the held output
                print(_HELD_BOUNCE)
                return 0
            if rest == ["-skip"]:
                print("pp: nothing to skip -- no reading waits")
                return 0
            if rest[:1] == ["-s"]:
                if len(rest) < 2:
                    raise SystemExit("pp -s needs a skill name")
                return _skill(key, rest[1], rest[2:])
            if rest[:1] == ["-open"]:
                if len(rest) != 2:
                    raise SystemExit("pp -open takes one name -- a proc the output offers, "
                                     "opened as a space")
                return _open(key, rest[1])
            if rest[:1] == ["-close"]:
                if len(rest) > 1:
                    raise SystemExit("pp -close takes no other argument -- it leaves the "
                                     "deepest space open")
                conductor = _here(key)
                return report(conductor, conductor.close(), act="closed")
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
                conductor = _here(key)
                return report(conductor, conductor.compacted(), act="compacted")
            if rest[:1] in (["-disable"], ["-enable"]):
                # the SOFT switch: the operator's word, said to the agent and written at
                # the run -- one package out of the play (its dependents with it) or back
                # in, and the block that stands comes back; the run never moves
                if len(rest) != 2:
                    raise SystemExit(f"pp {rest[0]} takes one package name -- "
                                     "the durable switch is `package.<name>: on|off` at SETTINGS")
                conductor = _here(key)
                print(conductor.switch(rest[1], rest[0] == "-disable", _mark(conductor)))
                return 0
            if rest[:1] == ["-peek"]:
                conductor = _here(key)
                block = conductor.peek()
                if block is None:
                    return 0
                # `-peek <name>` asks the same reader as a call would: the offer map
                # of the current output, never the block's own list
                if len(rest) > 1 and conductor.route(rest[1]) is None:
                    return denied(conductor, block, rest[1])
                print(conductor.delivered(block, _mark(conductor), act="view", view=True))
                return 0
            if rest[:1] == ["-mount"]:
                # the HOSTING verb: documents named by their ADDRESS enter the current
                # view until the exchange ends -- bare addresses take the defaults
                # (constraints+tools); ONE JSON array picks per document
                if len(rest) < 2:
                    raise SystemExit(
                        "pp -mount takes documents by their address (a name, a path in the "
                        "instance, `<package>:<path>`), or one JSON array of "
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
                conductor = _here(key)
                print(conductor.mount(entries, by_principal=_mark(conductor)))
                return 0
            given = " ".join(rest)
            if given == "-":
                given = sys.stdin.read().strip()
            conductor = _here(key)
            if not conductor.principal():
                return report(conductor, conductor.forward(given))
            # a run its principal conducts: the console tells the callers apart by the
            # mark and hands the answer to the facade -- the one judge serves both
            if context.by_principal():
                if conductor.held():
                    if rest:
                        raise Refusal("output-held", "an answer waits its principal's bare "
                                      "call -- it is served first")
                    print(conductor.release())
                    return 0
                return report(conductor, conductor.forward(given, by_principal=True))
            if not rest:
                if conductor.viewing():
                    # the rest of a view the agent was answered: its bare keyed call alone
                    # serves it, chunk by chunk -- nothing of the run moves
                    print(conductor.next_view())
                    return 0
                raise Refusal("principal-advances", _ALREADY)
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
            from conductor import instance
            from conductor.state import traces
            member = _member()
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
            where = ""
            if key is not None and not found:
                # a key the instance does not hold may be a run of an instance under it
                for borrower in instance.borrowers(member.meta):
                    found = traces.runs(borrower / instance.STATE, days=days, key=key)
                    if found:
                        where = borrower.parent.relative_to(member.meta.parent).as_posix()
                        break
                if not found:
                    raise Refusal("run-unknown", f"`{key}` -- no run of this instance nor of the "
                                                 "instances under it holds that key; `./pp -stats` "
                                                 "lists the runs here with their keys")
            if where and not as_json:
                print(f"pp: run {key} lives at {where}")
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
            from conductor import instance
            from conductor.state import log
            member = _member()
            state = member.meta / instance.STATE
            traced = sorted(state.glob("session-*.jsonl"), key=lambda p: p.stat().st_mtime)
            if not traced:
                raise Refusal("no-run", "no run trace to stamp -- `-new` opens a run")
            log.record(traced[-1], "turn-end")
            print(f"pp: turn-end -- {traced[-1].name}")
            return 0
        if argv[0] == "-peek":
            conductor = _here()
            block = conductor.peek()
            if block is None:
                return 0
            if len(argv) > 1 and conductor.route(argv[1]) is None:
                return denied(conductor, block, argv[1])
            print(conductor.delivered(block, _mark(conductor), act="view", view=True))
            return 0
        if not argv[0].startswith("-") and re.fullmatch(r"[0-9a-f]{6}", argv[0]):
            raise Refusal("run-unknown",
                          f"`{argv[0]}` -- no run holds that key; your "
                          "conversation's key was handed at `-new`")
        raise Refusal("verb-unknown", _unknown(argv[0]))
    except Refusal as refusal:
        if conductor is not None:      # best-effort: a refusal with no run resolved has no home
            conductor.noted(refusal)
        sys.stderr.write(f"pp: REFUSED — {refusal}\n  nothing played.\n")
        return 2
    finally:
        if lease is not None:
            lock.release(lease)


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
    from conductor import contributions
    buffer = io.StringIO()
    rc = 1
    # the script is LOADED here, so it reads its instance the way a launched one does --
    # `PP_HOME` named for the call, and taken back after
    spot = os.environ.get("PP_HOME")
    try:
        os.environ["PP_HOME"] = contributions.launched_environment(runner.member.meta)["PP_HOME"]
        with contextlib.redirect_stdout(buffer):
            rc = contributions.module_at(where).main(arguments) or 0
    finally:
        if spot is None:
            os.environ.pop("PP_HOME", None)
        else:
            os.environ["PP_HOME"] = spot
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
        print(runner.mount(entries, lead=shown if rank == 0 else "",
                           by_principal=_mark(runner)))
    for source, signal in events.gesture_signals(runner.member.meta, base):
        runner._signal(source, signal, evidence=" ".join(arguments))
    return rc


def _open(run: str, name: str) -> int:
    """The `-open` call: the agent opens a SPACE on a name the current output offers -- the
    same reader as `-s`, the single owner routes, several refuse by name, `name@<n>` says
    which -- and that resolves to a proc of the instance; anything else refuses
    `open-unplayable`. The space stacks over the pending step and becomes the root."""
    conductor = None
    try:
        base, sep, tail = name.partition("@")
        if sep and not tail.isdigit():
            raise Refusal("address-invalid",
                          f"`{name}` -- what follows `@` is the segment number: `-open {base}@<n>`")
        conductor = _here(run)
        block = conductor.peek()
        if block is None:
            raise Refusal("no-run", "no run is under way -- call `-new` first")
        entry = conductor.route(base, int(tail)) if sep else conductor.route(base)
        if entry is None:
            return denied(conductor, block, name)
        kind, _ = _resolve_skill(conductor.member.meta, base)
        if kind != "proc":
            raise Refusal("open-unplayable", f"`{base}` is no proc of this instance -- a space "
                                             "opens on the steps of a proc")
        player = _here(run)
        return report(player, player.open(base, route=entry), act="door")
    except Refusal as refusal:
        if conductor is not None:
            conductor.noted(refusal)
        sys.stderr.write(f"pp: REFUSED — {refusal}\n  nothing played.\n")
        return 2


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
        conductor = _here(run)
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
            player = _here(run)   # the peeked one is dry-tainted
            lead = (f"pp: argument ignored: {' '.join(arguments)} -- a proc opens on its own "
                    "documents and reads nothing from the call" if arguments else "")
            return report(player, player.play(base, route=entry, arguments=tuple(arguments)),
                          act="door", lead=lead)
        if kind == "script":
            # a GESTURE, never a step: the call plays the script and the run stays
            # exactly where it stood -- position, pending block and offer map all
            # untouched. What it renders is the anchor line (a fused output only),
            # then the skill's own output; the skill's guard refuses by name.
            runner = _here(run)
            if not arguments:
                runner.gesture_trace(base, entry or {})
                # called BARE, a script does not run: its contract is its MANUAL,
                # mounted body alone into the current view through the one reader --
                # cut at the cap, proven by its hash, in the ledger, swept with the
                # exchange; the standing block renders under it, the run untouched. The
                # skill's NAME is the manual's address, wherever its bundle lives
                print(runner.mount([{"doc": base, "body": True,
                                     "constraints": False, "tools": False}],
                                   by_principal=_mark(runner), act="manual"))
                return 0
            return _played(runner, where, arguments, base, entry,
                           rendering.head(block), runner.anchor_line(entry))
        if kind == "offer" and where is not None:
            from conductor import compiling
            if not compiling.conductible(where):
                # the skill IS a CALL: its constraints enter force with its frame,
                # its body is the brief, an implicit INFER carries the work -- the
                # close resumes the flow (`proc:` present plays the declared one)
                player = _here(run)
                return report(player, player.play(base, route=entry), act="door")
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
