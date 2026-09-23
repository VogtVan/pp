"""packages/authoring/refs/PP_CHEATSHEET.md -- the sheet's examples PLAY: every indented document
is installed on the scenario's environment, every indented rendering is compared with what the
engine renders for it, section by section; the sheet is read at play time and no phrase of it is
pinned. A rendering elides what the engine fills as `…` (a whole line: a gap; a line ending with
` …`: a prefix, then a gap); between two gaps its lines are CONSECUTIVE in the engine's output. An
indented block that is neither a document, a rendering nor a call is a FRAGMENT -- a figure's cited
lines -- and plays nothing. The catalog the sheet carries (the forms, the keys, the figures, the
doctrine, what the engine does since beta.8) is pinned here too: nothing of it may leave the sheet."""
from __future__ import annotations

import json
import re

from conductor import persistence, render
from tests.harness import SOURCE, kept_document

SETTINGS = ("---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\nnote_frequency: 3\n"
            "cargo_due: 3\ncapture_prompt: true\nmax_harness_tool_output: 200000\n---\n")
FORMS = ("READING", "HOSTING", "CONTEXT", "LAW", "OFFER", "MISS", "SIGNAL", "ELECTION", "PRODUCTION", "FEED",
         "SELF-PROOF", "BLOCKED", "RECALL", "GESTURE", "DUE", "WAKE", "ASK", "VERBATIM", "GATE", "TUNING")
FIGURES = ("The conducted step", "The contributor", "The door", "The mounted step", "The overlay",
           "The payload", "The sink", "The iterated door", "The described door", "The workflow",
           "The entry act", "The cadence", "The check and the signal", "The package command",
           "The writer skill", "The settings fragment")
KEYS = ("| `exec:` |", "| `field:` |", "| `next:` |", "| `choose:` / `decide:` |", "| `sink:` |")
EMPLOYERS = ("cycle-described.py", "workflow-acyclic.py", "exec-at-entry.py")
DOCTRINE = ("The lived doctrine", "5 900 ok for 3 fail", "constraints-unsectioned", "never proven",
            "whole, sample or trace fact", "the codes at risk", "no active production law means silent checkpoint")
DUE = ("ephemerals => chat", "<the operator's next message>", "mounts its manual", "chunk-pending",
       "-disable", "final-names.py", "mount-overlays.py", "skill-gesture.py", "cut.py",
       "package-switch-run.py")
FILE_OF = {"Compass": "MEMBER.md"}        # the member's document keeps its file name
NAME = re.compile(r"^name: (\S+)$", re.M)
KEY = re.compile(r"\./pp \S+")
PACKAGES = re.compile(r"^▌ (\S+ (on|off)( \(<- \S+\))?( · )?)+$")
HEADING = re.compile(r"^▌ (\[\d+\] )?(?P<stack>[^{]+?)(\{[^}]*\})?( · REPAIR \d+)?$")
STANDING = "▌ INFORMATION — standing orders"
PARTS = ("TOOLS", "INFORMATION", "NEXT INSTRUCTION CONTEXT", "CONSTRAINTS", "DEVIATION", "OPTIONS",
         "INSTRUCTION", "END")                # the sections of a block, never a document's heading
GAP = object()


def pieces(text: str) -> list[tuple[str, str, list[str]]]:
    """-> (section, kind, lines) for every indented block of the sheet, dedented: a `doc`
    opens on `---`, a `render` on `▌` or `▶`, a `call` on `./pp`, anything else a `fragment` -- a
    block starts at the head of a stretch or after a blank line, a document's body and a
    fragment's later lines continuing what stands; a stretch ends at a prose line."""
    found: list[tuple[str, str, list[str]]] = []
    section, current, blank = "", None, True
    for raw in text.splitlines():
        if raw.startswith("#"):
            section, current, blank = raw.lstrip("# ").strip(), None, True
            continue
        if not raw.strip():
            blank = True
            if current is not None:
                current[2].append("")
            continue
        if not raw.startswith("    "):
            current, blank = None, True
            continue
        line = raw[4:].rstrip()
        kind = ("doc" if line.startswith("---") else "render" if line[0] in "▌▶"
                else "call" if line.startswith("./pp") else "fragment")
        if current is None or (blank and kind in ("doc", "call")) \
                or (blank and kind == "render" and current[1] != "render") \
                or (blank and kind == "fragment" and current[1] in ("render", "call")):
            current = (section, kind, [])
            found.append(current)
        current[2].append(line)
        blank = False
    for _, _, lines in found:
        while lines and not lines[-1]:
            lines.pop()
    return found


