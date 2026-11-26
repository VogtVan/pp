"""core.messages — every line the engine addresses to the agent, written here and nowhere else.

Nine categories, each with ONE form function that sets its mark, its separator and its place in
the block; every message is a function of its category, called by its name from the site that
says it — no other module types the text. The module depends on nothing of the engine: it is
read by path by the model and the campaign, and a site hands it the values a message names.

    frame           the output's own lines: the heading, the packages' line, a section's title,
                    a segment's heading, the closing, a gesture's anchor        -> `framed`
    refusal         `pp: REFUSED — <code> — <detail>` and the line under it   -> `refused`
    deviation       what a call missed, said under `▌ DEVIATION`              -> `deviation`
    acknowledgement the one line a call answers: a held act, a print, a bounce -> `acknowledged`
    fact            a line of the foot, `   (<fact>)`                         -> `fact`
    complement      a text the conduction serves in place of a reading         -> `complement`
    diagnostic      a line under `▌ DIAGNOSTIC`, `<code> · <level> · <fact>`   -> `diagnostic`
    console         the console's own state, `pp: <state>`                    -> `console`
    maintenance     the lines of an install, a sync, a doctor, `pp: <line>`   -> `maintenance`
"""
from __future__ import annotations


# --- frame -------------------------------------------------------------------------------------

MARK = "▌"     # ONE repeating motif: `▌ TITLE`, flush content, a blank line between
               # sections — two characters of delimiter, never a wall of them
SIGNAL = "▶"   # the closing's own mark, once per block, right above the exact call owed --
               # CONTINUE/AWAIT carry it; a block that owes no call has none
ANCHOR = "◀"   # a gesture's own mark: the line points BACK, at the segment the call
               # hooked into — never a block, never a closing, one line and nothing else
VOICE = "pp"   # the engine's name on the heading and on the anchor
CELL = " · "   # between two cells of a heading
FUSION = "fusion · address a segment with @n when needed"   # the heading's reminder under fusion
AREAS = "on all produced areas"   # the plate a checkpoint judges, until a law declares its own
SUBJECT = " — "     # between the title of a section that serves a text and the subject it serves


def framed(mark: str, text: str) -> str:
    """The form of a FRAME line: its mark, a blank, its text."""
    return f"{mark} {text}"


def opening(cells: list[str]) -> str:
    """-> the output's heading: the engine's name, then its cells (the run, the root, the fusion,
    the hour)."""
    return framed(MARK, f"{VOICE}{CELL}" + CELL.join(cells))


def run_cell(key: str) -> str:
    return f"run {key}"


def root_cell(root: str) -> str:
    return f"root {root}"


def pins(cells: list[str]) -> str:
    """-> the packages' line under the heading, one cell per pin."""
    return framed(MARK, CELL.join(cells))


def pin_on(name: str) -> str:
    return f"{name} on"


def pin_off(name: str, cause: str) -> str:
    return f"{name} off" if cause == name else f"{name} off (<- {cause})"


def titled(section: str, subject: str = "") -> str:
    """-> the title of a section: its name, then the subject it serves when it serves one."""
    return f"{section}{SUBJECT}{subject}" if subject else section


def title(text: str) -> str:
    """-> a section's title line: `▌ <title>`."""
    return framed(MARK, text)


def segment(stack: str, ordinal: int = 0, routed: str = "", repair: int = 0) -> str:
    """-> a segment's heading: its number in a multi-heading output, its stack, the segment a door
    was routed from, its repair."""
    said = framed(MARK, (f"[{ordinal}] " if ordinal else "") + stack)
    if routed:
        said += f"   (routed from {routed})"
    if repair:
        said += f" · REPAIR {repair}"
    return said


def closing(label: str) -> str:
    """-> the closing's line: `▶ <label>`."""
    return framed(SIGNAL, label)


def anchor(ordinal: int, stack: str) -> str:
    """-> the one line a gesture renders: the segment it hooked into."""
    return framed(ANCHOR, f"{VOICE}{CELL}[{ordinal}] {stack}")


# --- refusal -----------------------------------------------------------------------------------

REFUSED = "pp: REFUSED — "     # the console's line of a refusal: this mark, then the refusal
SEPARATOR = " — "              # between a refusal's code and its detail
NOTHING_PLAYED = "pp: nothing was played"   # the line under a refusal
ARMED = "pp: the compaction you declared stands — your next call serves the run back; hand your production after it"
                               # the line under an armed refusal: what stands, and what the next call does
MOUNT_UNPLAYED = "pp: the skill ran — its mount did not"   # under a command's mount that found no run


