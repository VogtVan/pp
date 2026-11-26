"""Scenario `cut` -- 8 case(s):
- la-coupe-tient-le-cap: a block over the cap comes back in chunks, none over it
- la-matiere-est-entiere: the chunks carry the block's matter, byte for byte
- l-entete-ride-chaque-morceau: every chunk opens on the output's heading, run, hour and the packages' state
- la-tranche-qui-se-dit: an intermediate chunk says it is one and carries no instruction; the last carries the tail
- le-prouve-a-la-livraison: a document is proven when its last chunk has left, every chunk traced
- l-invariant-du-cap: whatever the matter, no output goes over the cap -- three regimes
- le-mount-sous-le-cap: a MOUNT's text is cut like any output, the rest on the bare calls
- la-vue-sous-le-cap: a VIEW (peek, keyless, denied) is clipped under the cap, nothing kept
- le-plafond-suit-l-appel-du-principal: `PP_PROMPT_CAP` on the principal's call is the cap of its
  outputs; without it the floor holds; a value that does not parse refuses `prompt-cap-invalid`; the
  variable is inert on the agent's call
- le-morceau-au-prompt-clot-more: a chunk before the last closes on `MORE` and the fact; the last chunk
  carries the block's own foot
The cases of the cut play under the launcher's cap (`PP_PROMPT_CAP`), the instance's setting beside it.
- la-queue-de-la-coupe: the steps of the last segment follow the last piece of matter, each with its
  context, its OPTIONS and its line -- whole in the last chunk when they fit; cut between two steps
  when they do not; a context larger than a chunk cut as a reading is, its line with its last piece;
  every chunk under the cap, every chunk but the last closed on the foot of a reading that continues
- la-vue-sans-seuil: a view cut under the cap cuts the matter first and shows the steps whole when
  they fit by themselves; when they do not, it cuts what they read and keeps their OPTIONS and lines
- le-groupe-sans-lecture: a group with nothing to read that does not fit has its OPTIONS cut as a
  reading is, its line with their last piece; a foot that waits alone is an output that waits
- le-skip-sous-le-plafond: `-skip` drops the matter that waits and nothing else; the steps that wait
  come by the same cut as any output, every chunk under the cap
- le-fait-d-un-morceau: the fact of a chunk counts all that is left to read, the matter and the
  steps, and the chunks still needed
- le-fait-derriere-un-texte-de-script: behind the text a script printed, the first chunk holds a
  smaller cap, and its fact still counts the chunks the bare calls serve under theirs
- le-groupe-insecable-partout: an output of two segments, cut in the first: whatever the size of the
  first step's brief under a chunk, each step of each segment stands in one chunk with its context, its
  OPTIONS and its line
- le-skip-laisse-tomber-les-tetes: an output of two segments, the second serving a long reading before its
  step, cut under the cap, then `-skip`: nothing of that reading nor of the second segment's heading is
  served; the group of each step that waits is, under the cap
"""
from __future__ import annotations

import json
import os
import re

from conductor.core import messages
from conductor import Conductor, discovery, persistence, rendering, settings
from conductor.core import language
from conductor.rendering.render import last_line
from conductor.state import context
from tests.harness import titled

LONGRUN = "---\nname: LONGRUN\nkind: proc\ndescription: a witness\nproc: |\n  SERVE LONG.md\n  WORK\n---\nread\n"


def _launcher_cap(cap: int | None) -> None:
    """The cap the principal's launcher names on its calls (`PP_PROMPT_CAP`), set in THIS process;
    None takes it away."""
    if cap is None:
        os.environ.pop(context.PROMPT_CAP, None)
    else:
        os.environ[context.PROMPT_CAP] = str(cap)


CAP = 2000
ASKED, LAWS = titled(language.INSTRUCTION), titled(language.CONSTRAINTS)   # two titles of the engine's list

# the witness of the tail: a root that calls TAILED -- two free steps under its brief, then the fork
# its `next:` injects under its own brief, with its OPTIONS; `{brief}` and `{fork}` size the two contexts
TAILROOT = "---\nname: TAILROOT\nkind: proc\ndescription: the root of the witness\nproc: |\n  CALL TAILED.md\n  INFER\n---\n\nroot\n"
TAILED = ("---\nname: TAILED\nkind: proc\ndescription: two steps, then a fork\nfusion: max\n"
          "next: LEFT.md RIGHT.md\nchoose: |\n{fork}proc: |\n  INFER\n  INFER\n---\n\n{brief}")
WAY = "---\nname: {name}\nkind: proc\ndescription: a way\nproc: |\n  INFER\n---\n\na way\n"
BRIEF, FORK = "brief line {n:04d} of the steps", "fork line {n:04d} of the choice"


def _tail(made, member, brief: int, fork: int) -> tuple[list[str], Conductor]:
    """-> the chunks of the witness's first output, its two contexts sized `brief` and `fork` lines,
    with the conductor that served them."""
    (made / "TAILED.md").write_text(TAILED.format(
        fork="".join(f"  {FORK.format(n=n)}\n" for n in range(fork)),
        brief="".join(f"{BRIEF.format(n=n)}\n" for n in range(brief))), encoding="utf-8")
    run = Conductor(member, made / ".sys" / "engine" / "pp.py")
    run.forget()
    chunks = [run.rendered(run.start(made / "TAILROOT.md"))]
    while run.pending() and len(chunks) < 400:
        chunks.append(run.next_chunk())
    return chunks, run


