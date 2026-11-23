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
  <key> -print <DOC> -   -> hand a production said to the principal, piped on stdin: the
                            one a step of <DOC> asked on `terminal` -- kept as handed,
                            answered by one line, or by the next block when it was the last due
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
  <key> -skip            -> DROP the rest of a reading cut under the cap: what waits
                            before the first step, and the head of every segment
                            after it -- its heading, its readings, its offers, its
                            laws --, is never served and stays unproven; the steps
                            that wait come next, each with what it reads, cut under
                            the cap, then the closing
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
                            workspace or absolute), kept at the run: a serve row that
                            names no tree reads it when it holds the file, the
                            repository otherwise. A document declares a tree in a
                            `materials:` block,
                            one line `<name>: <path>` each: the nearest document that
                            declares a name wins, and a relative path is read from
                            that document's folder. A row names one by `@<name>`, a
                            document by `material: <name>`; such a row is read from
                            that tree alone: when it cannot answer, the block says
                            `(not served: ...)` in its place, never another tree.
                            A tree called `repo` or `work` refuses `material-invalid`.
                            A launcher may give the run one more ROOT of documents: `PP_DOCUMENTS=<absolute
                            directory>`, kept at the run -- for that run alone its
                            documents resolve, declare (`attach:`, `mount:`) and overlay
                            between the instance's directory and the packages', at every
                            later call and through an upgrade's renewal; a path that is
                            not an absolute directory refuses `documents-unknown`, a
                            keyed call naming another root `documents-fixed`, nothing
                            played. A launcher may give the run its COMPOSITION:
                            `PP_PACKAGES=<name>=on|off[,<name>=on|off…]`, read by `-new`
                            alone, judged before anything is written (`packages-invalid`
                            for the form, `package-base`, `package-unpinned`) and kept
                            at the run as its own switches, in the play before its first
                            block is composed -- a switch of the run beats
                            `package.<name>` of SETTINGS, `-enable` and `-disable` write
                            the same switches, and a keyed call under the variable
                            ignores it. Every run is conducted by its principal --
                            an output that owes no call carries no closing, a chunk
                            ends on its matter. The launcher names the run to the
                            harness it launches (`PP_CONDUCTED_RUN=<key>`), never on
                            its own calls: a keyed call that carries it on that run
                            is the agent's, any other the principal's. The agent's bare call refuses
                            `principal-advances`; its value is judged as in any run,
                            and every block a call of the agent renders -- the step
                            after its value, a mount, a manual, a routed skill, a
                            re-serve, a switch's block, a peek, a denied offer -- is
                            HELD at the run: the agent gets what the act answers and
                            one line that names its act and says to hand back
                            (`pp: value judged — hand back`, `pp: mounted — hand back`...); the
                            principal's bare call serves the
                            held output (cut under the cap as any output), else
                            advances; a principal's call with a text while an output is
                            held refuses `output-held`; any call of the agent while
                            one is held bounces, nothing played. With
                            `PP_HOLD_OUTPUT=true` on the principal's call, an exchange
                            plays in three moves. The call that carries the
                            message -- an opening, or `<key> "<message>"` --
                            opens the exchange and renders no block: it prints
                            the output's heading and one line (`pp: exchange opened — your bare call plays it`).
                            Each mount played next (`-s <script> mount`) is
                            posed: its laws and its offers are in force, what
                            it serves waits at the run, and the call prints one
                            line (`pp: mounted — your bare call serves it`). The script is named alone, with
                            no `@<n>`: it plays when the root of the exchange
                            offers it, and what it prints answers the call and
                            goes into no output. The principal's bare call then
                            plays the exchange and renders ONE output, once:
                            what the mounts serve stands before its first step,
                            and every step carries the laws then in force. On a
                            run that stands on a step, the message opens
                            nothing more and the bare call renders that step.
                            While an exchange the message opened is not played,
                            a door (`-s <name>`) or a space (`-open <name>`) is
                            denied like a name no step offers, with or without
                            `@<n>`: no frame stacks before the bare call.
                            When an output that closed already waits at the
                            run, a mount under the flag joins it as any held
                            output does: nothing is held open, and the line is
                            the act's own (`pp: mounted — your bare call serves it`). A `-new` that names the
                            run (`PP_CONDUCTED_RUN`) while it is mid-exchange
                            opens nothing and says so.
  -install <workspace> [pkg ..] [-slug <slug>] [-base <package>] [-own] [-claude] [-codex] [-gemini] [-cursor]
                         -> seed `<workspace>/.pp`; `-base` names the package the instance
                            is built on (the kit by default -- `base:` at instance.yaml);
                            played by an installed engine, a workspace under an instance
                            that carries a machine BORROWS it (no engine, no vendor, no
                            pins of its own: the machine's versions and composition) --
                            `-own` gives it a copy of the machine instead;
                            each host flag wires its full
                            adapter (card, standing rules, permissions);
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

The workspace script `pp` forwards here verbatim; nine BARE verbs are the
OPERATOR'S CONSOLE, resolved before any skill name:

  upgrade                -> every pin moves to the source's current version,
                            re-materialized -- the open runs are renewed: each keeps
                            its key and reopens at its next call; a package the
                            source no longer carries is unpinned, its records and
                            settings kept
  add <package>          -> one more package into this instance, its prerequisites pinned
  remove <package>       -> one package out -- refused while another pin requires it
  develop <package> [off] -> a package of the house played from its sources, no copy:
                            a file changed plays at the next call that reads it; `off`
                            copies it back at its version (`develop-product`: a
                            package of the product)
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
from conductor import reading, render   # noqa: E402 -- the piped production; the block's text, the console's to print

from conductor import Block, Conductor, Refusal, adapters, console_command, instance, rendering   # noqa: E402
from conductor.core import messages   # noqa: E402 -- every line the console says
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
                        each keeps its key and reopens at its next call; a
                        package the source no longer carries is unpinned, its
                        records and settings kept
  ./pp add <package>    one more package into this instance, its prerequisites pinned
  ./pp remove <package> one package out -- refused while another pin requires it
  ./pp develop <package> [off]
                        a package of the house played from its own folder, no
                        copy: a file you change plays at the next call that reads
                        it; `off` copies it back at its version
  ./pp repo <name>      a sibling workspace, installed and wired like this one
  ./pp doctor           repair in place at constant pins -- runs survive
  ./pp acquit <vector>  a treated signal vector stops asking: its counter and
                        its latch fall together
  ./pp version [-json]  the source checkout and the pinned versions; -json: one object
  ./pp records list|read|count|search
                        read this instance's records without opening .sys/,
                        never writing: filtered, a page at most
                        records_read_limit long and short enough for one tool
                        result, that names the call for the next one;
                        --json: one object
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
        raise Refusal("flag-usage", messages.usage_flag(flag, what))
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
                      messages.refusal_skill_ambiguous(name))
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
            print(messages.maintenance(done))
            wrote += 1
    return wrote


