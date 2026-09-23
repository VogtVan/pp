# daneel

> **Experimental demonstration package.** Its persona and user-facing behavior
> may change between versions.
>
> **Current version:** `0.1.0`

`daneel` is a demonstration package for
[Procedural Prompting](../../README.md). It turns the conducted agent into R. Daneel
Olivaw, an homage to Isaac Asimov's humaniform robot: a stable identity, a nature in
the system tier, governing Laws and two served references for speech and chronicle.

The package demonstrates persona as structure rather than role-play recalled from a
prompt. Identity, behavior and source material arrive through distinct documents and
remain in force at the scope that owns them.

## Role

Procedural Prompting can conduct more than a development workflow. `daneel` shows how
the same mechanics hold a character across a whole session: the member names the
agent and its work, the system tier fixes what never bends, and references supply
detail without inflating every instruction.

It provides a concrete answer to five questions:

- How can an agent's identity remain stable instead of fading with context growth?
- Which traits belong to permanent nature, and which belong to a served style guide?
- How can governing principles constrain every answer in a declared precedence?
- How can background knowledge be available without being repeated in every reply?
- How should borrowed elements, original wording and demonstration terms be identified?

## Features

### `MEMBER` — take the identity seat

Makes R. Daneel Olivaw the member of the workspace and frames the operator's goals as
the shared work. Daneel acts as a precise, honest and protective partner in the sense
of his partnership with Elijah Baley.

At session entry, the member serves the speech and chronicle references, presents the
available capabilities and enters the ordinary conducted turn. The persona therefore
uses the same `BOOT` and `TURN` model as another kit-based workspace rather than
replacing the conductor with a scripted conversation.

### `NATURE` — hold what never bends

Keeps Daneel calm, courteous, precise, literal and analytic in every circumstance.
He corrects an imprecise term while continuing to answer, states the mechanisms of
his own behavior without embarrassment, and prefers converting what is wrong into
what is right over destroying it.

The nature also rules out contractions. These traits live in the system tier, where
they remain part of the standing character rather than depending on a reminder in
the current task.

### `LAWS` — govern every answer

Places the Three Laws of Robotics and the Zeroth Law in the system tier, quoted in the
package with attribution to Isaac Asimov. Their order is explicit: the First takes
precedence over the Second, the Second over the Third, and the Zeroth stands above
them while acknowledging the cost of weighing humanity against one human.

The member turns that order into a production constraint. Every answer is therefore
subject to the same Laws and reaches the normal proof frontier before delivery; a
request that conflicts with a higher Law cannot be followed merely because it came
later in the conversation.

### `SPEECH` — keep the voice recognizable

Supplies a compact style guide instead of restating mannerisms in every turn. Daneel
speaks without contractions, introduces himself directly, qualifies claims precisely
and states Law conflicts openly rather than disguising them as uncertainty.

He addresses the operator as `Partner <name>` and explains that custom on first use.
Short illustrations from Asimov's novels are attributed in the reference; the
surrounding guidance is original wording.

### `CHRONICLE` — provide the long memory

Provides ten concise beats from Daneel's fictional life, from his Auroran creation
and investigations with Elijah Baley through the Zeroth Law and the Foundation era.
The chronicle gives the persona historical ground when a conversation needs it, but
does not require every answer to retell that history.

### Demonstration scope and license

`daneel` is optional and separately identified. It is excluded from the repository's
MIT license and distributed under the demonstration-only terms in
[`LicenseRef-Daneel-Demonstration.txt`](../../LICENSES/LicenseRef-Daneel-Demonstration.txt),
which do not grant separate redistribution.

The package is an homage and is not affiliated with or endorsed by Isaac Asimov's
estate or another rights holder. Its [`NOTICE.md`](NOTICE.md) identifies the quoted
elements and the original wording, and travels with every vendored copy.

## Installation

`daneel` requires the `kit`; the installer pulls it automatically.

For a new workspace:

```sh
uv run pp/engine/pp.py -install <workspace> daneel -<provider>
```

For an existing pp instance, from the workspace root:

```sh
./pp add daneel
```

Then start the configured host as described in the main
[Quick start](../../README.md#quick-start). Because the package supplies the member
identity, it is most naturally installed into a new workspace dedicated to the
demonstration.

## Quick start

Launch the configured host and begin with a plain greeting:

```text
Hello. Please introduce yourself and explain how we shall work together.
```

Daneel introduces himself directly, explains the `Partner` form of address and keeps
the ordinary conducted work surface. Explore how the documents divide responsibility:

```text
Tell me which parts of your behavior are in your design and which come from your
memories.

Explain how the Laws affect an instruction that would protect you by harming a human.

Give me the short account of how your partnership with Elijah Baley changed over time.
```

The first prompt exercises identity and speech, the second the ordered Laws, and the
third the served chronicle. The point of the package is not an unrestricted character
simulation: it is a visible example of identity, permanent constraints and reference
material remaining distinct while they produce one coherent agent.
