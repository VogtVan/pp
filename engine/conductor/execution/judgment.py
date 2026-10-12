"""execution.judgment -- the judgment: the checkpoint's one regime, the checks of an answer. A mixin of the facade: no state of its own."""
from __future__ import annotations

import json
from ..core import deviation, document as documents, language
from ..state import instance, settings
from ..core.errors import Refusal
from ..core.model import Frame, Instruction, Stack
from .entry import ENTRIES, site_of


def _fix(one: dict) -> str:
    """-> the fix a proof object names, "" when it names none."""
    return str(one.get("fix", "")).strip()


def _gap(one: dict) -> str:
    """-> what a `fail` object declares missing (`blocked`, a non-empty text), "" otherwise."""
    blocked = one.get("blocked")
    return blocked.strip() if isinstance(blocked, str) else ""

class Judging:
    """The judgment: the checkpoint's one regime, the checks of an answer -- a mixin of the facade."""

    def _armed(self, frame: Frame) -> bool:
        """-> whether `frame` owes its checkpoint ITSELF: the entry table says `proof` for
        the floor, a written CALL, a door, a successor, a lap -- and `defer` for a document
        a SOCKET called (a contributor at a hook, a cadence): its own laws do not leave with
        it, they stay DUE at the run (`_owe`) and the turn's checkpoint names them. No key
        arms a document any more.

        documentary: the proof has ONE regime (operator word 2026-09-05) -- owed wherever
        a law of production is in force, in front of each FINAL and at a frame's exit;
        the engine decides, the agent never judges whether to prove. A document that
        still carries a `prove:` key refuses at its opening (`prove-gone`)."""
        if "prove" in frame.document.front:
            raise Refusal("prove-gone",
                          f"{frame.document.name}: `prove:` is gone -- the proof has no "
                          "switch: it is owed wherever a law of production is in force")
        return "proof" in ENTRIES[site_of(frame)]

    def _production_in_force(self, frame: Frame) -> bool:
        """-> whether ONE law of production binds `frame` (its chain and the mounts):
        the proof asks the production laws alone, so none in force means no
        checkpoint at all -- a behavior law binds the block, never the proof."""
        return any(one.section == "production" for one in self._in_force(frame))

    def _exit_due(self, frame: Frame, at_frontier: bool = False) -> bool:
        """-> whether this frame owes a checkpoint NOW: armed (not socket-opened),
        with productions standing unproven since the last played checkpoint and a
        law of production in force -- the one predicate frontier and exit share.
        At a frontier every yield of the frame counts (the FINAL delivers the turn
        under every law on screen); at a frame's EXIT they count only when the
        frame carries a law of production of its OWN -- the law that leaves the
        screen with it: a door's pop proves its laws, a callee under inherited laws
        alone lets its productions go to the frontier where those laws still stand."""
        if not self._armed(frame) or not self._production_in_force(frame):
            return False
        return self._unproven(frame, at_frontier)

    def _own_production(self, frame: Frame) -> bool:
        """-> whether `frame`'s OWN document declares a law of production -- a law
        that LEAVES the screen with the frame, so the exit must prove under it."""
        return any(one.section == "production"
                   for one in documents.constraints(frame.document))

    def _unproven(self, frame: Frame, at_frontier: bool) -> bool:
        """-> whether YIELDING productions stand unproven since the last played
        checkpoint: a played checkpoint clears the slate, any later production
        reopens the debt -- multi-frontier documents prove each segment before ITS
        delivery. At a frame's exit (no frontier) the debt exists only under a law
        of production of the frame's OWN -- the boot's table, a callee's feed, are
        proven by the turn that delivers them, where the inherited laws still stand."""
        if not at_frontier and not self._own_production(frame):
            return False
        fresh = at_frontier and bool(self._owed_laws())   # a socket's debt waits here
        for one in frame.procedure.instructions:
            if one.injected and one.keyword == "PROVE" and one.done:
                fresh = False
                continue
            if (one.done and not one.injected
                    and one.keyword in language.YIELDING and one.given != "off"):
                fresh = True
        return fresh

    def _exit_coming(self, frame: Frame, instruction: Instruction) -> str:
        """-> `obliged` when a checkpoint is CERTAIN to follow `instruction` -- its
        frame's last step, or the step a frontier sits right behind -- '' when
        none will come: the `_exit_due` conditions, one step ahead."""
        if not self._armed(frame) or not self._production_in_force(frame):
            return ""
        at = frame.procedure.instructions.index(instruction)
        following = frame.procedure.instructions[at + 1:at + 2]
        frontier = bool(following) and following[0].keyword == "FINAL"
        if not frontier and not self._own_production(frame):
            return ""
        if instruction.keyword in language.YIELDING or self._unproven(frame, frontier):
            return "obliged"
        return ""

    def _fusion_cap(self, frame: Frame) -> int:
        """-> the yields-per-output cap in force for `frame`'s steps: the document's
        own `fusion:` when declared, the instance's otherwise. 0 = unlimited."""
        declared = frame.document.front.get("fusion")
        if declared is not None:
            return settings.fusion_of(declared)
        return self._settings.fusion

    def _check(self, stack: Stack, frame: Frame, instruction: Instruction,
               answer: str) -> str:
        """-> what the answer missed, or "" when it arrives. One checker per keyword, by name."""
        checker = getattr(self, f"_check_{instruction.keyword.lower()}", None)
        return checker(stack, frame, instruction, answer) if checker else ""

    def _check_pick(self, stack: Stack, frame: Frame, instruction: Instruction,
                    answer: str) -> str:
        return "" if answer in instruction.options else deviation.wrong_answer(instruction, answer)

    def _check_next(self, stack: Stack, frame: Frame, instruction: Instruction,
                    answer: str) -> str:
        """The successor the agent elects is a PICK: judged by membership among the
        names of `next:`, a name outside the graph a miss that repairs."""
        return self._check_pick(stack, frame, instruction, answer)

    def _check_prove(self, stack: Stack, frame: Frame, instruction: Instruction,
                     answer: str) -> str:
        """The proof is machine-checked: valid JSON, the declared shape, one object for
        every code the line asks -- the laws of production in force: a code left unnamed
        is a named miss, a code no law in force carries is one too -- and any `fail`
        verdict reopens the whole document.
        `n/a` says a law without bearing on this production: neither earned nor
        failed, it repairs nothing -- `ok` is reserved for the VERIFIED. A `fail` that
        carries `blocked` (what is missing, a non-empty text) DECLARES a gap: accepted,
        the checkpoint closes; a bare `fail` outweighs it, a `fix` repairs in place."""
        try:
            proof = json.loads(answer)
        except ValueError as wrong:
            return f"the PROOF is not one valid JSON value -- {wrong}."
        if (not isinstance(proof, list)
                or not all(isinstance(one, dict) and {"code", "evidence", "verdict"} <= set(one)
                           for one in proof)):
            return ('the PROOF is not a JSON array of {"code", "evidence", "verdict"} '
                    "objects.")
        odd = [one for one in proof if one["verdict"] not in ("ok", "fail", "n/a")]
        if odd:
            return f"a verdict is `ok`, `fail` or `n/a` -- not {odd[0]['verdict']!r}."
        if instruction.refit:
            # the MINI-PROOF: the repaired codes alone come back, verified -- a code
            # failing twice loses the cheap branch, the document replays
            expected = set(instruction.refit)
            if {one["code"] for one in proof} != expected:
                # the ask stands: the mini-proof re-presents, the document never
                # reopens on a coverage slip -- the bound still counts the try
                self._inplace = instruction.refit
                return ("the mini-proof covers exactly the repaired code(s): "
                        f"{', '.join(instruction.refit)}.")
            relapsed = [one for one in proof if one["verdict"] == "fail" and not _gap(one)]
            instruction.refit = ()
            if relapsed:
                return ("the repaired code failed AGAIN -- the cheap branch closes: "
                        + " · ".join(f"{one['code']}: {one['evidence']}" for one in relapsed))
            self._declared([one for one in proof if one["verdict"] == "fail"])
            return ""
        covered = [one["code"] for one in proof]
        # a behavior law never enters the proof: it binds the block, the judge asks
        # the production laws alone (an object offered for a behavior law is not a miss);
        # a code no law in force carries is a miss -- the proof judges what stands --
        # and a proof naming no law of production proves nothing
        in_force = {one.code: one.section for one in self._in_force(frame)}
        foreign = [code for code in covered if code not in in_force]
        if foreign:
            return f"the PROOF names law(s) not in force: {', '.join(foreign)}."
        if not any(in_force[code] == "production" for code in covered):
            return "the PROOF names no law of production -- the codes at risk, at least one."
        unnamed = [code for code, section in in_force.items()
                   if section == "production" and code not in covered]
        if unnamed:
            # every code the line asks takes its verdict: a silence is no n/a
            return (f"the PROOF leaves {len(unnamed)} code(s) unnamed: {', '.join(unnamed)} -- "
                    "each one takes ok, fail or n/a.")
        failed = [one for one in proof if one["verdict"] == "fail"]
        bare = [one for one in failed if not _fix(one) and not _gap(one)]
        if bare:
            # a fail that neither fixes nor says what is missing: the document replays
            return ("your own proof failed -- "
                    + " · ".join(f"{one['code']}: {one['evidence']}" for one in bare))
        fixed = [one for one in failed if _fix(one)]
        self._declared([one for one in failed if not _fix(one)])
        if fixed:
            # every remaining fail NAMES its fix: the repair plays IN PLACE -- the agent
            # corrects the production and re-proves the fixed codes alone
            self._inplace = tuple(one["code"] for one in fixed)
            return ("your proof failed and NAMES its fixes -- repair the "
                    "production IN PLACE, then pipe a mini-proof over the failed "
                    "code(s) alone: "
                    + " · ".join(f"{one['code']}: {one['fix']}" for one in fixed))
        return ""

    def _declared(self, gapped: list[dict]) -> None:
        """The gaps a proof DECLARED -- `fail` objects carrying `blocked`: accepted, not
        repaired; written on the trace, and held for the closing of the block this call
        renders, which says them."""
        if not gapped:
            return
        found = [{"code": one["code"], "text": _gap(one)} for one in gapped]
        self._trace("blocked", gaps=found)
        self._gaps.extend((one["code"], one["text"]) for one in found)

    def _check_field(self, stack: Stack, frame: Frame, instruction: Instruction,
                     answer: str) -> str:
        """The FIELD is machine-checked on its FORM alone -- one valid JSON value, an
        array, scalars (strings or numbers) none empty, each once, under the bound -- and
        never on what an element IS: the engine knows no nature, an array of integers
        passes exactly as an array of paths that do not exist."""
        try:
            field = json.loads(answer)
        except ValueError as wrong:
            return f"the FIELD is not one valid JSON value -- {wrong}."
        return language.scalars_form(field, "FIELD", empty_ok=True)

    def _check_infer(self, stack: Stack, frame: Frame, instruction: Instruction,
                     answer: str) -> str:
        """A CAPTURED production validates against its format -- the mechanical seed
        of the convergence: `json` must parse; a consumed empty is no production. A
        production the next step ELECTS from is judged on the OPTIONS' form -- the one
        a FIELD has -- before the renderer ever meets it: a list of objects is the
        agent's miss, named, and the document reopens."""
        consumed, _ = self._consumer(stack, frame, instruction)
        if consumed and not answer.strip():
            return "an empty production -- the next step consumes it; hand it over."
        if self._output_of(frame) == "json" and answer.strip():
            try:
                value = json.loads(answer)
            except ValueError as wrong:
                return f"not one valid JSON value -- {wrong}."
            if self._elects(stack, frame, instruction):
                return language.scalars_form(value, "OPTIONS", empty_ok=False)
        return ""

    def _owes_proof(self, frame: Frame, wait_at: Instruction) -> bool:
        """-> whether the exchange this FINAL opens carries a PROVE -- said on the
        FINAL's closing, so the agent weighs the proof from the operator's message
        on, not when the proof block arrives. An idle lap (nothing produced) earns
        no checkpoint; with no law of production in force the lap owes nothing, and
        the closing says so."""
        return self._armed(frame) and self._production_in_force(frame)