def root_of(heading: str) -> str | None:
    """-> the document a rendering's heading opens on: the head of its stack."""
    match = HEADING.match(heading)
    if not match or "—" in heading or match.group("stack").strip() in PARTS:
        return None
    return match.group("stack").split(" ▸ ")[0].strip()


def outputs(lines: list[str]) -> list[list[str]]:
    """-> one list of lines per engine OUTPUT a rendering block shows: a new heading after a
    closing, or on another document, opens the next."""
    shown: list[list[str]] = []
    closed, root = False, None
    for line in lines:
        here = root_of(line) if line.startswith("▌ ") else None
        if here and (not shown or closed or here != root):
            shown.append([])
            closed, root = False, here
        elif not shown:
            shown.append([])
        shown[-1].append(line)
        if line.startswith("▶ "):
            closed = True
    return shown


def expected(lines: list[str]) -> list:
    """-> the tokens a shown rendering promises: literal lines, (prefix,) and GAPs."""
    tokens: list = []
    skip = False
    for line in lines:
        if not line:
            continue
        if line == STANDING:
            skip = True
            tokens.append(GAP)
            continue
        if skip and line == "…":
            skip = False
            continue
        skip = False
        if line == "…":
            tokens.append(GAP)
        elif line.endswith(" …"):
            tokens.append((line[:-2].rstrip(),))
            tokens.append(GAP)
        else:
            tokens.append(line)
    return tokens


def rendered(text: str) -> list[str]:
    """-> the engine's output as the sheet shows one: no output heading, no packages line,
    no standing orders, the key written `<key>`, no blank line."""
    kept: list[str] = []
    skip = False
    for line in text.splitlines():
        line = KEY.sub("./pp <key>", line.rstrip())
        if not line or line.startswith("▌ pp · ") or PACKAGES.match(line):
            continue
        if line == STANDING:
            skip = True
            continue
        if skip and (line.startswith("▌ ") or line.startswith("▶ ")):
            skip = False
        if not skip:
            kept.append(line)
    return kept


def mismatch(tokens: list, lines: list[str]) -> str | None:
    """-> None when every run of consecutive tokens appears in order in `lines`, else the
    first run that does not, with the lines it was looked for in."""
    runs: list[list] = [[]]
    for token in tokens:
        if token is GAP:
            if runs[-1]:
                runs.append([])
        else:
            runs[-1].append(token)
    runs = [run for run in runs if run]
    at = 0
    for run in runs:
        found = None
        for start in range(at, len(lines) - len(run) + 1):
            if all((lines[start + i].startswith(t[0]) if isinstance(t, tuple) else lines[start + i] == t)
                   for i, t in enumerate(run)):
                found = start
                break
        if found is None:
            want = " / ".join(t[0] + " …" if isinstance(t, tuple) else t for t in run)
            return f"missing {want!r}\n      in {' / '.join(lines[at:])!r}"
        at = found + len(run)
    return None


def home(name: str, body: str) -> str:
    """-> where a document of the sheet is installed: a proc under `procs/`, a served
    document or an overlay at the instance's root -- the two places the sheet names."""
    return f"procs/{name}.md" if "\nproc: |" in body else f"{name}.md"


def key(one) -> str:
    return persistence.run_id_of(one.session())