def refused(code: str, detail: str, under: str | None = NOTHING_PLAYED) -> str:
    """The form of a REFUSAL: `pp: REFUSED — <code> — <detail>`, then -- when `under` is given -- the
    line under it, in pp's voice, and the newline that ends the console's write."""
    line = f"{REFUSED}{code}{SEPARATOR}{detail}"
    return line if under is None else f"{line}\n{under}\n"


def refusal_text(code: str, detail: str) -> str:
    """-> what a refusal says of itself: `<code> — <detail>`."""
    return f"{code}{SEPARATOR}{detail}"


def read_refused(line: str) -> tuple[str, str] | None:
    """-> (code, detail) of a refusal line of the console, None for any other line."""
    if not line.startswith(REFUSED):
        return None
    code, _, detail = line[len(REFUSED):].partition(SEPARATOR)
    return code, detail


# the details of the refusals of the play — the codes the agent meets while a run plays
# (arbitrage 2 b: the refusals of the build keep their detail where they are raised)





def refusal_repair_exhausted(instruction, allowed) -> str:
    return f"`{instruction}` was repaired {allowed} times and still misses; the run stands on it"


def refusal_row(detail, row) -> str:
    """-> the detail of a refusal of a serve row, the row named after the detail it carries."""
    return f"{detail} — {row}"


def row_of(host) -> str:
    return f"serve row of {host}"


def row_token_of(token, host) -> str:
    return f"serve row `{token}` of {host}"


def row_body_of(name) -> str:
    return f"`body` of `{name}`"


def refusal_principal_advances() -> str:
    return ALREADY


def refusal_verb_unknown_word(word, hint) -> str:
    return (f"`{word}` is no verb of the console, no command of a pinned package and no run's key "
            f"— `./pp help` lists them{hint}")


def verb_hint(name) -> str:
    return f"; the package `{name}` declares it — `./pp add {name}`"






def refusal_options_empty(instruction) -> str:
    return f'`{instruction}` has nothing to choose from'


def refusal_options_invalid(instruction, wrong_form) -> str:
    return f'`{instruction}` — {wrong_form}'


def refusal_format_unknown(output, document) -> str:
    return f'`output: {output}` ({document}) — not in the enumeration; declare it in a `formats:` first'


def refusal_documents_unknown(documents, raw) -> str:
    return f'`{documents}={raw}` — the root of documents is an absolute path to a directory that exists'


def refusal_no_renewed_run() -> str:
    return 'no renewed run under this key — call `-new` first'


def refusal_next_floor(document) -> str:
    return f'{document} declares `next:` and is the floor — a transition needs a caller; CALL it from a root document'


def refusal_marble_missing(standing) -> str:
    return f'PP_MARBLE is declared but no compiled contract exists at {standing} — run `-build` (or drop the sentinel)'


def refusal_guard_negative(guard) -> str:
    return f'`^ @{guard}` — a cadence below 0 means nothing'


def refusal_door_unknown(door, door2) -> str:
    return f"`{door}={door2}` names no document of this instance — the launcher's entry must resolve through its search paths"


def refusal_packages_invalid(packages, raw) -> str:
    return f'`{packages}={raw}` — the form is `<name>=on|off`, several joined by commas'


def refusal_package_base(packages, raw, name) -> str:
    return f'`{packages}={raw}` — `{name}` is the base of every instance, never switched'


def refusal_package_unpinned(packages, raw, name, pinned) -> str:
    return f'`{packages}={raw}` — `{name}` is not pinned here: the packages are {pinned}'


def refusal_artifact_stale(marble, value, version) -> str:
    return f'{marble} was compiled by {value} and the standing engine is {version} — `doctor` (or `-build`) recompiles it'


def refusal_artifact_predates(marble) -> str:
    return f'{marble} predates the standing vendor inputs — `doctor` (or `-build`) recompiles it'


def refusal_no_run() -> str:
    return 'no run is under way — call `-new` first'


def refusal_guard_not_whole(guard, declared) -> str:
    return f'`^ @{guard}` — `{declared}` is not a whole number'


def refusal_run_ambiguous(count) -> str:
    return f"{count} runs are under way — your conversation's key (handed at `-new`) leads every command of this run, `./pp <key> ...`; a new conversation opens its own with `-new`"


def refusal_documents_fixed(documents, asked, slot, root) -> str:
    return f"`{documents}={asked}` — run {slot} keeps the root of documents it opened with ({root}): a run's composition never moves; another root opens another run, with `-new`"


def refusal_package_base_off(name) -> str:
    return f'`{name}` is the base of every instance — never switched off'


def refusal_package_unpinned_here(name) -> str:
    return f'`{name}` is not pinned here — `./pp version` says what this instance composes'