def _add(name: str) -> int:
    """One more package into the CURRENT instance -- with the fresh-workspace way
    out when the package's user-level files would replace the operator's own."""
    from conductor import discovery, install
    member = _member()
    clashes = install.user_clashes(member.meta, name)
    if clashes:
        print(messages.user_level(name, clashes))
        fresh = ""
        if sys.stdin.isatty():
            fresh = input(messages.fresh_workspace()).strip()
        if fresh:
            providers = install.wired_providers(member.path)
            made = install.install(adapters.product_of(HOME) / "engine" / "pp.py", Path(fresh) / INSTANCE_DIR,
                                   [name])
            print(messages.installed_at(made))
            _wire(Path(fresh), made, providers)
            return 0
    made = install.add_package(member, name)
    print(messages.package_installed(name, made))
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
            raise Refusal("version-usage", messages.usage_version())
        machine = instance.borrowed(member.meta)     # a borrower plays its machine's source
        declared = instance.read(machine or member.meta)
        if arguments:
            import json as version_json
            at_source = install.source_version(Path(str(declared.get("source", ""))))
            print(version_json.dumps({"source": declared.get("source"), "machine": str(machine) if machine else None,
                              "engine": VERSION, "at_source": at_source if at_source != VERSION else None,
                              "packages": dict(instance.pins(member.meta))}))
            return 0
        print(messages.version_source(declared.get('source', '?')))
        if machine is not None:
            print(messages.version_machine(machine))
        at_source = install.source_version(Path(str(declared.get("source", ""))))
        where = f"`{machine.parent / 'pp'} upgrade`" if machine is not None else "`upgrade`"
        moved = messages.version_moved(at_source, where) if at_source != VERSION else ""
        print(messages.version_engine(VERSION, moved))
        for name, version in instance.pins(member.meta).items():
            print(messages.version_pin(name, version))
        return 0
    if verb == "upgrade":
        if arguments and (arguments[0] != "--from" or len(arguments) != 2):
            raise Refusal("upgrade-usage", messages.usage_upgrade())
        if arguments and instance.borrowed(member.meta) is None:
            checkout = Path(arguments[1]).expanduser().absolute()
            if not (checkout / "engine" / "conductor" / "core" / "version.py").is_file():
                raise Refusal("source-missing", messages.refusal_source_missing(checkout))
            declared = instance.read(member.meta)
            declared["source"] = str(checkout)     # the source named anew, then followed
            instance.write(member.meta, declared)
        told = install.upgrade(member)
        if not told:
            print(messages.already_current())
            return 0
        for line in told:
            print(messages.maintenance(line))
        return 0
    if verb == "acquit":
        if len(arguments) != 1:
            raise Refusal("acquit-usage", messages.usage_acquit())
        from conductor import events
        fell = events.acquit(member.meta, arguments[0])
        print(messages.acquitted(arguments[0], fell))
        return 0
    if verb == "doctor":
        if arguments:
            raise Refusal("doctor-usage", messages.usage_doctor())
        from conductor import compiling
        for line in install.doctor(member):
            print(messages.maintenance(line))
        for warning in compiling.lint(member.meta):
            print(messages.warning(warning))
        return 0
    if verb == "add":
        if len(arguments) != 1:
            raise Refusal("add-usage", messages.usage_add())
        return _add(arguments[0])
    if verb == "develop":
        if len(arguments) not in (1, 2) or arguments[1:] not in ([], ["off"]):
            raise Refusal("develop-usage", messages.usage_develop())
        for line in install.develop(member, arguments[0], on=arguments[1:] != ["off"]):
            print(messages.maintenance(line))
        return 0
    if verb == "remove":
        if len(arguments) != 1:
            raise Refusal("remove-usage", messages.usage_remove())
        for line in install.remove_package(member, arguments[0]):
            print(messages.maintenance(line))
        return 0
    if verb == "records":
        return _records(member.meta, arguments)
    if len(arguments) != 1:
        raise Refusal("repo-usage", messages.usage_repo())
    providers = install.wired_providers(member.path)
    packages = [one for one in instance.pins(member.meta) if one != instance.base_of(member.meta)]
    workspace = member.path.parent / arguments[0]
    made = install.install(adapters.product_of(HOME) / "engine" / "pp.py", workspace / member.meta_name,
                           packages)
    print(messages.installed_at(made))
    if providers:
        _wire(workspace, made, providers)
    else:
        print(messages.no_harness(made.parent, console_command()))
    return 0


RECORDS_VERBS = ("list", "read", "count", "search")
RECORDS_VALUED = ("--since", "--until", "--key", "--prefix", "--where", "--match", "--order",
                  "--after", "--before", "--last", "--group", "--records")
RECORDS_CURSOR = ("--after", "--before")
EXCERPT = 160            # the characters of a body a table shows, around the text searched