def _asked(chunk: str) -> list[str]:
    """-> the sections of a chunk that belong to a step's group, in order, read by the engine's list."""
    mark = f"{messages.MARK} "
    names = [language.section_of(line.removeprefix(mark))[0] for line in chunk.splitlines() if line.startswith(mark)]
    return [name for name in names if name in (language.CONTEXT, language.OPTIONS, language.INSTRUCTION)]


def _shape(text: str) -> str:
    """-> a text with its counts masked: what two feet of the same form share."""
    return re.sub(r"\d+", "N", text)


# the witness of a group with nothing to read: a list, a proof with nothing due, then a choice among it
PICKED = ("---\nname: PICKED\nkind: proc\ndescription: a list, then a choice among it\nproc: |\n"
          "  INFER\n  PROVE\n  PICK choice\n---\n\ngive the list\n")
CHOICE = "option {n:04d} of the long choice"


def view_cases(bench, made, member) -> None:
    """A view cut under the cap, no threshold: the matter first, then what the steps read."""
    held, failures = bench.held, bench.failures
    first, whole = [language.CONTEXT, language.INSTRUCTION], [language.CONTEXT, language.OPTIONS, language.INSTRUCTION]

    def viewed(brief: int, fork: int) -> tuple[str, bool]:
        """-> the view of the witness's first output, and whether it left anything waiting."""
        (made / "TAILED.md").write_text(TAILED.format(
            fork="".join(f"  {FORK.format(n=n)}\n" for n in range(fork)),
            brief="".join(f"{BRIEF.format(n=n)}\n" for n in range(brief))), encoding="utf-8")
        run = Conductor(member, made / ".sys" / "engine" / "pp.py")
        run.forget()
        view = run.shown(run.start(made / "TAILROOT.md"))
        kept = run.pending()
        run.forget()
        return view, kept

    def count(view: str, line: str) -> int:
        return sum(1 for one in view.splitlines() if one.startswith(line.split("{")[0]))

    def asked(view: str) -> int:
        return sum(1 for one in view.splitlines() if one.endswith("(TAILED)"))

    fit, fit_kept = viewed(34, 4)          # the steps weigh over half the cap and fit by themselves
    over, over_kept = viewed(150, 4)       # the first step's brief is larger than the cap
    if (len(fit) <= CAP and not fit_kept and _asked(fit) == first + whole
            and count(fit, BRIEF) == 34 and count(fit, FORK) == 4 and asked(fit) == 3
            and fit.rstrip().splitlines()[-1].startswith("   (")
            and len(over) <= CAP and not over_kept
            and _asked(over)[:2] == first and _asked(over)[-2:] == whole[-2:]
            and 0 < count(over, BRIEF) < 150 and asked(over) == 3
            and over.rstrip().splitlines()[-1].startswith("   (")):
        held("a view is cut without a threshold",
             f"steps that fit by themselves stand whole behind the matter that fits ({len(fit)} characters, "
             f"34 lines of brief); steps that do not have what they read cut, each in its turn "
             f"({count(over, BRIEF)} of 150 lines of the first brief shown in {len(over)} characters), and "
             "keep their OPTIONS and their three lines; one fact at the foot each, nothing kept")
    else:
        failures.append(f"  ✗ the view without threshold  fit={len(fit)} {_asked(fit)} brief={count(fit, BRIEF)} "
                        f"lines={asked(fit)} | over={len(over)} {_asked(over)} brief={count(over, BRIEF)} "
                        f"fork={count(over, FORK)} lines={asked(over)} kept={fit_kept}/{over_kept}")


def options_case(bench, made, member) -> None:
    """A group with nothing to read that does not fit: its OPTIONS cut, its line with their last piece."""
    held, failures = bench.held, bench.failures
    (made / "PICKED.md").write_text(PICKED, encoding="utf-8")
    offered = [CHOICE.format(n=n) for n in range(150)]
    run = Conductor(member, made / ".sys" / "engine" / "pp.py")
    run.forget()
    run.start(made / "PICKED.md")
    block = run.submit(json.dumps(offered))
    chunks = [run.rendered(block)]
    while run.pending() and len(chunks) < 400:
        chunks.append(run.next_chunk())
    read = [one for chunk in chunks for one in chunk.splitlines() if one.startswith(CHOICE.split("{")[0])]
    lined = [rank for rank, chunk in enumerate(chunks) if any(one.endswith("(PICKED)") for one in chunk.splitlines())]
    last = chunks[-1].splitlines()
    idle = [one for one in last if one.startswith("   (")]
    # a foot that waits alone: the run says an output waits, and the bare call serves it
    slot = persistence.slots(made)[0]
    head, foot = rendering.head(block), rendering.foot("", "", ("a fact of the foot",))
    persistence.set_pending(slot, {"head": head, "matter": "", "steps": [], "tail": foot, "cap": CAP})
    waited = run.pending()
    served = run.next_chunk() if waited else ""
    if (block.options == tuple(offered) and len(chunks) > 2 and all(len(one) <= CAP for one in chunks)
            and read == offered and lined == [len(chunks) - 1]
            and any(one.startswith(CHOICE.split("{")[0]) for one in last)
            and last.index(next(one for one in last if one.endswith("(PICKED)"))) > max(
                rank for rank, one in enumerate(last) if one.startswith(CHOICE.split("{")[0]))
            and not idle
            and waited and served == rendering.joined(head, foot) and not run.pending()):
        held("a group with nothing to read has its OPTIONS cut",
             f"{len(offered)} options in {len(chunks)} chunks under {CAP}, each once and in order; the line of "
             "the choice in the last chunk, behind the last piece of its OPTIONS, no fact under it -- the idle PROVE "
             "says nothing; "
             "a foot that waits alone is served by the bare call")
    else:
        failures.append(f"  ✗ the group without reading   n={len(chunks)} sizes={[len(one) for one in chunks]} "
                        f"read={len(read)}/{read == offered} lined={lined} idle={idle} waited={waited} "
                        f"served={served == rendering.joined(head, foot)}")
    run.forget()