def refusal_address_ambiguous(name, where, verb, name2) -> str:
    return f'`{name}` is offered by segments [{where}] of the current output — address it: `{verb} {name2}@<n>`'


def refusal_package_in_flight(name, flight) -> str:
    return f'`{name}` holds the standing view: {flight} — the frame finishes, then the word plays'


def refusal_address_stale(at, name) -> str:
    return f'segment [{at}] of the current output does not offer `{name}` — addresses live with their output'


def refusal_open_unplayable(name, unplayable) -> str:
    return f'`{name}` cannot be opened as a space: {unplayable}'


def refusal_space_open(name, opened) -> str:
    return f'`{name}` is open already — the spaces open: {opened}; `-close` leaves the deepest'


def refusal_space_none() -> str:
    return 'no space is open — `-close` leaves the space an `OPEN` or `-open` opened'


def refusal_mount_missing(name) -> str:
    return f'`{name}` — no document answers that address'


def refusal_sys_shape(shown, what) -> str:
    return f'`{shown}` — a SYS.md declares its laws and nothing else: {what}'


def refusal_sys_misplaced(shown) -> str:
    return (f'`{shown}` — system laws and their `SYS<n>` codes belong to the engine\'s and the '
            'instance\'s `system/SYS.md` alone: move the laws to the instance\'s `system/SYS.md`, '
            'or declare them in a document under a code other than `SYS<n>`')


def refusal_law_twice(code, places) -> str:
    if len(set(places)) == 1:
        return f'`{code}` declared twice by `{places[0]}` — a system law\'s code is held once'
    return f'`{code}` declared by {" and ".join(f"`{one}`" for one in places)} — a system law\'s code is held once'


def refusal_mount_invalid(name) -> str:
    return f'`{name}` — a `body` list holds selections, one at least: ["<start>..<end>", ...]'


def refusal_mount_missing_2(name) -> str:
    return f'`{name}` — no such document in a bundle this instance plays'


def refusal_mount_missing_3(name) -> str:
    return f'`{name}` — a mount names an address, never an absolute path nor a `..`'


def refusal_mount_invalid_2() -> str:
    return '`replaces` is a list of addresses — {"doc": <path>, "replaces": [<address>, ...]}'


def refusal_mount_invalid_3() -> str:
    return 'a mount entry is {"doc": <path>[, "body", "constraints", "tools": true|false]}'


def refusal_mount_invalid_4(name) -> str:
    return f"`scope` ({name}) — a mount entry carries no `scope`: a mounted document makes no segment, its body is a reading of the step that stands, its laws and its offers join that step's"


def refusal_import_cycle(loop) -> str:
    return f'`{loop}` — the imports loop; a document imports what stands under it, never what imports it'


def refusal_mount_collision(code, name) -> str:
    return f'`{code}` ({name}) — already in force here'


def refusal_keyword_not_executable(keyword) -> str:
    return f'`{keyword}` has no handler'


def refusal_guard_unformed(declared, name) -> str:
    return f'`when: {declared}` on {name} — a guard is `@Doc.field`'


def refusal_cycle_unprovided(document, token, token2) -> str:
    return f'{document}: `cycle: {token}` — no document of the composition provides `{token2}`'


def refusal_exec_argument_empty(word, path, value, value2) -> str:
    return f'`{word}` at {path} — no `{value}:` on {value2}.md and no default: an exec argument is never passed empty'


def refusal_session_stale(document, anchor, above) -> str:
    return f'{document} no longer declares `{anchor}`, the step that holds {above} — the run cannot take up its passage; `./pp -reset <key>` ends it'


def refusal_field_argument_empty(document, stem, field) -> str:
    return f'{document}: `@{stem}.{field}` in `field:` resolves to nothing — a reference of the brief names a value'


def refusal_choose_argument_empty(document, stem, field) -> str:
    return f'{document}: `@{stem}.{field}` in `choose:` resolves to nothing — a reference of the brief names a value'


def refusal_next_refused(skill, rest, document, rc, err) -> str:
    return f'`{skill} {rest}` at {document} refused ({rc}): {err}'


def refusal_next_foreign(skill, rest, document, said, names) -> str:
    return f'`{skill} {rest}` at {document} said `{said}` — not a successor of its `next:` ({names})'


def refusal_exec_refused(skill, verb, path, site, rc, err) -> str:
    return f'`{skill} {verb}` at {path} ({site}) refused ({rc}): {err}'


def refusal_exec_mount(skill, verb, path) -> str:
    return f'`{skill} {verb}` at {path} printed a `::mount` — an exec prepares, it mounts nothing'