def _records(meta: Path, arguments: list[str]) -> int:
    """`./pp records list|read|count|search` -- the records of the instance READ through the
    store's common query, never written: the options are the query's filters, the output a
    table or one JSON object (`--json`), held under the host's cap (`harness_cap`, written
    `max_harness_tool_output` at SETTINGS) -- a page that would not fit shrinks from its far
    end and names the call that reads the rest."""
    import json
    from conductor import settings, store
    if not arguments or arguments[0] not in RECORDS_VERBS:
        raise Refusal("records-usage", messages.usage_records())
    verb, rest = arguments[0], arguments[1:]
    named, options, cursorless, flags = [], {}, [], set()
    index = 0
    while index < len(rest):
        token = rest[index]
        if token == "--json":
            flags.add(token)
        elif token in RECORDS_VALUED and index + 1 < len(rest):
            value = rest[index + 1]
            if token == "--where":
                options.setdefault(token, []).append(value)
            elif token in options:
                raise Refusal("records-usage", messages.usage_records())
            else:
                options[token] = value
            if token not in RECORDS_CURSOR:
                cursorless += [token, value]
            index += 1
        elif token.startswith("--") or named:
            raise Refusal("records-usage", messages.usage_records())
        else:
            named.append(token)
        index += 1
    allowed = {"list": (), "count": tuple(one for one in RECORDS_VALUED if one not in RECORDS_CURSOR + ("--records",)),
               "read": tuple(one for one in RECORDS_VALUED if one not in ("--group", "--records")),
               "search": tuple(one for one in RECORDS_VALUED if one not in ("--match", "--group"))}[verb]
    if (verb == "list") == bool(named) or any(one not in allowed for one in options):
        raise Refusal("records-usage", messages.usage_records())
    as_json = "--json" in flags
    desc = options.get("--order", "asc" if "--after" in options else "desc") != "asc"
    kept = store.of(meta, readonly=True)
    cap = settings.of(meta).harness_cap - 1           # the newline print adds
    if verb == "list":
        rows = kept.summary()
        if as_json:
            print(json.dumps({"rows": rows, "total": len(rows)}, ensure_ascii=False))
        else:
            print(_table(("record", "total", "first", "last"),
                         [(one["record"], one["total"], one["first"], one["last"]) for one in rows]))
        return 0
    query = _records_query(options)
    if verb == "count" and "--group" in options:
        query["group"] = options["--group"]
    store.judge(**query, **({"match": named[0]} if verb == "search" else {}),
                counting=verb == "count")                                         # before any name is read
    if verb == "search":
        names = [one for one in str(options.get("--records", "")).split(",") if one]
        known = kept.records()
        for name in names:
            if name not in known:
                raise Refusal("record-unknown", messages.refusal_record_unknown(name))
        pages = kept.search(named[0], records=names or None, **query)
        base = [console_command(), "records", "search", named[0]] + _without(cursorless, "--records") + list(flags)
        print(_records_fitted(pages, named[0], base, as_json, cap, desc, searched=True))
        return 0
    record = named[0]
    if record not in kept.records():
        raise Refusal("record-unknown", messages.refusal_record_unknown(record))
    if verb == "count":
        counted = kept.count(record, **query)
        if isinstance(counted, int):
            print(json.dumps({"record": record, "total": counted}) if as_json
                  else counted)
            return 0
        print(_groups_fitted(record, options["--group"], counted, as_json, cap, desc))
        return 0
    page = kept.read(record, **query)
    base = [console_command(), "records", "read", record] + cursorless + list(flags)
    print(_records_fitted({record: page}, query.get("match"), base, as_json, cap, desc))
    return 0


def _records_query(options: dict) -> dict:
    """-> the store's filters from the console's options -- a number where one is due, the
    value as said otherwise: the store judges them all (`filter-invalid`)."""
    import json
    query = {}
    for option, name in (("--since", "since"), ("--until", "until"), ("--key", "key"), ("--prefix", "prefix"),
                         ("--match", "match"), ("--order", "order")):
        if option in options:
            query[name] = options[option]
    for option, name in (("--after", "after"), ("--before", "before"), ("--last", "last")):
        if option in options:
            said = options[option]
            query[name] = int(said) if said.isdigit() else said
    if "--where" in options:
        where = {}
        for pair in options["--where"]:
            field, sep, value = pair.partition("=")
            if not sep:
                raise Refusal("filter-invalid", messages.refusal_where_malformed(pair))
            try:
                where[field] = json.loads(value)
            except ValueError:
                where[field] = value
            if isinstance(where[field], (dict, list)):
                where[field] = value
        query["where"] = where
    return query


def _without(said: list[str], option: str) -> list[str]:
    """-> the option tokens `said` without `option` and its value."""
    out = []
    for at in range(0, len(said), 2):
        if said[at] != option:
            out += said[at:at + 2]
    return out


def _records_fitted(pages: dict, match, base: list[str], as_json: bool, cap: int, desc: bool,
                    searched: bool = False) -> str:
    """-> the pages rendered under `cap`, MEASURED: rendered, measured, and again until the output
    fits -- first the page that shows the most entries gives up the one at its far end, its
    cursor following; when every page is down to one entry, the bodies are cut to a budget halved
    at each round, and say so; then, the bodies cut to nothing, the entries leave. Escapes and
    quotes count, since the output is measured as it is written."""
    import json
    import shlex
    shown = {name: list(page.rows) for name, page in pages.items()}

    def cursor(name):
        rows, page = shown[name], pages[name]
        if len(rows) == len(page.rows):
            return page.next
        if not rows:
            return {"before": page.rows[-1].seq + 1} if desc else {"after": page.rows[0].seq - 1}
        return {"before": rows[0].seq} if desc else {"after": rows[-1].seq}

    def call(name):
        following = cursor(name)
        if following is None:
            return None
        (which, seq), = following.items()
        words = base + [f"--{which}", str(seq)] + (["--records", name] if searched else [])
        return " ".join(shlex.quote(one) for one in words)

    def rendered(budget: int | None) -> str:
        if as_json:
            said = {}
            for name, page in pages.items():
                rows = [{"seq": one.seq, "at": one.at, "key": one.key,
                         "body": one.body if budget is None else _cut(one.body, budget)}
                        | ({} if budget is None else {"cut": True}) for one in shown[name]]
                said[name] = {"rows": rows, "total": page.total, "bound": page.bound, "shown": len(rows),
                              "next": cursor(name), "call": call(name)}
            if searched:
                return json.dumps({"text": match, "pages": said}, ensure_ascii=False)
            (only,) = said.values()
            return json.dumps({"record": next(iter(said))} | only, ensure_ascii=False)
        parts = []
        width = EXCERPT if budget is None else min(EXCERPT, budget)
        for name, page in pages.items():
            if searched and not page.total:
                continue
            table = _table(("seq", "at", "key", "body"),
                           [(one.seq, one.at, one.key or "", _excerpt(one.body, match, width))
                            for one in shown[name]])
            said = messages.records_shown(len(shown[name]), page.total, page.bound, call(name))
            parts.append((f"{name}\n\n" if searched else "") + table + "\n\n" + said
                         + ("" if budget is None else f"\n{messages.records_cut()}"))
        return "\n\n".join(parts) or messages.records_shown(0, 0, 0, None)

    budget = None
    text = rendered(budget)
    while cap > 0 and len(text) > cap:
        widest = max(shown, key=lambda one: len(shown[one]))
        if len(shown[widest]) > 1:
            shown[widest] = shown[widest][1:] if desc else shown[widest][:-1]
        elif budget is None or budget > 0:
            many = max(1, sum(len(rows) for rows in shown.values()))
            budget = cap // (2 * many) if budget is None else budget // 2
        elif shown[widest]:
            shown[widest] = []
        else:
            break
        text = rendered(budget)
    return text


