# The front matter and your own procedures

This file lists every key a document's front matter may declare, then shows how you write your own procedures and extend a package's procedure without editing it.

- [The front matter, key by key](#the-front-matter-key-by-key)
- [Writing your own procedures](#writing-your-own-procedures)

## The front matter, key by key

| Key | Declares |
|---|---|
| `name` | the document's identity (a skill directory's name IS the identity — `SKILL.md` is the mold) |
| `kind` | `proc` · `doc` · `boot` — a `doc` never executes |
| `description` | the catalog line — required for anything offered |
| `proc:` | the flow; its presence makes the document conducted |
| `output:` / `input:` | the pipeline's two ends — names of the formats enumeration |
| `serve:` | reading sections (paragraphs), one per bare `SERVE` — see [`serve:`](#serve) below |
| `tools:` | this frame's offers — `+name` adopts a harness skill, or a proc of the house the instance is installed under |
| `constraints:` | the laws, `CODE  text`, ONE line per law |
| `formats:` | form declarations `name  inline\|stdin\|words  description` — see [`formats:`](#formats) below |
| `attach:` | the HOOK socket this document answers |
| `mount:` | the HOOK socket this document ENTERS at — its laws, offers, body and readings ride the view there; it asks nothing |
| `mounts:` | what this document MOUNTS at its own sockets — see [`mounts:`](#mounts) below |
| `order:` | where this contributor stands among the socket's others — see [`order:`](#order) below |
| `exec:` | `<verb> [args]` — a skill the engine plays once at every ENTRY of this document — see [`exec:`](#exec) below |
| `cycle:` / `fusion:` | `true` the session floor, `<token>` the iterated door · the frame's own pace |
| `field:` | the DESCRIBED door — see [`field:`](#field) below |
| `next:` | the SUCCESSORS the document may leave to — see [`next:`](#next) below |
| `choose:` / `decide:` | the decider of a `next:` of several names — see [`choose:` / `decide:`](#choose--decide) below |
| `override:` | `true` on `SYSTEM_PROMPT.md` — composes the replace artifact |

#### `serve:`

`serve:` declares reading sections (paragraphs), one per bare `SERVE`. Each line is a grouping: its nature first, then its tokens separated by blanks. A blank inside a token's brackets does not separate.

A token is one of:

- `DOC`;
- `DOC[start..end]`;
- as a last resort, `DOC[x-y,…]`.

See [`SERVE [doc]`](language.md#serve-doc).

#### `formats:`

`formats:` holds form declarations, `name  inline|stdin|words  description`. It extends the enumeration.

A form at the mode `words` is written in the agent's words and stands alone (see [The form of a said production](block.md#the-form-of-a-said-production)). The engine's imposed forms keep their mode.

#### `mounts:`

`mounts:` declares what this document MOUNTS at its own sockets. It is a table `<socket>: <names>` (`turn.begin: HOUSE.md`, a name or a list), the socket written as its `proc:` writes it. It may be written on the document or on an overlay of it.

The names mount after the socket's `mount:` contributors, each under its own `when:`. They resolve as a CALL does, the house of an agent included. A socket the proc never hooks refuses `mounts-hook-unknown`.

#### `order:`

`order:` holds one line per pair, `<hook> before|after <package>`: where this contributor stands among the socket's others. A peer the composition lacks is inert.

The word `exec` in the socket's place orders several `exec:` on one document.

#### `exec:`

`exec:` is `<verb> [args]`: a skill the engine plays once at every ENTRY of this document (a CALL, a mount, a lap of an iterated door), before the body and before anything it serves.

The skill is the `pp-<package>` of the file's own package. A document of the instance names one of its own skills first: `exec: <skill> <verb>`. An argument `@Doc.field` takes the value a guard would read, never empty.

- A non-zero exit refuses `exec-refused`, and nothing enters.
- What the skill prints goes to the bus alone (`::push`, `::clear`).
- A `::mount` refuses `exec-mount`.

The base and each overlay may declare their own `exec:`, each playing its own package's skill.

#### `field:`

`field:` holds the prose of what the door turns on. Its presence declares the DESCRIBED door.

The engine asks the agent for the field once (`INFER field`, a JSON array judged on its form), then serves one element per lap under `field`. It is never written beside `cycle:`.

#### `next:`

`next:` lists the SUCCESSORS the document may leave to, as names written the way `CALL` writes them.

- One name follows alone.
- Several names are decided at the exit, and the one elected enters the caller's frame as a sibling CALL.

The graph of the composition is acyclic: a cycle refuses `next-cycle` at the build.

#### `choose:` / `decide:`

These declare the decider of a `next:` of several names. Use one of the two, never both.

- `choose: |` — the prose the agent reads at a `PICK next`.
- `decide: <verb> [args]` — the owner's skill that prints the name.

#### What serves, and `SETTINGS.md`

Any text file serves whole; there is no terminal marker. The hash pp computes on what it serves is the proof of what was served.

`SETTINGS.md` is documented in place (the template). The catalogue of the patterns sends each of its keys to the pattern that teaches it: the engine's defaults and the seeded values are the same.

## Writing your own procedures

Your own procedures live in `.pp/procs/`: a markdown document there, shaped like the `REVIEW` example of the [README](../../README.md).

Two seams let you extend a package's procedure **without ever editing it**:

- **flow** — a package proc declares `HOOK <name>`; any document of yours with `attach: <name>` is called there.
- **sections** — a document of the **same name** in `.pp/procs/` is an **overlay** (below).

#### Overlays

An overlay's `constraints:` and `tools:` are deltas over the bundle's:

| Delta | Effect |
|---|---|
| `+CODE  text` or `CODE  text` | adds a constraint |
| `-CODE` | removes a constraint |
| `+name` | adds a tool |
| `-name` | removes a tool |

The bundle's procedure keeps executing. An overlay that declares a `proc:` is refused, and so is a delta that changes nothing.

An overlay's `output:` and `input:` replace the bundle's: the nearest overlay that declares one wins.

An `overlays/` directory at the instance's root is never read: `-build` warns `overlays-ignored`.

### Packages declare their settings too

The conductor's protocol keys are seeded bare at the template. The base package declares its own in a `settings/SETTINGS.md` fragment, bare too:

- the kit's `capture_prompt`;
- `capabilities` — `false` boots straight to the turn, without the `CAPABILITIES` table.

The two readings the BOOT serves, `tools.md` and `output.md`, come at every value of `capabilities`. The member's `CALL CAPABILITIES.md ^ @SETTINGS.capabilities` reads it, and no effort presets it: the written value rules.

A package beyond the base carries the same fragment, holding:

- its own keys, each wearing the package's prefix (`plan_`);
- their defaults and `types:`;
- its `effort:`/`role:` presets;
- its SECTION of the instance's SETTINGS body.

Install, upgrade and doctor compose the file from the system's template and the fragments in the requires topology, the operator's values kept.

### Packages overlay too

A package's `overlays/` directory is its own overlay space, interposed between the user's and the packages' bases. A same-name file there applies AFTER the deeper bundle and BEFORE the user's (the user always wins). It can never become the base itself.

Between packages, the order is the REQUIRES topology, never the pins. A dependency's overlay applies first, its clients' after: a client amends what it requires and wins. Ties keep the pin order.

#### The body appends too

An overlay's BODY joins the served text of its base: the packages' prose first, the user's LAST, the reading's hash taken over the composition.

An overlay with no body appends nothing, and without overlays the served bytes are untouched.

#### The readings add too

An overlay's `serve:` rows join the service of its base. They are served whole as the base enters, in application order, each titled by its token.

A leading `+` on a row says the addition and is optional. A `-` refuses (`overlay-serve-removal`): an overlay never removes a reading.

The base's own sections keep their `SERVE` pace, and a base whose overlays carry no row serves nothing more.

### Any bundled constraint bends — add yours, remove any

Every rule a **bundled procedure** holds in force, the kit's included, is yours to lift or extend by its code. Your harness's own system, safety and provider rules are not pp's to bend.

Bothered by one? Write a file `.pp/procs/TURN.md` holding nothing but:

```
---
name: TURN
constraints: |
  -T4
  T6  answers stay under ten lines unless asked otherwise.
---
```

This lifts `T4` ("say what you are about to do, before you do it") from every block the kit's `TURN` holds it on, and puts your `T6` in force in its place. The bundle stays untouched, the delta is yours, and the build refuses a delta that changes nothing.

## See also

- [language.md](language.md) — the keywords a `proc:` flow is written in (`HOOK`, `CALL`, `SERVE`, …).
- [skills.md](skills.md) — how offered skills (`tools:`) play, and adoption.
- [instance.md](instance.md) — the instance on disk, and what the build refuses.
- [console.md](console.md) — the operator's console, and switching a package off.