def refusal_format_mismatch(document, frame, needs) -> str:
    return f'{document} produces `{frame}` — the adjacent CALL needs `{needs}`'


def refusal_skill_ambiguous(name) -> str:
    return f'`{name}` names both a conducted skill and another — rename one'


def refusal_command_broken(verb, skill, package) -> str:
    return f'`{verb}` -> `{skill}` — the manifest of `{package}` declares it, no script answers: `doctor` repairs the instance'


def refusal_mount_without_run(verb) -> str:
    return f'`{verb}` printed a `::mount` directive — the console has no run to host it; a mount needs a keyed call (`-s`)'


def refusal_call_reentrant(key, call) -> str:
    return f'this process was launched by a call on run {key} of this very instance (`{call}`) and calls it back — a skill never calls its own run: it prints, pp plays'


def refusal_call_busy(key, wait) -> str:
    return f'another call holds run {key} and has not answered within {wait}s (`call_lock_wait` at SETTINGS) — replay your call once it has'


def refusal_relaunch_invalid(verb, relaunches) -> str:
    return f'`{verb}` — a command at the terminal may ask {relaunches} alone'


def refusal_address_invalid(name, base) -> str:
    return f'`{name}` — what follows `@` is the segment number: `-peek {base}@<n>`'


def refusal_run_unknown(unknown) -> str:
    return f'`{unknown}` — no file of this instance belongs to that run; nothing removed'


def refusal_compacted_keyless() -> str:
    return '`-compacted` declares the compaction of YOUR run, so it leads with the key: `./pp <key> -compacted`; with the key gone too, `-new` opens a run'


def refusal_run_unknown_2(argv) -> str:
    return f"`{argv}` — no run holds that key; your conversation's key was handed at `-new`"


def refusal_address_invalid_2(name, base) -> str:
    return f'`{name}` — what follows `@` is the segment number: `-open {base}@<n>`'


def refusal_space_open_2(base, opened) -> str:
    return f'`{base}` is open already — the spaces open: {opened}; `-close` leaves the deepest'


def refusal_open_unplayable_2(base) -> str:
    return f'`{base}` is no proc of this instance — a space opens on the steps of a proc'


def refusal_address_invalid_3(name, base) -> str:
    return f'`{name}` — what follows `@` is the segment number: `-s {base}@<n>`'


def refusal_source_missing(checkout) -> str:
    return f'`{checkout}` holds no engine — `--from` names a checkout of the product'


def refusal_call_busy_2(run) -> str:
    return f'a call holds run {run} — `-reset` forgets no run under a call: replay once it has answered'


def refusal_purge_invalid(value) -> str:
    return f'`--before {value}` — a date is written YYYY-MM-DD'


def refusal_call_busy_3(key) -> str:
    return f'a call holds run {key} — `-purge` removes no run under a call, and nothing was removed: replay once it has answered'


def refusal_install_borrowed() -> str:
    return "an instance that borrows a machine plays its composition — packages and `-base` are the machine's (`-own` for a copy of yours)"


def refusal_verb_unknown(rest) -> str:
    return f'`{rest}` is no verb of the console — `./pp help` lists them'


def refusal_no_trace() -> str:
    return 'no run trace to stamp — `-new` opens a run'


def refusal_mount_invalid_5(wrong) -> str:
    return f'`::mount` payload is not one valid JSON array — {wrong}'


def refusal_install_ambiguous() -> str:
    return '`-package <name>` targets the current instance alone'


def refusal_install_ambiguous_2(strange) -> str:
    return f'`{strange}` — the day-2 form takes host flags alone: `-install -claude|-codex|-gemini|-cursor`'


def refusal_instance_missing() -> str:
    return 'nothing to wire — the day-2 form runs from an installed instance'


def refusal_gemini_missing() -> str:
    return '`-gemini` needs the gemini CLI on PATH — the standing rules compose over its baseline'


def refusal_run_unknown_3(key) -> str:
    return f'`{key}` — no run of this instance nor of the instances under it holds that key; `./pp -stats` lists the runs here with their keys'


def refusal_output_held() -> str:
    return "an answer waits its principal's bare call — it is served first"


def refusal_mount_invalid_6(wrong) -> str:
    return f'not one valid JSON array — {wrong}'


# --- deviation ---------------------------------------------------------------------------------

def deviation(fact: str, call: str) -> str:
    """The form of a DEVIATION, said under `▌ DEVIATION`: pp's voice, the fact the call missed, then
    the call that mends it -- to the agent, plainly, no rule of the standing orders said again."""
    return f"pp: {fact}. {call[:1].upper()}{call[1:]}."


def empty_answer(instruction) -> str:
    return deviation(f"your answer to `{instruction}` is empty", "hand the production it asks")