def _groups_fitted(record: str, group: str, counted, as_json: bool, cap: int, desc: bool) -> str:
    """-> a page of groups rendered under `cap`, MEASURED like the pages of entries: each value an
    excerpt of `EXCERPT` characters, the groups at the far end given up until it fits."""
    import json
    rows = [(_clip(value), count) for value, count in counted.rows]
    far_first = group == "day" and desc            # by day the newest page: the oldest day is the far end

    def rendered() -> str:
        if as_json:
            return json.dumps({"record": record, "group": group, "rows": [list(one) for one in rows],
                               "total": counted.total, "bound": counted.bound, "shown": len(rows)},
                              ensure_ascii=False)
        return (_table((group, "count"), rows) + "\n\n"
                + messages.records_shown(len(rows), counted.total, counted.bound, None))

    text = rendered()
    while cap > 0 and len(text) > cap and rows:
        rows = rows[1:] if far_first else rows[:-1]
        text = rendered()
    return text


def _clip(value):
    """-> a group's value as shown: a text longer than `EXCERPT` cut to it."""
    if isinstance(value, str) and len(value) > EXCERPT:
        return value[:EXCERPT] + "…"
    return value


def _cut(body, budget: int) -> str:
    """-> a body cut to `budget` characters of its JSON text."""
    import json
    return json.dumps(body, ensure_ascii=False)[:max(0, budget)]


def _excerpt(body, match, width: int = EXCERPT) -> str:
    """-> `width` characters of a body, centred on the first word searched, one line, no pipe."""
    import json
    text = " ".join(json.dumps(body, ensure_ascii=False).split())
    at = 0
    if match:
        word = str(match).strip().strip('"').split()[0].lower() if str(match).strip().strip('"') else ""
        found = text.lower().find(word) if word else -1
        at = max(0, found - width // 2) if found >= 0 else 0
    piece = text[at:at + width]
    return ("…" if at else "") + piece.replace("|", "\\|") + ("…" if at + width < len(text) else "")


def _table(columns, rows) -> str:
    """-> a markdown table, its cells one line each."""
    def cell(value) -> str:
        return " ".join(str("" if value is None else value).split()).replace("|", "\\|")
    lines = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    lines += ["| " + " | ".join(cell(one) for one in row) + " |" for row in rows]
    return "\n".join(lines)


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
                      messages.refusal_command_broken(entry['verb'], skill, entry['package']))
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
                          messages.refusal_mount_without_run(entry['verb']))
        sys.stderr.write(messages.refused(refusal.code, refusal.detail, messages.MOUNT_UNPLAYED))
        return 2
    return rc


def denied(conductor: Conductor, block: Block, name: str) -> int:
    """The out-of-turn catch: the pending block answers, the ask named as not played --
    the conductor's own face (`denied`: the deviation, the trace, the seam). Exit 2.
    A stranger -- a name declared nowhere -- is caught here too: the pending block
    answers, never the console's usage."""
    print(conductor.denied(block, name, _agents(conductor)))
    return 2




def _agents(conductor: Conductor) -> bool:
    """-> whether THIS call is the AGENT's on the conductor's run (`context.agents`)."""
    return context.agents(conductor.resolved())


def _holds(conductor: Conductor) -> bool:
    """-> whether this call is the principal's and asks its output HELD OPEN at the run
    (`PP_HOLD_OUTPUT=true`): an opening, a message, a mount."""
    return not _agents(conductor) and context.holding()


def _opens(key: str, rest: list[str]) -> bool:
    """-> whether the keyed call `rest` is the principal's MESSAGE under an output it holds open:
    words that name no verb, on the principal's call under `PP_HOLD_OUTPUT=true`. Such a call opens the
    exchange and renders nothing, whatever waits at the run."""
    return bool(rest) and not rest[0].startswith("-") and _holds(_here(key))


def _agents_call(key: str) -> bool:
    """-> whether this keyed call is the AGENT's: it names the run its launcher conducts."""
    return context.agents(key)


def _moves_nothing(key: str, rest: list[str]) -> bool:
    """-> whether the keyed call `rest` MOVES NOTHING of the run: a view (`-peek`, a switch, a name
    not offered at this step) or a GESTURE (a script called with its arguments, or bare for its
    manual) -- what plays while an output is HELD, because the agent loses nothing by playing it.
    A value, a mount, a door, a re-serve and `-skip` move the run or its reading: they wait for the
    output the agent has not read. Over a CUT output `-peek` alone plays."""
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