def play(env, member, section: str, items: list[tuple[str, list[str]]], first_proc: str | None) -> int:
    """Plays one section's calls and renderings in order on `env` (`member` boots the kit
    on the sheet's MEMBER) -> the renderings compared; the first gap raises, named."""
    root, compared = None, 0
    pending: str | None = None            # a call's rendering, awaiting its shown output
    for index, (kind, lines) in enumerate(items):
        if kind == "fragment":
            continue                          # a figure's cited lines: nothing plays
        if kind == "call":
            head = lines[0]
            ahead = next((root_of(l[0]) for k, l in items[index + 1:] if k == "render"), None)
            if root is None or (" -mount " in head and root != ahead):
                root = ahead or first_proc         # the run the call plays on
                env.conductor().forget()
                env.conductor().start(env.made / "procs" / f"{root}.md")
            if "<<'EOF'" in head:
                fed = "\n".join(lines[1:lines.index("EOF")])
                pending = render(env.conductor(key(env)).forward(fed))
            elif " -mount " in head:
                specs = json.loads(head.split(" -mount ", 1)[1].strip().strip("'"))
                pending = env.conductor(key(env)).mount(specs)
            elif " -s " in head:
                pending = None            # the sheet shows nothing after a gesture
            else:                         # a bare advance, or an inline value on the call
                value = head.split(" ", 2)[2].strip() if head.count(" ") >= 2 else ""
                pending = render(env.conductor(key(env)).forward(value))
            continue
        for shown in outputs(lines):
            here = (root_of(shown[0]) if shown[0].startswith("▌ ") else None) or first_proc
            if pending is not None:
                out, pending = pending, None
            elif here == "BOOT":
                member.conductor().forget()
                conductor = member.conductor()
                out = render(conductor.start(conductor.boot("BOOT.md")))
            elif here != root:
                env.conductor().forget()
                out = render(env.conductor().start(env.made / "procs" / f"{here}.md"))
            else:
                out = render(env.conductor(key(env)).forward(""))
            root = here
            gap = mismatch(expected(shown), rendered(out))
            assert gap is None, f"{section} -- {shown[0]}: {gap}"
            compared += 1
    return compared


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "authoring", "PP_CHEATSHEET").read_text(encoding="utf-8")
    parts = pieces(text)
    docs = {NAME.search("\n".join(lines)).group(1): "\n".join(lines) + "\n"
            for _, kind, lines in parts if kind == "doc"}
    env = bench.env("cheatsheet-examples", packages=("authoring", "doc"), pin=False)
    member = bench.env("cheatsheet-member", packages=("authoring", "doc"), pin=False)
    for one in (env, member):
        one.write("SETTINGS.md", SETTINGS)
        (one.root / "README.md").write_text("# the member's repository\n", encoding="utf-8")
        for name, body in docs.items():
            if name in FILE_OF and one is env:
                continue
            one.write(FILE_OF.get(name, home(name, body)), body)
    bench.held("every document of the sheet installs", f"{len(docs)} documents, the procs under procs/, {FILE_OF} at their file")

    total, blocks = 0, sum(1 for _, kind, _ in parts if kind == "render")
    for section in dict.fromkeys(s for s, _, _ in parts):
        items = [(k, l) for s, k, l in parts if s == section and k != "doc"]
        if not any(k == "render" for k, _ in items):
            continue
        first_proc = next((NAME.search("\n".join(l)).group(1)
                           for s, k, l in parts if s == section and k == "doc" and "proc: |" in l), None)
        compared = play(env, member, section, items, first_proc)
        total += compared
        bench.held(f"{section}: the renderings play", f"{compared} output(s) compared with the engine's")
    assert total >= blocks, (total, blocks)
    bench.held("every shown rendering was compared", f"{total} outputs for {blocks} rendering blocks")
    assert re.search(r"^    constraints\.production: \|", text, re.M) and not re.search(r"^    constraints: \|", text, re.M)
    bench.held("every example carries its section", "no bare key in the sheet's examples")
    assert all(f"| {form} |" in text for form in FORMS)
    bench.held("the sheet names every interaction form", " · ".join(FORMS[:6]) + " …")
    assert "The figures — what a package makes of the forms" in text and "Sixteen figures cover" in text
    assert all(f"### {figure}" in text for figure in FIGURES)
    bench.held("the sheet carries the sixteen figures", "each citing its real employer or the bench door that plays it")
    assert all(employer in text for employer in EMPLOYERS)
    assert "The served `CONDUCTION` says WHEN to choose each figure" in text
    bench.held("the described door, the workflow and the entry act cite the bench door that plays them", " · ".join(EMPLOYERS))
    assert all(key in text for key in KEYS)
    serve_row = next(line for line in text.splitlines() if line.startswith("| `serve:` |"))
    assert "[start..end]" in serve_row and text.count("prove-gone") == 1
    bench.held("the key table declares exec, field, next, choose/decide and sink", "the serve row says the tags, prove-gone said once")
    assert all(phrase in text for phrase in DOCTRINE)
    bench.held("the sheet carries the lived doctrine", "the proof's numbers, the two sections, the codes at risk")
    table = text.split("## 5. The front matter", 1)[1].split("## 6.", 1)[0]
    keys = [k.strip("`:") for cell in re.findall(r"^\| `([^|]+?)` \|", table, re.M) for k in cell.split("` / `")]
    lacking = [k for k in keys if not re.search(rf"^    {re.escape(k)}:", text, re.M)]
    assert len(keys) >= 24 and not lacking, lacking
    bench.held("every key of the table has an indented line", f"{len(keys)} keys, each opening a line of a document or a cited fragment")
    assert all(phrase in text for phrase in DUE)
    bench.held("the sheet says what the engine does since beta.8, each with the scenario that plays it",
               "the FINAL that names, the mount's overlays, the bare -s, the chunks, the package switch")
    return 0