def prints_due(documents) -> str:
    """-> what a call missed while productions said on `terminal` are due: the print call of each,
    by its document, in the order they are due."""
    calls = ", ".join(f"`-print {one} -`" for one in documents)
    return deviation("nothing was played: prints are due first", f"call {calls}")


def empty_print(document) -> str:
    return deviation(f"your print for `{document}` is empty", "pipe the production itself")


def print_stray(document) -> str:
    return deviation(f"nothing of `{document}` is due to print, nothing was kept", "go on with the step below")


def wrong_answer(answer, section, options) -> str:
    return deviation(f"`{answer}` is not in {section} ({', '.join(options)})", "pick one of them")


def not_offered(name) -> str:
    return deviation(f"`{name}` is not offered at this step, nothing was played", "play the step below")


def stray_production() -> str:
    return deviation("this step owes the tool no production, nothing was kept", "go on with the step below")


def soft_catch(document) -> str:
    return deviation("this production goes to the principal, not to the tool, nothing was kept",
                     f"print it with `-print {document} -`")


def renewed_reopens(key) -> str:
    return deviation(f"run {key} was renewed by an upgrade and reopens on its boot", "play the step below")


def mini_proof_codes(codes) -> str:
    return deviation(f"the mini-proof covers the repaired code(s) {', '.join(codes)} alone",
                     "pipe it again over them")


def mini_proof_relapsed(relapsed) -> str:
    return deviation("a repaired code failed again — "
                     + " · ".join(f"{one['code']}: {one['evidence']}" for one in relapsed),
                     "play the document again from its first step")


def proof_foreign(foreign) -> str:
    return deviation(f"your proof names laws not in force: {', '.join(foreign)}", "prove the codes the line asks")


def proof_unlawful() -> str:
    return deviation("your proof names no law of production", "prove the codes the line asks")


def proof_unnamed(unnamed) -> str:
    return deviation(f"your proof leaves {len(unnamed)} code(s) unnamed: {', '.join(unnamed)}",
                     "give each a verdict")


def proof_failed(bare) -> str:
    return deviation("your proof failed — " + " · ".join(f"{one['code']}: {one['evidence']}" for one in bare),
                     "play the document again from its first step")


def proof_fixes(fixed) -> str:
    return deviation("your proof failed and names its fixes — "
                     + " · ".join(f"{one['code']}: {one['fix']}" for one in fixed),
                     "repair the production in place, then prove the failed codes alone")


def proof_unparsed(wrong) -> str:
    return deviation(f"your proof is not one valid JSON value — {wrong}", "pipe it again")


def proof_unshaped() -> str:
    return deviation('your proof is not a JSON array of {"code", "evidence", "verdict"} objects', "pipe it again")


def proof_verdict(verdict) -> str:
    return deviation(f"a verdict is `ok`, `fail` or `n/a`, not {verdict!r}", "pipe the proof again")


def field_unparsed(wrong) -> str:
    return deviation(f"your field is not one valid JSON value — {wrong}", "pipe it again")


def production_empty() -> str:
    return deviation("your production is empty and the next step consumes it", "hand it over")


def production_unparsed(wrong) -> str:
    return deviation(f"your production is not one valid JSON value — {wrong}", "hand it again")


# --- acknowledgement ---------------------------------------------------------------------------

ALREADY = "call already done"     # the fact a bare call of the agent is refused with
HAND_BACK = "hand back"           # what is due of the agent once its call is answered by a line
SERVED = "your bare call serves it"   # what is due of the principal once its call held an output
ACKNOWLEDGED = {   # the verdict of an act whose output is held
    "value": "value judged",
    "mount": "mounted",
    "door": "opened",
    "closed": "closed",
    "compacted": "re-served",
    "reopened": "reopened",
}
OPENED = {         # what the principal's call that renders no block did: the exchange, and what waits
    "opened": "exchange opened",          # an opening, a message: the exchange waits for its mounts
    "reopened": "run reopened",           # a run renewed by an upgrade, reopened on its boot
    "standing": "exchange already open",  # an exchange an earlier call opened and never served
    "waiting": "an output waits",         # an output that closed already: nothing is opened
}
PRINTED = {        # what a print call answers: the print taken, what is due next
    "more": "printed",
    "last": "printed",
    "waived": "print not kept",
}
NEXT = "next:"     # what opens the call due after a print, when another call is due
NOT_PLAYED = "not played"   # the verdict of a call that moves the run while an output it has not read is held
CHUNK_PENDING = "chunk-pending"


def acknowledged(said: str, due: str) -> str:
    """The form of an ACKNOWLEDGEMENT, the one line a call answers: `pp: <verdict> — <what is due
    now>`."""
    return f"pp: {said} — {due}"