def report(conductor: Conductor, block: Block | None, act: str = "value", lead: str = "",
           gesture: bool = False) -> int:
    if block:
        # the engine hands over its own text through its one seam: measured and closed
        # under the host's cap, the rest waiting at the run -- or held for the principal's
        # call when the agent's call serves it, or when the principal's GESTURE moved the
        # run between two exchanges
        caught = conductor.caught()    # a print missed: the block that stands answers, as a view
        print(conductor.delivered(block, _agents(conductor), act="denied" if caught else act, lead=lead,
                                  view=caught, gesture=gesture and not caught))
        return 0
    if conductor.said_open():
        # an exchange opened under an output its principal holds open: the heading, the act's line
        print(conductor.said_open())
        return 0
    print(messages.complete())
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
                      messages.refusal_call_reentrant(key, context.CALL))
    wait = settings.of(member.meta).call_lock_wait
    lease = lock.acquire(lock.call_of(member.meta, key), wait=wait)
    if lease is None:
        raise Refusal("call-busy",
                      messages.refusal_call_busy(key, wait))
    os.environ[context.CALL] = own
    return lease


MAINTAINS = ("upgrade", "doctor", "add", "remove", "develop", "-sync")   # the verbs that rewrite the machine
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
                    hint = messages.verb_hint(declared.get('name'))
        except Refusal:
            hint = ""
    return messages.refusal_verb_unknown_word(word, hint)


def _relaunched(verb: str, asked: list[str]) -> int:
    """The verb a command at the terminal asked, played by this engine on the instance addressed -- the hold on
    the machine left, the maintenance verb takes its own --, then the command played again, told the verb and its
    exit code (`PP_RELAUNCHED`). A verb outside `RELAUNCHES` refuses `relaunch-invalid`, nothing played.
    -> the exit code of the command played again."""
    import subprocess
    from conductor import contributions
    if verb not in contributions.RELAUNCHES:
        refusal = Refusal("relaunch-invalid", messages.refusal_relaunch_invalid(verb or '(none)', ' or '.join(contributions.RELAUNCHES)))
        sys.stderr.write(messages.refused(refusal.code, refusal.detail))
        return 2
    addressed = ["--instance", str(HOME)] if HOME is not None else []
    played = subprocess.run([sys.executable, str(Path(__file__).resolve()), *addressed, verb]).returncode
    again = {**os.environ, RELAUNCHED: f"{verb} {played}"}
    return subprocess.run([sys.executable, str(Path(__file__).resolve()), *asked], env=again).returncode


CMDLINE = "PP_CMDLINE"              # cmd.exe's raw command line, set by `pp.cmd`: `%*` stops at a newline
CONSOLE_TOKENS = ("pp.cmd", "pp")    # the command `cmd.exe /c` runs when it runs the console


