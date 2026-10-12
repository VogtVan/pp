"""reading.serve -- the ONE reader of the three sites (a section's line, a mount's
row, a CALLed body): the resolution of a name through the member's search paths,
the serve plan of a section, the line-bound cut at the room, the proof by hash.
The mixin of the facade that holds it: the room, the proven tags and the payloads
are the facade's state, read here."""
from __future__ import annotations

import os
from pathlib import Path

from ..core import document, language
from ..core.tokens import split_row
from ..core.errors import Refusal
from ..state import instance, persistence, settings
from .tokens import ranged, sliced, spanned
from .composition import Composing


class Reading(Composing):
    """The reading of documents -- a mixin of the facade: serve, resolve, prove."""

    def _resolve(self, name: str) -> Path:
        """A name resolves through the member's search paths (its instance's own space
        first, then its packages), then at the ROOT OF ITS REPO -- `README.md`,
        `design/target.md`: the member's own documents by their bare path, the
        instance and the packages keeping the upper hand on a same name, the repo a
        last resort that never overlays anything -- and a name no document answers to
        may be a SKILL: its contract resolves where a document does not (the skill is
        a CALL), instance skills first, then a harness home (an authored CALL is the
        instance's own consent)."""
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
        calling frame that declares one, the launcher's `work` when the run was given one,
        the repository otherwise (`repo`). The ONE site that answers the question, for
        every reader of a row."""
        if mark:
            return mark
        own = str((front or {}).get("material", "") or "").strip()
        if own:
            return own
        if stack is not None:
            for frame in reversed(stack.frames):
                declared = str(frame.document.front.get("material", "") or "").strip()
                if declared:
                    return declared
        if self._session is not None and persistence.material_of(self._session):
            return settings.MATERIAL_WORK
        return settings.MATERIAL_REPO

    def _material_root(self, name: str, token: str) -> Path | None:
        """-> the tree the material `name` is, or None when the reading goes as today --
        the repository asked by name, or a material that cannot answer: a name the
        catalogue does not know (`material-unknown`), a declared path absent from the disk
        (`material-missing`) -- each SAID, never silent; the reading then serves as it
        always did."""
        if not name or name == settings.MATERIAL_REPO:
            return None
        if name == settings.MATERIAL_WORK:
            held = persistence.material_of(self._session) if self._session is not None else {}
            path = str(held.get("path") or "")
            if not path:
                self._signal("engine", "material-unknown",
                             evidence=f"{token} -- `@work`: this run was given no material; served as today")
                return None
        else:
            path = dict(self._settings.materials).get(name, "")
            if not path:
                self._signal("engine", "material-unknown",
                             evidence=f"{token} -- `@{name}`: no `material.{name}` at SETTINGS; served as today")
                return None
        root = Path(os.path.expanduser(path))
        if not root.is_absolute():
            root = self.member.path / root
        if not root.is_dir():
            self._signal("engine", "material-missing",
                         evidence=f"{token} -- `@{name}` names {path}, which is no directory; served as today")
            return None
        return root

    def _titled(self, token: str, path: Path) -> str:
        """-> the title a row-served reading renders under: the token as written, and the
        material it came from when that is not the repository (` @<name>`)."""
        place = self._served_from.get(str(path), "")
        return f"{token} @{place}" if place else token

    def _resolve_served(self, name: str, material: str = "") -> Path:
        """A SERVE token's document. A PATH -- the token carries a `/` -- is its MATERIAL's
        when a material is named and holds it (`@<name>`, the document's `material:`, the
        run's `work`), else the repository's when the repository holds it, the instance's
        otherwise: a member without the source reads the machine's copy, and `.sys/...`
        addresses the machine wherever the source stands beside it. A bare NAME resolves as
        every document name does (`_resolve`): the instance keeps the upper hand, the
        repository a last resort; a material never changes a name. A path standing at the
        repository AND the instance is said, once per run; a path a material lacks is said
        too, and serves as today."""
        if "/" in name:
            root = self._material_root(material, name) if material else None
            if root is not None:
                at_material = root / name
                if at_material.is_file():
                    self._served_from[str(at_material)] = material
                    return at_material
                self._signal("engine", "serve-stale",
                             evidence=f"{name} -- not in material `{material}`; served as today")
            at_repo = self.member.path / name
            if at_repo.is_file():
                if instance.resolve(self.member.meta, name).is_file():
                    self._shadowed(name)
                return at_repo
        return self._resolve(name)

    def _shadowed(self, name: str) -> None:
        """The repository served a path the instance holds too: the engine's own signal
        says it, once per run and per path -- a row mounted ten times says it once."""
        if self._dry or self._count_traced("shadowed", "token", name):
            return
        self._trace("shadowed", token=name)
        self._signal("engine", "serve-shadowed",
                     evidence=f"{name} -- served from the repository; the instance "
                              "holds a file of the same path")

    def _stale(self, name: str, material: str = "") -> Path | None:
        """-> the resolved path of a serve token's document, or None when it is
        GONE: the serve is a convenience the improve signal keeps honest -- a
        vanished document never stops a reading, it is said and skipped."""
        try:
            path = self._resolve_served(name, material)
        except Refusal:
            return None
        return path if path.is_file() else None

    def _clipped(self, path: Path, cut: tuple, home: str, name: str, token: str = "") -> bool:
        """-> whether the selection of a token STANDS. Nobody maintains a selector by hand:
        what drifted is SAID to the improve and the reading goes on. A line range past the
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
        names the MATERIAL every document of the row reads from -- `@` is reserved, no
        document is called so; a bare `@` refuses `material-invalid`. A row without the
        mark wears the empty material: the document's, the run's or the repository's."""
        nature, tokens = self._natured(row)
        if tokens and tokens[0].startswith("@"):
            name = tokens[0][1:].strip()
            if not name:
                raise Refusal("material-invalid",
                              f"`{tokens[0]}` -- a row's material mark names a material: `@<name>`")
            return nature, name, tokens[1:]
        return nature, "", tokens

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
                          f"section(s) -- a {rank + 1}th bare SERVE asks for one more")
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
        is already proven, the ledger saying `spared`. A nested mount writes the admitted
        body under its own heading; every other site stacks it as a payload."""
        text, tag = self._reading(path, cut)
        subject = title if title is not None else document.title(path)
        package = self.note_package(path)
        if tag in self._proven and not force:
            self.note(subject, "", "spared", origin, by=by, nature=nature, at=at,
                      package=package, spared=len(text))
            return None
        self.note(subject, text, "forced" if tag in self._proven else "served", origin,
                  by=by, nature=nature, at=at, package=package)
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