def held(act: str, default: str = "value", principal: bool = False) -> str:
    """-> the line of an act whose output is held -- its verdict, the `default` act's for an act the
    table does not name --, then what is due: the agent hands back; the principal's bare call serves."""
    return acknowledged(ACKNOWLEDGED.get(act, ACKNOWLEDGED[default]), SERVED if principal else HAND_BACK)


def opened(state: str) -> str:
    """-> the line of the principal's call that opens an exchange under an output it holds open:
    what it did (`OPENED`), then the bare call that plays it."""
    return acknowledged(OPENED[state], "your bare call plays it" if state != "waiting" else SERVED)


def printed(said: str, due: str = "") -> str:
    """-> the line a print call answers: `more` with the call due (`next_print`, `next_value`),
    `last`, `waived`."""
    if said == "last":
        return acknowledged(PRINTED[said], "hand back")
    if said == "waived":
        return acknowledged(PRINTED[said], "it was refused too many times; go on with the step that stands")
    return acknowledged(PRINTED[said], due)


def next_print(document) -> str:
    """-> the call due after a print when another print is due."""
    return f"{NEXT} `-print {document} -`"


def next_value(document, key, piped: bool) -> str:
    """-> the call due after a print when the step of `document` awaits its value: the call that hands
    it -- on the call itself, or piped by a heredoc when the step's line says `tool_heredoc` (`piped`)."""
    if piped:
        return f"{NEXT} pipe the value `{document}` asks with `./pp {key} - <<'EOF'`"
    return f"{NEXT} hand the value `{document}` asks with `./pp {key} <value>`"


def bounced() -> str:
    """-> the line a call that moves the run answers while an output it has not read is held."""
    return acknowledged(NOT_PLAYED, HAND_BACK)


def chunk_pending(words: str) -> str:
    """-> the line a call that moves the run answers while a chunk waits: nothing played."""
    return acknowledged(f"{CHUNK_PENDING}: `{words}` was not played", HAND_BACK)


def switched(name: str, off: bool) -> str:
    """-> the fact a switch of a package for the run says above the block."""
    return acknowledged(f"`{name}` {'off' if off else 'on'} for this run", "go on with the step below")


def argument_ignored(arguments: str) -> str:
    """-> what a door opened with arguments says above its block: they are not read."""
    return acknowledged(f"`{arguments}` ignored, a proc reads nothing from its call", "play the step below")


def offered_unplayed(name: str) -> str:
    """-> what a name offered and not conductible answers: it is the agent's, through its harness."""
    return acknowledged(f"`{name}` is offered and pp runs nothing for it", "play it through your harness")


def unsaid(line: str) -> str:
    """-> a line of the console without its voice: what a delegated engine said, said again."""
    return line[4:] if line.startswith("pp: ") else line


def answers() -> list[str]:
    """-> every line an acknowledgement says to the AGENT, without its voice -- what a reader of the
    engine's answers knows them by: the held acts, the head of a print's `more` (its call due follows
    it), the print's `last` and `waived`, the bounce."""
    return ([unsaid(held(act)) for act in ACKNOWLEDGED]
            + [unsaid(acknowledged(PRINTED["more"], NEXT)), unsaid(printed("last")), unsaid(printed("waived")),
               unsaid(bounced())])


# --- fact --------------------------------------------------------------------------------------

def fact(text: str) -> str:
    """The form of a FACT: a line of the foot, indented, in pp's voice between parentheses."""
    return f"   (pp: {text})"


READING = "a reading continues"   # the fact of a chunk before the last


def reading_continues(left, more) -> str:
    return f"{READING}: {left} characters in {more} more chunk(s)"


def gap_declared(code, text) -> str:
    return f"a gap declared: {code} — {text}"


def nothing_in_force() -> str:
    """-> why a written PROVE resolved with nothing to ask, as the trace keeps it (`prove-idle`)."""
    return "nothing due: no law of production in force"


def nothing_since() -> str:
    """-> the other reason of an idle PROVE, as the trace keeps it."""
    return "nothing due since the last proof"


def stopped_at_bound(instruction, repairs) -> str:
    return (f"stopped at the repair bound: `{instruction}` "
            f"missed {repairs} times")


# --- complement --------------------------------------------------------------------------------

def complement(text: str) -> str:
    """The form of a COMPLEMENT: a text the conduction serves where a reading or a context stands,
    under the section it completes -- the renderer places it, the text stands as it is."""
    return text