def windows_argv(line: str) -> list[str]:
    """-> the arguments of a Windows command line by the rules of `CommandLineToArgvW`, in pure Python: the first
    one, the program, up to the next quote when it opens on one, else up to a blank; then each argument up to a blank
    outside quotes -- 2n backslashes before a quote are n and the quote opens or closes, 2n+1 are n and a literal
    quote, a third consecutive quote is literal; a newline is no blank."""
    found: list[str] = []
    if line.startswith('"'):
        end = line.find('"', 1)
        end = len(line) if end < 0 else end
        found.append(line[1:end])
        at = end + 1
    else:
        at = 0
        while at < len(line) and line[at] not in " \t":
            at += 1
        found.append(line[:at])
    while True:
        while at < len(line) and line[at] in " \t":
            at += 1
        if at >= len(line):
            return found
        out: list[str] = []
        quotes = slashes = 0
        while at < len(line) and not (line[at] in " \t" and quotes == 0):
            char = line[at]
            at += 1
            if char == "\\":
                out.append(char)
                slashes += 1
                continue
            if char != '"':
                out.append(char)
                slashes = 0
                continue
            if slashes % 2 == 0:
                del out[len(out) - slashes // 2:]
                quotes += 1
            else:
                del out[len(out) - slashes // 2 - 1:]
                out.append('"')
            slashes = 0
            while at < len(line) and line[at] == '"':
                quotes += 1
                if quotes == 3:
                    out.append('"')
                    quotes = 0
                at += 1
            if quotes == 2:
                quotes = 0
        found.append("".join(out))


def cmd_arguments(line: str) -> list[str] | None:
    """-> the arguments that follow the console's token in cmd.exe's own command line (`CMDCMDLINE`):
    `cmd.exe [switches] /c <command>`, the command's first quote and its last taken off as cmd.exe takes them, then
    read by `windows_argv` -- None when cmd.exe runs no `/c`/`/k` (an interactive cmd) or runs another command first."""
    at = len(windows_argv(line)[0]) + (2 if line.startswith('"') else 0)
    while True:
        while at < len(line) and line[at] in " \t":
            at += 1
        if not line.startswith("/", at):
            return None
        if line[at + 1:at + 2].lower() in ("c", "k"):
            command = line[at + 2:].lstrip(" \t")
            break
        while at < len(line) and line[at] not in " \t":
            at += 1
    if command.startswith('"'):
        last = command.rfind('"')
        command = command[1:last] + command[last + 1:] if last > 0 else command[1:]
    argv = windows_argv(command)
    return argv[1:] if re.split(r"[\\/]", argv[0])[-1].lower() in CONSOLE_TOKENS else None


def console_arguments(argv: list[str], line: str | None) -> list[str]:
    """-> the console's arguments: those that follow the token of `pp.cmd` in cmd.exe's raw line (`PP_CMDLINE`) when
    it is set and carries the token -- an argument of several lines and every flag after it whole --, behind the
    `--instance <dir>` the borrowed `pp.cmd` puts first itself; else `argv`."""
    found = cmd_arguments(line) if line else None
    if found is None:
        return argv
    launcher = argv[:2] if argv[:1] == ["--instance"] and found[:2] != argv[:2] else []
    return launcher + found


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
        sys.stderr.write(messages.refused(refusal.code, refusal.detail))
        return 2
    except BrokenPipeError:
        # the reader of stdout left before the output was written (`| head -c 0`): the run
        # MOVED -- its state is saved before anything prints -- and the output
        # is lost to the caller alone. Said on stderr, the exit clean: no traceback at the
        # interpreter's last flush
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.stderr.write(messages.output_lost() + "\n")
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
                raise Refusal("call-busy", messages.refusal_call_busy_2(run))
            leases.append(lease)
        dropped = _here(key).forget()
    finally:
        for lease in leases:
            lock.release(lease)
    print(messages.forgotten(dropped))
    return 0


def _purge(arguments: list[str]) -> int:
    """`-purge`: removes for good what the engine keeps of runs -- each one's slot or renewal
    mark, every `session-<key>.*`, every trace of its key -- the runs named, or every run and
    every trace that names no run last written before `--before`. Without `--yes` it says what it
    would remove and writes nothing. Each run under ITS call lock, tried without waiting: one
    held refuses `call-busy` and nothing is removed; the lock's own file is removed once released --
    an open file is never removed, and one another process holds open is left and said."""
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
            raise Refusal("purge-invalid", messages.refusal_purge_invalid(value))
        del rest[at:at + 2]
    if (before is None) == (not rest) or any(one.startswith("-") for one in rest):
        raise Refusal("purge-usage", messages.usage_purge())
    member = _member()
    keys = list(dict.fromkeys(rest))
    if before is None:
        unknown = [key for key in keys if not purge.files_of(member.meta, key)]
        if unknown:
            raise Refusal("run-unknown", messages.refusal_run_unknown(' '.join(unknown)))
    entries = purge.planned(member.meta, keys, before)
    leases, left = [], []
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
                raise Refusal("call-busy", messages.refusal_call_busy_3(entry['key']))
        if confirmed:
            left = purge.removed(member.meta, entries, {lease.path for lease in leases})
    finally:
        for lease in leases:
            lock.release(lease)
    if confirmed:
        left += purge.released([lease.path for lease in leases])
    for path in left:
        print(messages.left_open(path.name), file=sys.stderr)
    files = sum(len(entry["files"]) for entry in entries)
    weight = sum(entry["bytes"] for entry in entries)
    if as_json:
        print(purge_json.dumps({"dry": not confirmed, "runs": [
            {"key": entry["key"], "files": [one.name for one in entry["files"]], "bytes": entry["bytes"]}
            for entry in entries], "files": files, "bytes": weight}, ensure_ascii=False))
        return 0
    head = (messages.purged(len(entries), files, weight) if confirmed else
            messages.purge_would(len(entries), files, weight))
    lines = [head]
    for entry in entries:
        name = entry["key"] or entry["files"][0].name
        lines.append(messages.purged_run(name, len(entry['files']), entry['bytes']))
    if not confirmed and entries:
        lines.append(messages.purge_unconfirmed())
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
                                  messages.refusal_install_ambiguous())
                return _add(name)
            if len(argv) < 2:
                raise Refusal("install-usage", messages.usage_install())
            if argv[1].startswith("-"):
                # the DAY-2 form: no workspace leads -- host flags alone, and the
                # adapters wire the CURRENT instance's workspace (the `-package` motif)
                allowed = tuple(f"-{name}" for name in ("claude", "codex", "gemini", "cursor"))
                strange = [a for a in argv[1:] if a not in allowed]
                if strange:
                    raise Refusal("install-ambiguous",
                                  messages.refusal_install_ambiguous_2(' '.join(strange)))
                member = _standing()
                if member is None:
                    raise Refusal("instance-missing",
                                  messages.refusal_instance_missing())
                wired = [name for name in ("claude", "codex", "gemini", "cursor")
                         if f"-{name}" in argv[1:]]
                if "gemini" in wired:
                    import shutil
                    if shutil.which("gemini") is None:
                        raise Refusal("gemini-missing",
                                      messages.refusal_gemini_missing())
                if not _wire(member.path, member.meta, wired):
                    print(messages.already_wired())
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
                                  messages.refusal_gemini_missing())
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
                              messages.refusal_install_borrowed())
            made = install.install(adapters.product_of(HOME) / "engine" / "pp.py", target, packages,
                                   slug=slug, base=base, borrow=borrow)
            print(messages.installed_at(made))
            if wired:
                _wire(workspace, made, wired)
            else:
                print(messages.no_harness(made.parent, console_command()))
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
                    print(messages.materialized(made))
            else:
                compiling.render_registry(member.meta)   # validates; writes nothing
                for made in filter(None, (compiling.build_tools(member.meta),
                                          compiling.build_system(member.meta))):
                    print(messages.compiled(made))
                for made in install.console(member.meta):
                    print(messages.rewritten(made))
                for warning in compiling.lint(member.meta):
                    print(messages.warning(warning))
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
                        else messages.refused(refusal.code, refusal.detail, None))   # context for the agent to repair
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
            named = os.environ.get(context.CONDUCTED_RUN, "").strip()
            if named:
                # the agent's `-new` under a launcher that conducts a run of this instance
                # (`PP_CONDUCTED_RUN` names it) while that run stands mid-exchange: that
                # agent IS that run's -- softly, nothing opens. Unnamed, the call is another
                # conversation's (an editor beside the post): it opens
                from conductor import persistence
                if named in persistence.under_way(conductor.member.meta):
                    print(messages.already_open(named))
                    return 0
            if context.holding():
                conductor.open_output()      # the launcher's mounts follow: the output waits, open
            return report(conductor, conductor.start(conductor.boot(BOOT), " ".join(argv[1:])))
        if argv and argv[0] == "-reset":
            return _reset(argv[1] if len(argv) > 1 else None)
        if argv and argv[0] == "-purge":
            return _purge(argv[1:])
        if argv and argv[0] in ("-run", "-answer"):
            raise Refusal("verb-retired", messages.refusal_verbs_gone())
        if not argv:
            # keyless = INSPECTION only: shows where the single run stands --
            # never advances anything, never opens a run; the first line says the
            # effort in force -- a display for the operator, the agent owes it no
            # reading (the first call of a conversation is `-new`, always)
            conductor = _here()
            print(messages.effort(conductor.effort() or '—'))
            mark = conductor.renewal()
            if mark is not None:            # an upgrade renewed the run: said, never reopened here
                print(rendering.renewed(conductor.run_id, mark))
                return 0
            block = conductor.peek()
            if block is None:
                said = rendering.packages(conductor.switch_state())
                if said:
                    print(said)          # the DURABLE state: what SETTINGS switches off
                print(messages.no_run_under_way())
                return 0
            print(conductor.delivered(block, _agents(conductor), act="view", view=True))
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
                    given = reading.piped().strip()
                verb = " ".join(rest) if rest and rest[0].startswith("-") and rest != ["-"] else ""
                conductor = _here(key)
                if not context.agents(key) and context.holding():
                    conductor.open_output()  # the launcher's mounts follow: the output waits, open
                return report(conductor, conductor.reopen(conductor.boot(BOOT), given, verb),
                              act="reopened")
            if (rest[:1] not in (["-compacted"], ["-peek"]) and conductor_pending(key)
                    and not _opens(key, rest)):
                # an output cut under the cap: its next chunk comes BEFORE anything plays --
                # the bare call serves it; any other call bounces, a gesture and a print with
                # it: the fact said first, the chunk served after, nothing played and nothing
                # recorded. A view alone plays below, the chunk untouched
                conductor = _here(key)
                if context.agents(key):
                    # the agent's call: the chunk is the
                    # principal's to serve -- a bare call refuses, a value bounces unserved;
                    # the rest of a VIEW is the agent's own, served first
                    if not rest and conductor.viewing():
                        print(conductor.next_view())
                        return 0
                    if not rest:
                        raise Refusal("principal-advances", messages.refusal_principal_advances())
                    print(messages.chunk_pending(' '.join(rest)))
                    return 0
                if rest == ["-skip"]:
                    print(conductor.drop_pending())
                    return 0
                if rest:
                    print(messages.chunk_pending(' '.join(rest)))
                print(conductor.next_chunk())
                return 0
            if rest[:1] == ["-print"]:
                # the PRINT call: a production said to the principal, handed with the document
                # whose step asked it -- it plays over an output held, which it never moves
                if len(rest) != 3 or rest[2] != "-":
                    raise Refusal("print-usage", messages.usage_print())
                handed = reading.piped()
                conductor = _here(key)
                said, block = conductor.printed(rest[1], handed[:-1] if handed.endswith("\n") else handed)
                if block is not None:        # the run moved on, or the call was caught: the seam decides
                    return report(conductor, block)
                print(messages.printed(said, conductor.print_due()))
                return 0
            if rest and _agents_call(key) and _here(key).held() and not _moves_nothing(key, rest):
                # ONE output held at a time: the agent has not read it, so nothing that MOVES
                # the run -- a value, a mount, a door, a re-serve -- plays over it; a view or a
                # gesture moves nothing and plays, a gesture's `::mount` joining the held output
                print(messages.bounced())
                return 0
            if rest == ["-skip"]:
                print(messages.nothing_to_skip())
                return 0
            if rest[:1] == ["-s"]:
                if len(rest) < 2:
                    raise Refusal("s-usage", messages.usage_s())
                return _skill(key, rest[1], rest[2:])
            if rest[:1] == ["-open"]:
                if len(rest) != 2:
                    raise Refusal("open-usage", messages.usage_open())
                return _open(key, rest[1])
            if rest[:1] == ["-close"]:
                if len(rest) > 1:
                    raise Refusal("close-usage", messages.usage_close())
                conductor = _here(key)
                return report(conductor, conductor.close(), act="closed", gesture=True)
            if rest[:1] and rest[0].startswith("-") \
                    and rest[0] not in ("-", "-s", "-peek", "-mount", "-compacted",
                                        "-disable", "-enable"):
                # a dash-word the console does not know is no value: named, nothing played
                raise Refusal("verb-unknown",
                              messages.refusal_verb_unknown(rest[0]))
            if rest[:1] == ["-compacted"]:
                if len(rest) > 1:
                    raise Refusal("compacted-usage", messages.usage_compacted())
                conductor = _here(key)
                return report(conductor, conductor.compacted(), act="compacted")
            if rest[:1] in (["-disable"], ["-enable"]):
                # the run's switch: the operator's word, said to the agent and written at
                # the run -- one package out of the play (its dependents with it) or back
                # in, and the block that stands comes back; the run never moves
                if len(rest) != 2:
                    raise Refusal("switch-usage", messages.usage_switch(rest[0]))
                conductor = _here(key)
                print(conductor.switch(rest[1], rest[0] == "-disable", _agents(conductor)))
                return 0
            if rest[:1] == ["-peek"]:
                conductor = _here(key)
                block = conductor.peek()
                if block is None:
                    return 0
                # `-peek <name>` asks the same reader as a call would: the offer map
                # of the current output, never the block's own list
                if len(rest) > 1 and _peeked(conductor, rest[1]) is None:
                    return denied(conductor, block, rest[1])
                print(conductor.delivered(block, _agents(conductor), act="view", view=True))
                conductor.viewed_map()
                return 0
            if rest[:1] == ["-mount"]:
                # the HOSTING verb: documents named by their ADDRESS enter the current
                # view until the exchange ends -- bare addresses take the defaults
                # (constraints+tools); ONE JSON array picks per document
                if len(rest) < 2:
                    raise Refusal("mount-usage", messages.usage_mount())
                raw = rest[1:]
                if len(raw) == 1 and raw[0].lstrip().startswith("["):
                    import json as mount_json
                    try:
                        entries = mount_json.loads(raw[0])
                    except ValueError as wrong:
                        raise Refusal("mount-invalid", messages.refusal_mount_invalid_6(wrong))
                else:
                    entries = [{"doc": one} for one in raw]
                conductor = _here(key)
                print(conductor.mount(entries, agents=_agents(conductor), hold=_holds(conductor)))
                return 0
            given = " ".join(rest)
            if given == "-":
                given = reading.piped().strip()
            conductor = _here(key)
            # the console tells the callers apart (`context.agents`) and hands the answer
            # to the facade -- the one judge serves both
            if not context.agents(key):
                if _opens(key, rest):
                    # the launcher's mounts follow: the message opens the exchange, no block is
                    # rendered, and the bare call plays it once its context is posed
                    print(conductor.opens(given))
                    return 0
                if conductor.held():
                    if rest:
                        raise Refusal("output-held", messages.refusal_output_held())
                    print(conductor.release())
                    return 0
                return report(conductor, conductor.forward(given, principal=True))
            if not rest:
                if conductor.viewing():
                    # the rest of a view the agent was answered: its bare keyed call alone
                    # serves it, chunk by chunk -- nothing of the run moves
                    print(conductor.next_view())
                    return 0
                raise Refusal("principal-advances", messages.refusal_principal_advances())
            return report(conductor, conductor.forward(given))
        if argv[0] == "-s":
            if len(argv) < 2:
                raise Refusal("s-usage", messages.usage_s())
            return _skill(None, argv[1], argv[2:])
        if argv[0] == "-compacted":
            raise Refusal("no-run",
                          messages.refusal_compacted_keyless())
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
                raise Refusal("stats-usage", messages.usage_stats())
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
                    raise Refusal("stats-usage", messages.usage_stats_days())
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
                    raise Refusal("run-unknown", messages.refusal_run_unknown_3(key))
            if where and not as_json:
                print(messages.run_lives(key, where))
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
                raise Refusal("no-run", messages.refusal_no_trace())
            log.record(traced[-1], "turn-end")
            print(messages.turn_end(traced[-1].name))
            return 0
        if argv[0] == "-peek":
            conductor = _here()
            block = conductor.peek()
            if block is None:
                return 0
            if len(argv) > 1 and _peeked(conductor, argv[1]) is None:
                return denied(conductor, block, argv[1])
            print(conductor.delivered(block, _agents(conductor), act="view", view=True))
            conductor.viewed_map()
            return 0
        if not argv[0].startswith("-") and re.fullmatch(r"[0-9a-f]{6}", argv[0]):
            raise Refusal("run-unknown",
                          messages.refusal_run_unknown_2(argv[0]))
        raise Refusal("verb-unknown", _unknown(argv[0]))
    except Refusal as refusal:
        if conductor is not None:      # best-effort: a refusal with no run resolved has no home
            conductor.noted(refusal)
        # an armed refusal ended a re-serve: the declaration stands and the next call re-serves
        sys.stderr.write(messages.refused(refusal.code, refusal.detail,
                                          messages.ARMED if refusal.armed else messages.NOTHING_PLAYED))
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
    the same output, so one call leaves one rest. Under an output its principal
    holds open the text answers the call and joins nothing. The trace weighs the text.
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
    holds = _holds(runner)
    # the anchor line of a fused output opens the text: it counts under the same cap -- an output
    # the principal holds open has shown no segment: the text answers the call without the line,
    # and nothing of it joins that output
    shown = f"{anchor}\n\n{text}" if anchor and not holds else text
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
                          messages.refusal_mount_invalid_5(wrong))
        print(runner.mount(entries, lead=shown if rank == 0 else "",
                           agents=_agents(runner), hold=holds))
    for source, signal in events.gesture_signals(runner.member.meta, base):
        runner._signal(source, signal, evidence=" ".join(arguments))
    return rc