def _fact(chunk: str) -> tuple[int, int]:
    """-> (the characters left, the chunks still needed) the fact at the foot of a chunk counts."""
    counts = re.findall(r"\d+", chunk.rstrip().splitlines()[-1])
    return (int(counts[0]), int(counts[1])) if len(counts) == 2 else (-1, -1)


def _body(chunk: str, head: str) -> str:
    """-> what a chunk carries of its output: the chunk less the heading it opens on and its foot."""
    lines = chunk[len(head):].splitlines()
    at = next((rank for rank, one in enumerate(lines) if one.startswith(f"{messages.SIGNAL} ")), len(lines))
    return "\n".join(lines[:at]).strip("\n")


def skip_and_fact_cases(bench, made, member) -> None:
    """`-skip` under the cap, and what the fact of a chunk counts."""
    held, failures = bench.held, bench.failures
    first, whole = [language.CONTEXT, language.INSTRUCTION], [language.CONTEXT, language.OPTIONS, language.INSTRUCTION]

    def count(chunks: list[str], line: str) -> int:
        return sum(1 for chunk in chunks for one in chunk.splitlines() if one.startswith(line.split("{")[0]))

    # --- -skip: the matter that waits is dropped, the steps come under the cap -------------------
    skipped = {}
    for name, brief in (("between two steps", 34), ("a brief over the cap", 150)):
        (made / "TAILED.md").write_text(TAILED.format(
            fork="".join(f"  {FORK.format(n=n)}\n" for n in range(34)),
            brief="".join(f"{BRIEF.format(n=n)}\n" for n in range(brief))), encoding="utf-8")
        run = Conductor(member, made / ".sys" / "engine" / "pp.py")
        run.forget()
        opening = run.rendered(run.start(made / "TAILROOT.md"))
        served = [run.drop_pending()]
        while run.pending() and len(served) < 400:
            served.append(run.next_chunk())
        dropped = [one for one in served if "standing orders" in one or len(one) > CAP]
        skipped[name] = (len(opening) <= CAP and not dropped
                         and [name_ for one in served for name_ in _asked(one)] == first + whole
                         and count(served, BRIEF) == brief and count(served, FORK) == 34
                         and not run.pending(), [len(one) for one in served])
        run.forget()
    if all(ok for ok, _ in skipped.values()):
        held("-skip drops the matter and serves the steps under the cap",
             "; ".join(f"{name}: {len(sizes)} output(s) after the skip, the largest {max(sizes)}"
                       for name, (_, sizes) in skipped.items())
             + f" under {CAP} -- the two steps with what they read whole, nothing of the matter that waited")
    else:
        failures.append(f"  ✗ -skip under the cap         {skipped}")

    # --- the fact of a chunk: all that is left to read, the chunks still needed ------------------
    chunks, run = _tail(made, member, 34, 34)
    head = chunks[0].split("\n\n", 1)[0]
    facts = [_fact(one) for one in chunks[:-1]]
    carried = [len(_body(one, head)) for one in chunks]
    # what a fact counts against what the chunks behind it carry: the seams a cut eats apart
    drift = [abs(left - sum(carried[rank + 1:])) for rank, (left, _) in enumerate(facts)]
    if (len(chunks) > 3 and [more for _, more in facts] == list(range(len(chunks) - 1, 0, -1))
            and all(one <= 4 * (len(chunks) - rank) for rank, one in enumerate(drift))
            and [left for left, _ in facts] == sorted((left for left, _ in facts), reverse=True)):
        held("the fact of a chunk counts all that is left",
             f"{len(chunks)} chunks: each fact counts the chunks still needed, {facts[0][1]} down to 1, and the "
             f"characters the chunks behind it carry, matter and steps ({facts[0][0]} down to {facts[-1][0]})")
    else:
        failures.append(f"  ✗ the fact of a chunk         n={len(chunks)} facts={facts[-4:]} "
                        f"carried={carried[-4:]} drift={drift[-4:]}")
    run.forget()