ASK_TEXT = complement("the principal's last message is the context")
RUN_COMPLETES = complement("nothing due — the run completes")
NOTHING_OPENS = complement("nothing due — nothing opens")
FRAME_LEAVING = complement("nothing due — the frame is leaving")
SECTION_GONE = complement("(this section's document is gone)")


# --- diagnostic --------------------------------------------------------------------------------

def diagnostic(code: str, level: str, text: str, way: str = "") -> str:
    """The form of a DIAGNOSTIC: `<code> · <level> · <fact>`, then ` — <way out>` when one is said."""
    return f"{code} · {level} · {text}" + (f" — {way}" if way else "")


def gone(name) -> str:
    """-> the evidence of a document gone: what `mount-gone` and `serve-stale` say."""
    return f"{name} — gone"


# --- console -----------------------------------------------------------------------------------

def console(state: str, then: str = "") -> str:
    """The form of the CONSOLE's state: `pp: <state>`, then ` — <what follows>` when one is said."""
    return f"pp: {state}" + (f" — {then}" if then else "")


def complete() -> str:
    return console("the procedure is complete", "nothing more to do")


def no_run_under_way() -> str:
    return console("no run is under way", "`-new` opens one")


def nothing_to_skip() -> str:
    return console("nothing to skip", "no reading waits")


def effort(said) -> str:
    return console("effort", said)


def already_open(key) -> str:
    return console("a run is already open", key)


def run_lives(key, where) -> str:
    return console(f"run {key} lives at {where}")


def turn_end(name) -> str:
    return console("turn-end", name)


def forgotten(count) -> str:
    return console(f"{count} run(s) forgotten", "`-new` opens a fresh one")


def output_lost() -> str:
    return console("the output was lost, its reader closed before it was written",
                   "the run played, its pending block stands")


def left_open(name) -> str:
    return console(f"{name} left", "another process holds it open")


def purged(count, files, weight) -> str:
    return console(f"{count} run(s) purged", f"{files} file(s), {weight} bytes")


def purge_would(count, files, weight) -> str:
    return console(f"-purge would remove {count} run(s)", f"{files} file(s), {weight} bytes")


def renewed(key, said) -> str:
    return console(f"run {key} was renewed by an upgrade ({said or 'the machine moved'}), nothing was written",
                   "the run stands on its boot, under the same key")


def purged_run(name, files, weight) -> str:
    return console(f"{name}  {files} file(s)  {weight} bytes")


def purge_unconfirmed() -> str:
    return console("nothing removed", "replay with --yes to remove them")


def version_source(source) -> str:
    return console(f"source {source}")


def version_machine(machine) -> str:
    return console(f"machine {machine}")


def version_moved(at_source, where) -> str:
    return f" — the source holds {at_source}; {where} moves you there"


def version_engine(version, moved) -> str:
    return console(f"engine {version}{moved}")


def version_pin(name, version) -> str:
    return console(f"{name} {version}")


def no_script(skill) -> str:
    return console(f"`{skill}` is no script skill of this instance")


def refusal_verbs_gone() -> str:
    return "`-run` and `-answer` are gone — the key leads: `./pp <key> [value|-|-s <name> [args]|-peek]`"


def usage(verb: str, text: str) -> str:
    """The detail of a USAGE refusal -- a verb of the console called without what it takes, refused
    `<verb>-usage`: `` `pp <verb>` <what it takes> ``."""
    return f"`pp {verb}` {text}"


def usage_flag(flag, what) -> str:
    return usage(flag, f"needs {what}")


def usage_repo() -> str:
    return usage("repo", "needs one workspace name")


def usage_version() -> str:
    return usage("version", "takes no argument but `-json`")


def usage_records() -> str:
    return usage("records", "takes `list`, `read <record>`, `count <record>` or `search <text>`. `read` "
                            "takes the filters `--since --until --key --prefix --where <field>=<value> "
                            "--match --order --after --before --last`, each once but `--where`; `count` "
                            "takes them but `--after` and `--before`, plus `--group day|key|<field>`; "
                            "`search` takes them all but `--match`, plus `--records <a,b>` to search those "
                            "records only. `--json` gives one JSON object; `list` takes nothing else")


def refusal_record_unknown(name: str) -> str:
    return f"`{name}` is not a record of this instance — `pp records list` names them"


def refusal_where_malformed(pair: str) -> str:
    return (f"`--where {pair}` — write `<field>=<value>`: a field of the entry and the value it must "
            "equal (`null`: the field is null or absent)")


def records_shown(shown: int, total: int, bound: int, call: str | None) -> str:
    line = f"{shown} shown out of {total} (at most {bound} per read)"
    return f"{line} — the next ones: `{call}`" if call else line


def records_cut() -> str:
    return "the entries are too long for one output: their bodies are cut short"