def _peeked(conductor, name: str) -> dict | None:
    """-> the segment entry `-peek <name>` asks about -- the reader a call would ask, `name@<n>`
    naming the segment as `-s` and `-open` do; several owners refuse under `-peek`."""
    base, sep, tail = name.partition("@")
    if sep and not tail.isdigit():
        raise Refusal("address-invalid",
                      messages.refusal_address_invalid(name, base))
    return conductor.route(base, int(tail) if sep else None, verb="-peek")


def _open(run: str, name: str) -> int:
    """The `-open` call: the agent opens a SPACE on a name the current output offers -- the
    same reader as `-s`, except that several owners route to the LAST, the pending step's
    segment (a name resolves one document), `name@<n>` still saying which -- and that
    resolves to a proc of the instance; anything else refuses `open-unplayable`, a space
    open already `space-open`. The space stacks over the pending step and becomes the root."""
    conductor = None
    try:
        base, sep, tail = name.partition("@")
        if sep and not tail.isdigit():
            raise Refusal("address-invalid",
                          messages.refusal_address_invalid_2(name, base))
        conductor = _here(run)
        block = conductor.peek()
        if block is None:
            raise Refusal("no-run", messages.refusal_no_run())
        opened = conductor.spaces_open()          # judged on the stack before the offer: a space open
        if base in opened:                         # already is never opened twice, offered or not
            raise Refusal("space-open", messages.refusal_space_open_2(base, ' ▸ '.join(opened)))
        # a space stacks a frame: none stacks before the exchange an open output waits for is played
        entry = None if conductor.unplayed() else conductor.route(base, int(tail) if sep else None, verb="-open")
        if entry is None:
            return denied(conductor, block, name)
        kind, _ = _resolve_skill(conductor.member.meta, base)
        if kind != "proc":
            raise Refusal("open-unplayable", messages.refusal_open_unplayable_2(base))
        player = _here(run)
        return report(player, player.open(base, route=entry), act="door", gesture=True)
    except Refusal as refusal:
        if conductor is not None:
            conductor.noted(refusal)
        sys.stderr.write(messages.refused(refusal.code, refusal.detail))
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
                          messages.refusal_address_invalid_3(name, base))
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
            if at is None and kind == "script" and _holds(conductor):
                # the principal poses the context of an exchange: whatever waits at the run, a
                # SCRIPT is judged on what the root of the passage offers, read at its document --
                # never on a segment of an output
                entry = conductor.rooted(base)
            elif kind != "script" and conductor.unplayed():
                # a door stacks a frame: none stacks before the exchange an open output waits for
                # is played -- no segment of that exchange stands to offer it
                entry = None
            else:
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
            raise Refusal("no-run", messages.refusal_no_run())
        if entry is None:
            return denied(conductor, block, name)
        if kind == "proc":
            player = _here(run)   # the peeked one is dry-tainted
            lead = messages.argument_ignored(' '.join(arguments)) if arguments else ""
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
                                   agents=_agents(runner), act="manual"))
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
        print(messages.offered_unplayed(base))
        return 0
    except Refusal as refusal:
        if conductor is not None:      # best-effort: a refusal with no run resolved has no home
            conductor.noted(refusal)
        sys.stderr.write(messages.refused(refusal.code, refusal.detail))
        return 2


if __name__ == "__main__":
    sys.argv[1:] = console_arguments(sys.argv[1:], os.environ.pop(CMDLINE, None))   # dropped: no child reads it
    raise SystemExit(main(sys.argv[1:]))