def lead_case(bench, made, member) -> None:
    """Behind a script's text, the fact of the first chunk counts the chunks the bare calls serve."""
    held, failures = bench.held, bench.failures
    (made / "TAILED.md").write_text(TAILED.format(
        fork="".join(f"  {FORK.format(n=n)}\n" for n in range(34)),
        brief="".join(f"{BRIEF.format(n=n)}\n" for n in range(34))), encoding="utf-8")
    counted = {}
    for size in (60, 400, 900):                 # a script's text, under half the cap: it opens the output
        lead = "\n".join(["a line of the script's own text"] * (size // 32))
        run = Conductor(member, made / ".sys" / "engine" / "pp.py")
        run.forget()
        chunks = [run.rendered(run.start(made / "TAILROOT.md"), lead)]
        while run.pending() and len(chunks) < 400:
            chunks.append(run.next_chunk())
        counted[len(lead)] = (chunks[0].startswith(lead), len(chunks[0]), _fact(chunks[0])[1], len(chunks) - 1,
                              max(len(one) for one in chunks))
        run.forget()
    if all(opened and first <= CAP and said == served and largest <= CAP
           for opened, first, said, served, largest in counted.values()) and len(counted) == 3:
        held("the fact behind a script's text counts the chunks served",
             "; ".join(f"behind {size} characters, {said} more chunk(s) said and {served} served"
                       for size, (_, _, said, served, _) in counted.items())
             + f" -- the first chunk under {CAP} with the text that opens it")
    else:
        failures.append(f"  ✗ the fact behind a script    {counted}")


def tail_cases(bench, made, member) -> None:
    """The steps of the last segment under the cap: whole, cut between two steps, a context cut."""
    held, failures = bench.held, bench.failures
    (made / "SETTINGS.md").write_text(
        f"---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {CAP}\n---\n", encoding="utf-8")
    (made / "TAILROOT.md").write_text(TAILROOT, encoding="utf-8")
    for name in ("LEFT", "RIGHT"):
        (made / f"{name}.md").write_text(WAY.format(name=name), encoding="utf-8")
    first, whole = [language.CONTEXT, language.INSTRUCTION], [language.CONTEXT, language.OPTIONS, language.INSTRUCTION]

    def closed(chunks: list[str], run: Conductor) -> bool:
        """Whether every chunk holds the cap and every chunk but the last closes on the foot of a
        reading that continues, the last one on none."""
        label, call, fact = run.closing(language.READING_ON, language.PROMPT, left=0, more=0)
        waiting = _shape(rendering.foot(label, call, (fact,)))
        tall = len(waiting.strip("\n").splitlines())             # the lines a foot holds
        feet = [_shape("\n" + "\n".join(one.splitlines()[-tall:])) for one in chunks]
        return (all(len(one) <= CAP for one in chunks) and all(foot == waiting for foot in feet[:-1])
                and feet[-1] != waiting)

    def lines_of(chunk: str, line: str) -> int:
        return sum(1 for one in chunk.splitlines() if one.startswith(line.split("{")[0]))

    # (1) a tail that fits: every step of the last segment in the last chunk
    chunks, run = _tail(made, member, 4, 4)
    if (len(chunks) > 1 and closed(chunks, run) and not any(_asked(one) for one in chunks[:-1])
            and _asked(chunks[-1]) == first + whole
            and lines_of(chunks[-1], BRIEF) == 4 and lines_of(chunks[-1], FORK) == 4):
        held("a tail that fits follows the last piece of matter whole",
             f"{len(chunks)} chunks under {CAP}: the two steps under their brief, then the fork under its "
             "own with its OPTIONS, all in the last chunk; every chunk before it closes on the reading")
    else:
        failures.append(f"  ✗ the tail that fits          n={len(chunks)} sizes={[len(one) for one in chunks][-3:]} "
                        f"asked={[_asked(one) for one in chunks][-3:]}")

    # (2) a tail that does not fit: cut between two steps, each group whole in its chunk
    chunks, run = _tail(made, member, 34, 34)
    carried = [(rank, _asked(one)) for rank, one in enumerate(chunks) if _asked(one)]
    if (closed(chunks, run) and [asked for _, asked in carried] == [first, whole]
            and carried[-1][0] == len(chunks) - 1
            and lines_of(chunks[carried[0][0]], BRIEF) == 34 and lines_of(chunks[carried[1][0]], FORK) == 34):
        held("a tail that does not fit is cut between two steps",
             f"{len(chunks)} chunks under {CAP}: the two steps with their whole brief in chunk "
             f"{carried[0][0] + 1}, closed on the reading; the fork with its whole brief, its OPTIONS and its "
             "line in the last")
    else:
        failures.append(f"  ✗ the tail cut between steps  n={len(chunks)} sizes={[len(one) for one in chunks][-3:]} "
                        f"carried={carried}")

    # (3) a context larger than a chunk: cut as a reading is, its lines with its last piece
    chunks, run = _tail(made, member, 150, 4)
    spread = [rank for rank, one in enumerate(chunks) if lines_of(one, BRIEF)]
    opened = [rank for rank, one in enumerate(chunks) if _asked(one)[:1] == [language.CONTEXT]]
    ended = [rank for rank, one in enumerate(chunks) if BRIEF.format(n=149) in one]
    if (closed(chunks, run) and len(spread) > 1 and spread == list(range(spread[0], spread[-1] + 1))
            and sum(lines_of(one, BRIEF) for one in chunks) == 150
            and opened[:1] == spread[:1] and _asked(chunks[spread[0]]) == [language.CONTEXT]
            and not any(_asked(chunks[rank]) for rank in spread[1:-1])
            and ended == spread[-1:] and _asked(chunks[ended[0]])[:1] == [language.INSTRUCTION]
            and [name for one in chunks for name in _asked(one)] == first + whole):
        held("a context larger than a chunk is cut as a reading is",
             f"{len(chunks)} chunks under {CAP}: the brief opens in chunk {spread[0] + 1} under its title "
             f"and runs to chunk {spread[-1] + 1}, where the lines of its steps follow its last piece; "
             "every chunk before the last closes on the reading")
    else:
        failures.append(f"  ✗ the context cut             n={len(chunks)} sizes={[len(one) for one in chunks][-4:]} "
                        f"spread={spread} opened={opened} ended={ended} "
                        f"asked={[_asked(one) for one in chunks][-4:]}")
    run.forget()


# the witness of two segments: a root that calls SEGA -- one step under its brief -- then SEGB -- one step,
# then the fork its `next:` injects under its own brief, with its OPTIONS; `{brief}` sizes the context of the
# first segment's step, `{fork}` the fork's
SEGROOT = ("---\nname: SEGROOT\nkind: proc\ndescription: the root of two segments\nproc: |\n"
           "  CALL SEGA.md\n  CALL SEGB.md\n  INFER\n---\n\nroot\n")
SEGA = ("---\nname: SEGA\nkind: proc\ndescription: one step under its brief\nfusion: max\nproc: |\n  INFER\n"
        "---\n\n{brief}")
SEGB = ("---\nname: SEGB\nkind: proc\ndescription: one step, then a fork\nfusion: max\nnext: LEFT.md RIGHT.md\n"
        "choose: |\n{fork}proc: |\n  INFER\n---\n\nthe second segment's brief\n")


def segments_case(bench, made, member) -> None:
    """The group of a step holds in one chunk in every segment of an output, not in the last alone."""
    held, failures = bench.held, bench.failures
    (made / "SEGROOT.md").write_text(SEGROOT, encoding="utf-8")
    (made / "SEGB.md").write_text(SEGB.format(fork="".join(f"  {FORK.format(n=n)}\n" for n in range(20))),
                                  encoding="utf-8")
    groups = [[language.CONTEXT, language.INSTRUCTION], [language.CONTEXT, language.INSTRUCTION],
              [language.CONTEXT, language.OPTIONS, language.INSTRUCTION]]
    split, played, early = [], 0, 0
    run = None
    for size in range(8, 56):
        (made / "SEGA.md").write_text(SEGA.format(
            brief="".join(f"{BRIEF.format(n=n)}\n" for n in range(size))), encoding="utf-8")
        run = Conductor(member, made / ".sys" / "engine" / "pp.py")
        run.forget()
        chunks = [run.rendered(run.start(made / "SEGROOT.md"))]
        while run.pending() and len(chunks) < 400:
            chunks.append(run.next_chunk())
        asked = [_asked(one) for one in chunks]
        first = next((rank for rank, one in enumerate(chunks) if "(SEGA)" in one), -1)
        whole = (all(len(one) <= CAP for one in chunks)
                 and [name for one in asked for name in one] == [name for one in groups for name in one]
                 and all(not one or (one[0] == language.CONTEXT and one[-1] == language.INSTRUCTION) for one in asked)
                 and first >= 0 and sum(1 for line in chunks[first].splitlines()
                                        if line.startswith(BRIEF.split("{")[0])) == size)
        played += 1
        early += 1 if 0 <= first < len(chunks) - 1 else 0
        if not whole:
            split.append((size, [one for one in asked if one]))
    if played and not split and early:
        held("the group of a step holds in one chunk in every segment",
             f"{played} outputs of two segments, the first step's brief from 8 to 55 lines, each cut under {CAP}: "
             "the step of the first segment stands with its whole brief and its line in one chunk, the step and "
             f"the fork of the second with theirs; in {early} of them the first segment's step leaves before "
             "the last chunk")
    else:
        failures.append(f"  ✗ the group in every segment  played={played} early={early} split={split[:4]}")
    if run is not None:
        run.forget()


# the second segment of the witness, with a long reading at its head: SEGLONG serves READ before its one step
SEGLONG = ("---\nname: SEGB\nkind: proc\ndescription: a long reading, then one step\nfusion: max\nproc: |\n"
           "  SERVE READ.md\n  INFER\n---\n\nthe second segment's brief\n")
READ = "reading line {n:04d} of the second segment"


def skip_heads_case(bench, made, member) -> None:
    """`-skip` drops the head of every segment that waits, and serves the groups of the steps alone."""
    held, failures = bench.held, bench.failures
    (made / "SEGROOT.md").write_text(SEGROOT, encoding="utf-8")
    (made / "SEGA.md").write_text(SEGA.format(brief="".join(f"{BRIEF.format(n=n)}\n" for n in range(10))),
                                  encoding="utf-8")
    (made / "SEGB.md").write_text(SEGLONG, encoding="utf-8")
    (made / "READ.md").write_text("---\nname: READ\nkind: doc\n---\n\n"
                                  + "".join(f"{READ.format(n=n)}\n" for n in range(300)), encoding="utf-8")
    run = Conductor(member, made / ".sys" / "engine" / "pp.py")
    run.forget()
    opening = run.rendered(run.start(made / "SEGROOT.md"))
    served = [run.drop_pending()]
    while run.pending() and len(served) < 400:
        served.append(run.next_chunk())
    lines = [line for one in served for line in one.splitlines()]
    read = sum(1 for line in lines if line.startswith(READ.split("{")[0]))
    headed = [line for line in lines if line.startswith(f"{messages.MARK} ") and "SEGB{" in line]
    asked = [sum(1 for line in lines if line.endswith(f"({name})")) for name in ("SEGA", "SEGB")]
    brief = sum(1 for line in lines if line.startswith(BRIEF.split("{")[0]))
    if (len(opening) <= CAP and all(len(one) <= CAP for one in served) and not read and not headed
            and asked == [1, 1] and brief == 10 and not run.pending()):
        held("-skip drops the head of every segment that waits",
             f"two segments, 300 lines of reading at the head of the second: {len(served)} output(s) after the "
             f"skip, the largest {max(len(one) for one in served)} under {CAP} -- no line of that reading, no "
             "heading of the second segment; the step of the first segment under its whole brief and the step "
             "of the second, once each")
    else:
        failures.append(f"  ✗ -skip and the heads         outputs={len(served)} "
                        f"sizes={[len(one) for one in served][:4]} read={read} headed={len(headed)} "
                        f"asked={asked} brief={brief} pending={run.pending()}")
    run.forget()


def scenario(bench) -> int:
    entry = os.environ.get(context.PROMPT_CAP)
    _launcher_cap(CAP)
    try:
        return _scenario(bench)
    finally:
        _launcher_cap(int(entry) if entry else None)


def _scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    made = bench.env("cut").made
    (made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 2000\n---\n", encoding="utf-8")
    member = discovery.instance_member(made / ".sys" / "engine" / "pp.py")
    conductor = Conductor(member, made / ".sys" / "engine" / "pp.py")
    block = conductor.resume(conductor.boot("BOOT.md"))
    whole, tail = rendering.parts(block)

    chunks = [conductor.rendered(block)]
    while conductor.pending() and len(chunks) < 200:
        chunks.append(conductor.next_chunk())

    over = [len(one) for one in chunks if len(one) > CAP]
    if len(chunks) > 1 and not over:
        held("the cut holds the cap",
             f"{len(chunks)} chunks, none over {CAP} -- the block was {len(whole) + len(tail)} characters")
    else:
        failures.append(f"  ✗ cut over the cap            {len(chunks)} chunk(s), over: {over}")

    # the head comes with the tail: a chunk arriving alone still says which run it is from
    head = rendering.head(block)
    strayed = [one[:40] for one in chunks if not one.startswith(head)]
    if head and not strayed:
        held("the head comes with every chunk", f"`{head}` opens each of the {len(chunks)} chunks -- "
             "no piece arrives without saying which run it comes from")
    else:
        failures.append(f"  ✗ head off a chunk            {head!r} {strayed[:1]}")

    # the packages' state belongs to that heading: it rides every chunk by the same seam,
    # never by a second mechanism -- the pairs are posed here, the instance pinning none
    from dataclasses import replace
    switched = replace(block, switches=(("alpha", ""), ("beta", "alpha")))
    state = f"{messages.MARK} alpha on · beta off (<- alpha)"
    switched_head = rendering.head(switched)
    matter, rode = rendering.parts(switched)[0], []
    while matter:
        piece, matter = rendering.cut(matter, CAP - len(tail))
        rode.append(rendering.under(switched_head, piece))
    if state in switched_head and len(rode) > 1 and all(state in one for one in rode):
        held("the packages' state rides every chunk", f"the state line opens each of the "
             f"{len(rode)} chunks with the heading -- it IS the heading's second line, so the "
             "cut carries it without knowing it exists")
    else:
        failures.append(f"  ✗ state off a chunk           {switched_head!r} {len(rode)} chunk(s)")

    # the matter of a chunk is the chunk minus the tail that rides it: the last one carries
    # the block's own closing, the others the bare call back
    seen, rest = [], whole
    while rest:
        piece, rest = rendering.cut(rest, CAP - len(tail))
        seen.append(piece)
    if "".join(seen) == whole:
        held("the matter comes back whole", "the chunks' matter concatenates to the block's, byte for byte")
    else:
        failures.append("  ✗ matter lost                 the concatenation is not the block's matter")

    # --- l-invariant-du-cap: the PERMANENT guard, on matter the scenario poses itself ----
    # the composition is `kit` alone and both the matter and the CAP are written here: the
    # invariant answers for the MECHANISM, never for what a real composition weighs (KPS17).
    # Three regimes, the cap moving around the block: it fits, it just overflows, it dwarfs.
    (made / "MATTER.md").write_text("m" * 1000 + "\n", encoding="utf-8")
    (made / "MATTERRUN.md").write_text(
        "---\nname: MATTERRUN\nproc: |\n  SERVE MATTER.md\n  INFER\n---\n", encoding="utf-8")
    regimes, broken = [], False
    for label, cap in (("it fits", 40000), ("it just overflows", 20000), ("it dwarfs", 2000)):
        (made / "SETTINGS.md").write_text(
            f"---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {cap}\n---\n", encoding="utf-8")
        _launcher_cap(cap)
        run = Conductor(member, made / ".sys" / "engine" / "pp.py")
        run.forget()
        posed = run.start(made / "MATTERRUN.md")
        posed_matter, posed_tail = rendering.parts(posed)
        pieces = [run.rendered(posed)]
        while run.pending() and len(pieces) < 400:
            pieces.append(run.next_chunk())
        biggest = max(len(one) for one in pieces)
        regimes.append(f"cap {cap}: block {len(posed_matter) + len(posed_tail)} -> "
                       f"{len(pieces)} chunk(s), biggest {biggest}")
        rebuilt, rest = [], posed_matter
        while rest:
            piece, rest = rendering.cut(rest, cap - len(posed_tail))
            rebuilt.append(piece)
        if biggest > cap or "".join(rebuilt) != posed_matter or (cap == 40000 and len(pieces) != 1):
            failures.append(f"  ✗ cap invariant ({label})    {regimes[-1]}")
            broken = True
            break
        run.forget()
    _launcher_cap(CAP)
    if not broken:
        held("no output goes over the cap", " | ".join(regimes))

    # --- la-tranche-qui-se-dit (rework of 2026-09-09): an intermediate chunk carries no
    # instruction and closes on the reading itself; the block's own tail rides the LAST
    middles, last = chunks[:-1], chunks[-1]
    said = [one for one in middles if "a reading continues" in one and one.rstrip().endswith("more chunk(s))")
            and f"{messages.SIGNAL} {language.MORE}" in one and ASKED not in one.splitlines()]
    if len(said) == len(middles) and last.endswith(tail.rstrip("\n").splitlines()[-1]) \
            and (ASKED in last or "▌ END" in last or not block.command):
        held("a chunk says it is a chunk",
             f"each of the {len(middles)} intermediate chunks closes on `MORE` and the count of "
             "what remains, nothing more, and carries no instruction; the last "
             "chunk alone carries the block's own tail -- nothing invites a production before the reading is whole")
    else:
        failures.append(f"  ✗ chunk without its word      {len(said)}/{len(middles)} intermediate chunks said the reading; last={last[-160:]!r}")

    # --- le-prouve-a-la-livraison: a document is proven when its last chunk has left ------
    proved = Conductor(member, made / ".sys" / "engine" / "pp.py")
    proved.forget()
    (made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 2000\n---\n", encoding="utf-8")
    (made / "LONG.md").write_text("---\nname: LONG\nkind: doc\n---\n\n" + ("long line of matter\n" * 200) + "\n", encoding="utf-8")
    (made / "LONGRUN.md").write_text(
        "---\nname: LONGRUN\nproc: |\n  SERVE LONG.md\n  INFER\n---\n", encoding="utf-8")
    from conductor import persistence
    first = proved.rendered(proved.start(made / "LONGRUN.md"))
    slot = next(iter(sorted((made / ".sys" / "state").glob("session-*.json"))), None)
    import json as _json
    early = _json.loads(slot.read_text(encoding="utf-8")) if slot else {}
    staged_early, proven_early = len(early.get("pending", {}).get("staged", [])), len(early.get("proven", []))
    served_chunks = 1
    while proved.pending() and served_chunks < 400:
        proved.next_chunk()
        served_chunks += 1
    late = _json.loads(slot.read_text(encoding="utf-8")) if slot else {}
    proven_late = len(late.get("proven", []))
    kinds = [_json.loads(one).get("kind") for one in (made / ".sys" / "state" / early.get("log", "x")).read_text(encoding="utf-8").splitlines()] if slot and (made / ".sys" / "state" / early.get("log", "x")).exists() else []
    if (served_chunks > 1 and staged_early >= 1 and proven_early == 0 and proven_late >= 1
            and kinds.count("chunk") == served_chunks - 1 and kinds.count("cut") >= 1):
        held("a document is proven when its last chunk has left, and every chunk is traced",
             f"after the first chunk the reading stands STAGED ({staged_early}) and the run proves nothing; "
             f"once the {served_chunks} chunks are served the proof lands ({proven_late}); the trace says "
             f"`cut` then {kinds.count('chunk')} `chunk` -- whether the agent drained is read at the journal")
    else:
        failures.append(f"  ✗ proven at delivery          chunks={served_chunks} staged={staged_early} proven={proven_early}->{proven_late} kinds={ {k: kinds.count(k) for k in set(kinds)} }")
    proved.forget()
    # --- le-mount-sous-le-cap: a MOUNT's text goes through the ONE cut ---------------------
    # before the fix `mount()` returned a bare render: 41 610 characters in one output on a
    # real plan (core, 2026-08-26) -- the one text of the engine that could exceed the cap
    (made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 2000\n---\n", encoding="utf-8")
    (made / "BIG.md").write_text(
        "---\nname: BIG\nkind: doc\n---\n\n" + ("big matter line\n" * 300) + "\n",
        encoding="utf-8")
    host = Conductor(member, made / ".sys" / "engine" / "pp.py")
    host.forget()
    booted = host.start(host.boot("BOOT.md"))   # the boot block, over the cap: the view's matter
    view = host.shown(booted)                  # a VIEW never taints the conductor (a peek would)
    view_kept = host.pending()
    mounted = [host.mount([{"doc": "BIG.md", "body": True}])]
    while host.pending() and len(mounted) < 400:
        mounted.append(host.next_chunk())
    mount_over = [len(one) for one in mounted if len(one) > CAP]
    if len(mounted) > 1 and not mount_over and "big matter line" in "".join(mounted):
        held("a mount is cut like any output",
             f"{len(mounted)} chunks, none over {CAP} -- the mounted body came through whole")
    else:
        failures.append(f"  ✗ mount over the cap          {len(mounted)} chunk(s), over: {mount_over}")

    # --- la-vue-sous-le-cap: a VIEW is clipped, and keeps nothing at the run ----------------
    if (booted is not None and len(rendering.render(booted)) > CAP and len(view) <= CAP
            and view.rstrip().splitlines()[-1].startswith("   (") and not view_kept):
        held("a view is clipped under the cap",
             f"the view of a {len(rendering.render(booted))}-character block shows {len(view)}, "
             "says it is cut by one fact at its foot, and leaves no chunk waiting")
    else:
        failures.append(f"  ✗ view over the cap           {len(view)} kept={view_kept}")

    host.forget()
    tail_cases(bench, made, member)
    view_cases(bench, made, member)
    options_case(bench, made, member)
    skip_and_fact_cases(bench, made, member)
    lead_case(bench, made, member)
    segments_case(bench, made, member)
    skip_heads_case(bench, made, member)

    # --- le-plafond-suit-l-appel-du-principal: the cap of a principal's output is the launcher's ----
    # the one rule, `settings.served_cap`: the floor without the variable, the variable's value with
    # it, a tool's result under the setting untouched, 0 cutting nothing
    _launcher_cap(None)
    floor = settings.PRINCIPAL_CAP
    ruled = {(20000, True, None): floor, (20000, True, 2000000): 2000000, (20000, True, 50000): 50000,
             (300000, True, None): 300000, (20000, False, 2000000): 20000, (0, True, 2000000): 0}
    got = {triple: settings.served_cap(*triple) for triple in ruled}
    # the reader of the variable: on the principal's call alone, a number or a refusal
    def capped(agents: bool, value: str | None):
        spot = {name: os.environ.get(name) for name in (context.CONDUCTED_RUN, context.PROMPT_CAP)}
        for name, given in ((context.CONDUCTED_RUN, "k00001" if agents else None), (context.PROMPT_CAP, value)):
            if given is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = given
        try:
            return context.prompt_cap("k00001")
        except Exception as refused:          # noqa: BLE001 -- the refusal's code is what the case reads
            return getattr(refused, "code", type(refused).__name__)
        finally:
            for name, was in spot.items():
                if was is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = was
    read = {"principal": capped(False, "2000000"), "agent": capped(True, "2000000"),
            "absent": capped(False, None), "odd": capped(False, "plenty"), "zero": capped(False, "0")}
    if (got == ruled and read["principal"] == 2000000 and read["agent"] is None and read["absent"] is None
            and read["odd"] == "prompt-cap-invalid" and read["zero"] == "prompt-cap-invalid"):
        held("the cap follows the principal's call", f"served_cap: {ruled}; PP_PROMPT_CAP read on the "
             "principal's call alone (2000000), None on the agent's or absent, `plenty` and `0` refuse prompt-cap-invalid")
    else:
        failures.append(f"  ✗ the launcher's cap          got={got} read={read}")

    # the rendering: a 300 000-character block served WHOLE under PP_PROMPT_CAP=2000000,
    # in two chunks without the variable (the floor), cut under 2 000 000 with a bigger block
    capped_env = bench.env("prompt-cap")
    capped_env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 20000\n---\n")
    capped_env.write("LONG.md", "---\nname: LONG\nkind: doc\n---\n\n" + "long line of matter\n" * 15000 + "\n")
    capped_env.write("procs/LONGRUN.md", LONGRUN)
    capped_env.write("HUGE.md", "---\nname: HUGE\nkind: doc\n---\n\n" + "long line of matter\n" * 125000 + "\n")
    capped_env.write("procs/HUGERUN.md", LONGRUN.replace("LONGRUN", "HUGERUN").replace("LONG.md", "HUGE.md"))

    caps: list = []

    def served(doc: str, value: str | None) -> list[int]:
        """-> the sizes of the chunks the output comes in, the principal's calls serving the rest."""
        conductor = capped_env.conductor()
        conductor.forget()
        spot = os.environ.get(context.PROMPT_CAP)
        if value is None:
            os.environ.pop(context.PROMPT_CAP, None)
        else:
            os.environ[context.PROMPT_CAP] = value
        try:
            block = conductor.start(capped_env.made / "procs" / doc)
            sizes = [len(conductor.rendered(block))]
            while conductor.pending() and len(sizes) < 50:
                sizes.append(len(conductor.next_chunk()))
            caps.append((conductor._cap(), value))
        finally:
            if spot is None:
                os.environ.pop(context.PROMPT_CAP, None)
            else:
                os.environ[context.PROMPT_CAP] = spot
        return sizes

    whole = served("LONGRUN.md", "2000000")
    floored = served("LONGRUN.md", None)
    huge = served("HUGERUN.md", "2000000")
    # the first seam of a block is a section boundary: the first chunk is short, the body comes after,
    # cut at a line under the cap -- what the case reads is the cap each chunk holds and how many come
    if (len(whole) == 1 and whole[0] > 290000
            and len(floored) > 1 and max(floored) <= floor and sum(floored) > 290000
            and len(huge) > 1 and floor < max(huge) <= 2000000 and sum(huge) > 2400000):
        held("the principal's output is served under the launcher's cap", f"300 000 characters in ONE output "
             f"({whole[0]}) under PP_PROMPT_CAP=2000000; {len(floored)} chunks under the floor without it "
             f"(the biggest {max(floored)}); a 2 500 000-character block in {len(huge)} chunks under 2 000 000 "
             f"(the biggest {max(huge)}, over the floor)")
    else:
        failures.append(f"  ✗ the output under the cap    whole={whole} floored={floored} huge={huge} caps={caps}")

    # --- le-morceau-au-prompt-clot-more: the foot of a chunk -------------------------------------
    led = capped_env.conductor()
    led.forget()
    led_block = led.start(capped_env.made / "procs" / "LONGRUN.md")
    led_chunks = [led.rendered(led_block)]
    while led.pending() and len(led_chunks) < 50:
        led_chunks.append(led.next_chunk())
    more = f"{messages.SIGNAL} {language.MORE}"

    def foot_of(text: str) -> list[str]:
        lines = text.splitlines()
        at = max((i for i, one in enumerate(lines) if one.startswith("▶ ")), default=len(lines))
        return lines[at:]

    work = f"WORK any => {language.TERMINAL}"        # the last step of LONGRUN: said on `terminal`
    led_feet = [foot_of(one) for one in led_chunks[:-1]]
    checks = {"led_more": all(foot[0] == more and len(foot) == 2 and foot[1].startswith(messages.fact(messages.READING)[:-1])
                              for foot in led_feet),
              "led_nocall": all("./pp" not in "\n".join(foot) for foot in led_feet),
              "asked_led": all(ASKED not in one.splitlines() and last_line("LONGRUN") not in one
                               and not any(line.startswith(LAWS) for line in one.splitlines())
                               for one in led_chunks[:-1]),
              "work_led": work in led_chunks[-1], "last_led": not foot_of(led_chunks[-1])}
    if len(led_chunks) > 1 and all(checks.values()):
        held("a chunk closes on MORE", f"{len(led_chunks) - 1} chunk(s) close on `{more}` and the fact, no call; "
             "no CONSTRAINTS, no INSTRUCTION and no line added above the MORE; the last chunk carries the WORK "
             "on `terminal` and no foot, the step pending")
    else:
        failures.append(f"  ✗ the chunk's foot            checks={checks} led={led_feet[:1]} "
                        f"last={foot_of(led_chunks[-1])!r} n={len(led_chunks)}")
    return 0