def usage_upgrade() -> str:
    return usage("upgrade", "takes no argument but `--from <checkout>`")


def usage_acquit() -> str:
    return usage("acquit", "needs one vector")


def usage_doctor() -> str:
    return usage("doctor", "takes no argument")


def usage_add() -> str:
    return usage("add", "needs one package name")


def usage_develop() -> str:
    return usage("develop", "needs one package name, then `off` to copy it back")


def usage_remove() -> str:
    return usage("remove", "needs one package name")


def usage_install() -> str:
    return usage("-install", "takes <workspace> [package ...] [-slug <slug>] [-base <package>] [-claude] [-codex] "
                             "[-gemini] [-cursor]")


def usage_s() -> str:
    return usage("-s", "needs a skill name")


def usage_stats() -> str:
    return usage("-stats", "takes [<days>|<key>] [--blocks] [-json]")


def usage_print() -> str:
    return usage("-print", "takes a document and its production piped — `-print <DOCUMENT> -`")


def usage_open() -> str:
    return usage("-open", "takes one name — a proc the output offers, opened as a space")


def usage_close() -> str:
    return usage("-close", "takes no other argument — it leaves the deepest space open")


def usage_compacted() -> str:
    return usage("-compacted", "takes no other argument — it declares that the host summarized the conversation")


def usage_switch(verb) -> str:
    return usage(verb, "takes one package name — the durable switch is `package.<name>: on|off` at SETTINGS")


def usage_mount() -> str:
    return usage("-mount", 'takes documents by their address (a name, a path in the instance, `<package>:<path>`), '
                           'or one JSON array of {"doc"[, "body": true|false|["<start>..<end>", ...], "constraints", '
                           '"tools": true|false]}')


def usage_purge() -> str:
    return usage("-purge", "takes <key> [<key> ...] | --before <YYYY-MM-DD> [--yes] [-json]")


def usage_stats_days() -> str:
    return usage("-stats", "takes a number of days or a run's key")


# --- maintenance -------------------------------------------------------------------------------

def maintenance(text: str) -> str:
    """The form of a MAINTENANCE line -- an install, a sync, a doctor, an upgrade: `pp: <what was done>`."""
    return f"pp: {text}"


def warning(text) -> str:
    return maintenance(warned(text))


def warned(text) -> str:
    """A warning among the lines a maintenance verb tells, before the voice `maintenance` gives them."""
    return f"WARNING — {text}"


def instance_document_faulty(code: str, detail: str) -> str:
    """A fault of one of the instance's own documents that `upgrade` and `doctor` let pass: its code
    first, then the refusal it would be, which names the path, then when that refusal comes."""
    return (f"{code}: {detail} -- this upgrade or doctor goes on, but the next `-sync` or build "
            "refuses it and stops the whole command: fix it, or move it into a folder whose name "
            "starts with `_`")


def borrower_faulty(borrower: str, line: str) -> str:
    """The same fault in an instance that borrows this machine, said by the machine's `upgrade` or
    `doctor`: the code first, as `instance_document_faulty` gives it, then the borrower, then the
    rest of that line."""
    code, _, rest = line.partition(": ")
    return f"{code}: in `{borrower}`, which borrows this machine, {rest}"


def installed_at(made) -> str:
    return maintenance(f"instance installed at {made}")


def package_installed(name, made) -> str:
    return maintenance(f"`{name}` installed at {made}")


def user_level(name, clashes) -> str:
    return maintenance(f"`{name}` installs user-level files ({', '.join(clashes)}) — a fresh, just-installed "
                       "workspace is recommended; here, your files would be replaced and saved as `.old`")


def fresh_workspace() -> str:
    return maintenance("fresh workspace name (empty = replace here): ")


def already_current() -> str:
    return maintenance("already current — nothing touched (`doctor` repairs in place)")


def acquitted(name, fell) -> str:
    return maintenance(f"`{name}` acquitted — {fell} entr{'y' if fell == 1 else 'ies'} of the record fell")


def already_wired() -> str:
    return maintenance("nothing to write — already wired")


def materialized(made) -> str:
    return maintenance(f"{made} materialized")


def compiled(made) -> str:
    return maintenance(f"{made} compiled")


def rewritten(made) -> str:
    return maintenance(f"{made} rewritten")


def replaced(saved) -> str:
    return maintenance(f"{saved} replaced — your previous file is at {saved}.old")


def no_harness(where, console) -> str:
    return maintenance(f"no harness wired at {where} — `{console} -install -<harness>` there wires one "
                       "(see the README)")


def pins_required(name, extra) -> str:
    return maintenance(f"add {name} — pins {', '.join(extra)} (required)")
