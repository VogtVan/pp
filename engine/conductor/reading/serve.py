"""reading.serve -- the ONE reader of the three sites (a section's line, a mount's
row, a CALLed body): the resolution of a name through the member's search paths,
the serve plan of a section, the line-bound cut at the room, the proof by hash.
The mixin of the facade that holds it: the room, the proven tags and the payloads
are the facade's state, read here."""
from __future__ import annotations

import os
from pathlib import Path

from ..core import document, language
from ..core.model import Document
from ..core.tokens import split_row
from ..core.errors import Refusal
from ..state import instance, persistence, settings
from .tokens import ranged, sliced, spanned
from .composition import Composing

MATERIALS = "materials"   # the front-matter key a document DECLARES its trees under


def _retired(name: str) -> str:
    """-> what a refusal says of a name no tree takes."""
    return (f"no tree is called `{name}`: a document declares its trees (`{MATERIALS}:`) and names one of "
            "them; a row that names none reads the run's own tree, or the repository")


def materials(declarer: Document) -> tuple[tuple[str, str], ...]:
    """-> the TREES a document declares, (name, path) pairs in the order written: its
    `materials:` block, one `<name>: <path>` a line. The path is absolute or relative to
    the folder of the document that declares it, judged on disk at the reading, never
    here: a worktree may leave and come back. A block badly written refuses
    `material-invalid`, naming the document: a value that is no block of lines, a line
    without a name or without a path, one of the two names no tree takes (`repo`, `work`), a
    name declared twice. A document without the key declares nothing."""
    raw = declarer.front.get(MATERIALS)
    if raw is None or raw == "":
        return ()
    if not isinstance(raw, str):
        raise Refusal("material-invalid",
                      f"{declarer.name}: `{MATERIALS}:` is a block of lines, one "
                      f"`<name>: <path>` each (`{MATERIALS}: |`)")
    found: list[tuple[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, colon, path = line.partition(":")
        name, path = name.strip(), path.strip()
        if not colon or not name or not path or " " in name:
            raise Refusal("material-invalid",
                          f"{declarer.name}: `{line}` — a line of `{MATERIALS}:` is "
                          "`<name>: <path>`, the path absolute or relative to this document's folder")
        if name in settings.RETIRED_MATERIALS:
            raise Refusal("material-invalid", f"{declarer.name}: `{line}` — {_retired(name)}")
        if any(name == one for one, _ in found):
            raise Refusal("material-invalid",
                          f"{declarer.name}: `{name}` is declared twice in `{MATERIALS}:`")
        found.append((name, path))
    return tuple(found)


class Reading(Composing):
    """The reading of documents -- a mixin of the facade: serve, resolve, prove."""

    def _resolve(self, name: str) -> Path:
        """A name resolves through the member's search paths (its instance's own directory
        first, then its packages), then at the ROOT OF ITS REPO -- `README.md`,
        `design/target.md`: the member's own documents by their bare path, the
        instance and the packages keeping the upper hand on a same name, the repo a
        last resort that never overlays anything -- and a name no document answers to
        may be a SKILL: its contract resolves where a document does not (the skill is
        a CALL), instance skills first, then a harness home or the house's procs
        (`instance.adopted`; an authored CALL is the instance's own consent)."""
        path = instance.resolve(self.member.meta, name)
        if path.is_file():
            return path
        at_repo = self.member.path / name
        if at_repo.is_file():
            return at_repo
        stem = Path(name).stem
        contract = (instance.skill_contract(self.member.meta, stem)
                    or instance.adopted(self.member.meta, stem))
        return contract if contract is not None else path

    def _material_name(self, mark: str, front: dict | None = None, stack=None) -> str:
        """-> the MATERIAL a row reads from, the nearest word winning: the row's own mark
        (`@<name>`), the `material:` of the document that carries the row, the nearest
        calling frame that declares one; "" when nobody names a tree -- the row then reads
        the run's own tree when the launcher gave it one, the repository otherwise
        (`_located`). A `material:` that says one of the two names no tree takes refuses
        `material-invalid`. The ONE site that answers the question, for every reader of
        a row."""
        if mark:
            return mark
        own = str((front or {}).get("material", "") or "").strip()
        if own in settings.RETIRED_MATERIALS:
            raise Refusal("material-invalid", f"`material: {own}` — {_retired(own)}")
        if own:
            return own
        if stack is not None:
            for frame in reversed(getattr(stack, "frames", stack)):
                declared = str(frame.document.front.get("material", "") or "").strip()
                if declared in settings.RETIRED_MATERIALS:
                    raise Refusal("material-invalid",
                                  f"{frame.document.name}: `material: {declared}` — {_retired(declared)}")
                if declared:
                    return declared
        return ""

    @staticmethod
    def _around(host: Document | None, stack=None) -> tuple[Document, ...]:
        """-> the documents a row of `host` looks a tree up in, nearest first: the document
        that carries the row, then the frames of the stack from the nearest to the farthest
        (`stack`: a Stack or its frames, the calling chain of the row)."""
        frames = getattr(stack, "frames", stack) or ()
        return ((host,) if host is not None else ()) + tuple(
            frame.document for frame in reversed(frames))

    def _material_path(self, name: str, around) -> tuple[str, Path] | None:
        """-> (the path as written, the folder it is read from) of the tree `name`: the
        FIRST document that declares the name, among the documents in play around the row,
        nearest first (`around`, a tuple of documents or a call that gives it -- read only
        when a row names a tree of a document's); None when none declares it."""
        for declarer in (around() if callable(around) else around or ()):
            for declared, path in materials(declarer):
                if declared == name:
                    return path, declarer.path.parent
        return None

    def _material_root(self, name: str, token: str, around=(), say=None) -> tuple[Path | None, str, str]:
        """-> (the tree the material `name` is, "", "") or (None, what lacks, the line the
        block carries in place of the reading) when the tree cannot answer: a name no
        document in play declares (`material-unknown`), a declared path absent from the disk
        (`material-missing`) -- each SAID by `say` (the engine's signal), never silent. A
        tree is declared by a DOCUMENT (`materials:`): the nearest one that declares the
        name answers (`_material_path`), and its relative path is read from that
        document's folder, never from the reader's workspace -- two readers of one
        document read one tree."""
        say = say or self._signal
        declared = self._material_path(name, around)
        if declared is None:
            say("engine", "material-unknown",
                evidence=f"{token} -- `@{name}`: no document in play declares it (`{MATERIALS}:`); not served")
            return None, "material-unknown", f"(not served: no document in play declares the tree `{name}`)"
        path, base = declared
        root = Path(os.path.expanduser(path))
        if not root.is_absolute():
            root = Path(os.path.normpath(base / root))
        if not root.is_dir():
            say("engine", "material-missing",
                evidence=f"{token} -- `@{name}` names {path}, which is no directory; not served")
            return None, "material-missing", f"(not served: the tree `{name}` names {path}, which is no directory)"
        return root, "", ""

    def _run_tree(self, name: str, say) -> Path | None:
        """-> the file `name` in the RUN's own tree -- the one the launcher gave it at its
        opening, kept at the slot --, None when the run has none or the tree does not hold
        the file: the tacit context of a row that names no tree. A tree that is no
        directory, or lacks the file, is said and the row reads the repository as a run
        without a tree does."""
        held = persistence.material_of(self._session) if self._session is not None else {}
        path = str(held.get("path") or "")
        if not path:
            return None
        root = Path(os.path.expanduser(path))
        if not root.is_absolute():
            root = self.member.path / root
        if not root.is_dir():
            say("engine", "material-missing",
                evidence=f"{name} -- the run's tree names {path}, which is no directory; served from the repository")
            return None
        at_run = root / name
        if at_run.is_file():
            self._served_tacit[str(at_run)] = str(held.get("name") or "run")
            return at_run
        say("engine", "serve-stale", evidence=f"{name} -- not in the run's tree; served from the repository")
        return None

    def _titled(self, token: str, path: Path) -> str:
        """-> the title a row-served reading renders under: the token as written, and the
        material it came from when the row or its document named one (` @<name>`)."""
        place = self._served_from.get(str(path), "")
        return f"{token} @{place}" if place else token

    def _lender(self, host: Path | None) -> Path | None:
        """-> the LENT machine's instance when the document at `host` is one of its own `procs/`
        and this instance borrows it: a row of that document that names no tree reads what the
        machine reads when it plays the document -- a relative path is read from the place of
        the document that declares it. None for any other document: the instance's own, a
        package's, a document of an instance that carries its machine."""
        if host is None:
            return None
        machine = instance.borrowed(self.member.meta)
        if machine is None:
            return None
        try:
            Path(host).resolve().relative_to((machine / instance.PROCS).resolve())
        except ValueError:
            return None
        return machine

    def _located(self, name: str, material: str = "", around=(),
                 quiet: bool = False, host: Path | None = None) -> tuple[Path | None, str, str]:
        """A SERVE token's document -> (its path, "", ""), or (None, what lacks, the line) when
        it is not served. A PATH -- the token carries a `/` -- whose row NAMES a tree
        (`@<name>`, a `material:`; `around`, the documents that may declare it) is that
        tree's and no other's: a name nobody declares, a tree that is no directory, a file
        the tree lacks are a reading DUE -- said, and a line of the block stands in its
        place; nothing is read from another tree. A path whose row names none, carried by a
        document of the machine the instance borrows (`host`, `_lender`), reads what that
        machine reads when it plays the document, its run's tree apart: its workspace, then its
        instance and the machine's copy; a file none of them holds is a reading due, said, never
        read at the borrower nor in the run's tree. Any other path whose row names none
        is the run's own tree's when the launcher gave it one and it holds the file, else the
        repository's, else the instance's: a member without the source reads the machine's
        copy, and `.sys/...` addresses the machine wherever the source stands beside it. A
        bare NAME resolves as every document name does (`_resolve`): the instance keeps
        the upper hand, the repository a last resort; a material never changes a name. A
        path standing at the repository AND the instance is said, once per run. A document
        GONE is (None, "", ""): the caller says it. A bare name carried by a document of the lent
        machine resolves as that machine resolves it: its instance and its copy, then its
        workspace, then its skills and its harness homes -- never the borrower's instance nor its
        repository. `quiet` says nothing of what lacks -- a second look at a row already served
        or said. A declaration of trees badly
        written is no document gone: `material-invalid` goes up."""
        say = (lambda *args, **kwargs: None) if quiet else self._signal
        if "/" in name:
            if material:
                root, lacks, line = self._material_root(material, name, around, say)
                if root is None:
                    return None, lacks, line
                at_material = root / name
                if at_material.is_file():
                    self._served_from[str(at_material)] = material
                    return at_material, "", ""
                say("engine", "serve-stale", evidence=f"{name} -- not in material `{material}`; not served")
                return None, "serve-stale", f"(not served: the tree `{material}` does not hold `{name}`)"
            lender = self._lender(host)
            if lender is not None:
                # what the lent machine reads when it plays the document, its run's tree apart: its
                # workspace, then its instance and the machine's copy -- never the borrower
                for candidate in (lender.parent / name, instance.resolve(lender, name)):
                    if candidate.is_file():
                        return candidate, "", ""
                say("engine", "serve-stale",
                    evidence=f"{name} -- not where {Path(host).name} lives ({lender.parent}); not served")
                return None, "serve-stale", (f"(not served: `{name}` is read where {Path(host).name} "
                                             "lives, which does not hold it)")
            at_run = self._run_tree(name, say)
            if at_run is not None:
                return at_run, "", ""
            at_repo = self.member.path / name
            if at_repo.is_file():
                if instance.resolve(self.member.meta, name).is_file():
                    self._shadowed(name)
                return at_repo, "", ""
        lender = self._lender(host) if "/" not in name else None
        if lender is not None:
            # a bare name of the lent machine's document resolves as the machine resolves it: its
            # instance and the machine's copy, then its workspace, then its skills and its harness
            # homes -- never the borrower's instance nor its repository
            for candidate in (instance.resolve(lender, name), lender.parent / name):
                if candidate.is_file():
                    return candidate, "", ""
            stem = Path(name).stem
            contract = instance.skill_contract(lender, stem) or instance.adopted(lender, stem)
            return (contract if contract is not None and contract.is_file() else None), "", ""
        try:
            path = self._resolve(name)
        except Refusal as refusal:
            if refusal.code == "material-invalid":
                raise
            return None, "", ""
        return (path if path.is_file() else None), "", ""

    def _missing(self, token: str, material: str, lacks: str, line: str, by: str) -> None:
        """A reading DUE and not served: ONE line of the block in its place, under the title
        the reading would have had, and the ledger says `missing` with what lacks."""
        title = f"{token} @{material}" if material else token
        self.note(title, "", "missing", "serve", by=by, package=material, lacks=lacks)
        self._payloads.append((title, line))

    def _shadowed(self, name: str) -> None:
        """The repository served a path the instance holds too: the engine's own signal
        says it, once per run and per path -- a row mounted ten times says it once."""
        if self._dry or self._count_traced("shadowed", "token", name):
            return
        self._trace("shadowed", token=name)
        self._signal("engine", "serve-shadowed",
                     evidence=f"{name} -- served from the repository; the instance "
                              "holds a file of the same path")

    def _clipped(self, path: Path, cut: tuple, home: str, name: str, token: str = "") -> bool:
        """-> whether the selection of a token STANDS. Nobody maintains a selector by hand:
        what drifted is SAID on the bus (`serve-stale`) and the reading goes on. A line range past the
        document's end clamps (sliced serves what stands); an end tag gone serves to the
        end; a start tag gone selects nothing -- the reading is `missing`, its line says
        so in the block, and the caller passes to the next token."""
        span = getattr(cut, "span", None)
        if span is None:
            total = len(path.read_text(encoding="utf-8").splitlines())
            if any(high > total for _, high in cut):
                self._signal("engine", "serve-stale",
                             evidence=f"{name} -- a range points past {total} lines, clamped")
            return True
        missing = spanned(path, span)[2]
        if missing == "end":
            self._signal("engine", "serve-stale",
                         evidence=f"{name} -- end tag gone, served to the end: `{span[1]}`")
        elif missing == "start":
            self._signal("engine", "serve-stale",
                         evidence=f"{name} -- start tag gone, nothing served: `{span[0]}`")
            self.note(token or name, "", "missing", "serve", by=home)
            self._payloads.append((token or name,
                                   f"(no line of this document starts with `{span[0]}`)"))
        return missing != "start"

    def _natured(self, row: tuple[str, ...]) -> tuple[str, tuple[str, ...]]:
        """-> (nature, tokens) of a serve row: a first token `<nature>:` DECLARES
        it (never inferred); an un-natured row wears the empty nature and always
        serves -- nothing disappears silently."""
        if row and row[0].endswith(":") and row[0][:-1] in settings.SERVE_NATURES:
            return row[0][:-1], row[1:]
        return "", row

    def _marked(self, row: tuple[str, ...]) -> tuple[str, str, tuple[str, ...]]:
        """-> (nature, material, tokens) of a serve row: after the nature, a token `@<name>`
        names the MATERIAL every document of the row reads from -- the row's FIRST token or
        its LAST (`@alt engine/x.py`, `engine/x.py @alt`), one mark a row; `@` is reserved,
        no document is called so. A bare `@`, or two marks on one row, refuse
        `material-invalid`. A row without the mark wears the empty material: the
        document's, the run's or the repository's."""
        nature, tokens = self._natured(row)
        marks = [one for one in tokens if one.startswith("@")]
        if not marks:
            return nature, "", tokens
        if len(marks) > 1 or (tokens[0] != marks[0] and tokens[-1] != marks[0]):
            raise Refusal("material-invalid",
                          f"`{' '.join(row)}` — a row names one material, by its first token or its last")
        name = marks[0][1:].strip()
        if not name:
            raise Refusal("material-invalid",
                          f"`{marks[0]}` — a row's material mark names a material: `@<name>`")
        if name in settings.RETIRED_MATERIALS:
            raise Refusal("material-invalid", f"`{' '.join(row)}` — {_retired(name)}")
        return nature, name, tuple(one for one in tokens if one != marks[0])

    def _section(self, frame: Frame, instruction: Instruction) -> tuple[tuple[str, ...], ...]:
        """-> the LINES this SERVE serves: its own argument as one line, or the whole
        `serve:` section of its rank -- a bare SERVE serves one section ENTIRE, however
        many lines and documents it holds; n sections take n SERVEs, in order."""
        if instruction.argument:
            return (split_row(instruction.argument),)
        sections = document.serve_sections(frame.document)
        rank = self._serve_rank(frame, instruction)
        if rank >= len(sections):
            raise Refusal("serve-exhausted",
                          f"{frame.document.name} declares {len(sections)} `serve:` "
                          f"section(s) — a {rank + 1}th bare SERVE asks for one more")
        return sections[rank]

    def _serve_plan(self, lines: tuple[tuple[str, ...], ...]) -> list[tuple]:
        """-> what a SERVE plays, entry by entry: one entry per document of the line --
        a row's nature is a declaration, never a hold: every row serves."""
        plan: list[tuple] = []
        for line in lines:
            nature, material, tokens = self._marked(line)
            for token in tokens:
                name, cut = ranged(token)
                # the row's NATURE and MATERIAL ride with its entry -- declarations the ledger
                # and the title say, never a hold; the token AS WRITTEN titles the reading
                plan.append((nature or "doc", name, cut, token, material))
        return plan

    def _reading(self, path: Path, cut: tuple) -> tuple[str, str]:
        """-> (the served text, its PROOF) of one document: a ranged token serves its
        lines raw -- its ranges, or what stands between its two tags --, a whole document
        its composed BODY; the proof hashes the selection or the composition: a run proves
        a reading once, document by document."""
        if getattr(cut, "span", None) is not None:
            return spanned(path, cut.span)[:2]
        if cut:
            return sliced(path, cut)
        text, digest = self._composed(path)
        return document.body_of(text).strip(), digest

    def _serve_document(self, path: Path, cut: tuple, *,
                        force: bool = False,
                        title: str | None = None,
                        origin: str = "serve", by: str = "",
                        nature: str = "", at: str = "") -> bool:
        """The ONE reader, for every site -- a section's line, a mount's row, a
        CALLed body: the text composed (a ranged token its lines, a whole document
        its body through the overlays), served WHOLE, and proven by the hash of what
        was read. A reading already proven in this run renders NOTHING, whatever
        vehicle brings it back; `force` reads it again regardless (the CALLed body
        under `proc_body_serve: always`); `title` is the subject the reading renders
        under -- a row-served reading says its TOKEN as the row wrote it, path and
        range, two files of one name never confused; absent, the document's own name
        (a CALLed body, a proc addressed by its unique name).

        The LEDGER takes a line either way: the reading entered the output, or it was
        SPARED because its content was already proven -- with the mass that sparing
        avoided. `origin`, `by`, `nature` and `at` come from the caller, which knows why
        it reads; nothing here is inferred from a name.

        documentary: nothing is cut here. A served document is matter of the OUTPUT
        like any other, and the output is what the engine measures and cuts under the
        host's cap -- one mechanism, one seam, one resume.
        -> whether the reading stands: proven before, or now."""
        admitted = self._admitted(path, cut, force=force, title=title, origin=origin,
                                  by=by, nature=nature, at=at)
        if admitted is not None:
            self._payloads.append(admitted)
        return True

    def _admitted(self, path: Path, cut: tuple, *,
                  force: bool = False,
                  title: str | None = None,
                  origin: str = "serve", by: str = "",
                  nature: str = "", at: str = "") -> tuple[str, str] | None:
        """The reader's DECISION, apart from where the text lands: -> (subject, text) when
        the reading enters the output -- noted, proven, staged -- and None when its content
        is already proven, the ledger saying `spared`. Every site stacks the admitted text
        as a payload."""
        text, tag = self._reading(path, cut)
        subject = title if title is not None else document.title(path)
        package = self.note_package(path)
        if tag in self._proven and not force:
            self.note(subject, "", "spared", origin, by=by, nature=nature, at=at,
                      package=package, spared=len(text))
            return None
        self.note(subject, text, "forced" if tag in self._proven else "served", origin,
                  by=by, nature=nature, at=at, package=package)
        if tag not in self._proven:
            self._fresh.add(tag)
        self._proven.add(tag)
        # the tag is also STAGED for this output: an output cut under the cap DEMOTES its
        # readings until their last chunk leaves -- a document is proven by its delivery
        self._staged.append(tag)
        return subject, text

    @staticmethod
    def _serve_rank(frame: Frame, instruction: Instruction) -> int:
        """-> how many bare SERVEs precede this one: its position in the `serve:` rows."""
        rank = 0
        for one in frame.procedure.instructions:
            if one is instruction:
                return rank
            if one.keyword == "SERVE" and not one.argument:
                rank += 1
        return rank
