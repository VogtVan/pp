# payload — a skill's output served as a section

## What you write

- On the consumer, the document that wants the output: `payloads: <token> …`, one or
  more tokens.
- On the provider, a document of a package: `provides: <token>` and `with: <skill>
  [args]`, the skill whose output renders the token; the skill knows the run that started it
  (see `packaging/run-context`). The token is the package's name or
  starts with it (`witness`, `witness-inbox` for the package `witness`), and the skill is
  the package's.

## What you get

- When the consumer enters a block — called, mounted, or contributing at a socket —
  each of its tokens renders as a section `INFORMATION — <token>`: the output of the
  skill of every provider of that token, in order.
- A skill that refuses is said in its section, with its exit code; the step goes on.
- A token enters an output once: a second consumer of the same token in the same output
  runs no provider and renders nothing more. In a later output the providers run again,
  and the content decides: the same rendering is spared, a changed one enters whole.
- A refusal is said once per output too.
- After a compaction, each token standing in the view is resolved once more, once for
  all the consumers that name it.
- A mounted consumer's body enters once; under the setting `proc_body_serve: always` it
  is served at every mount. A nested mount whose body is spared keeps its segment: its
  heading and its offers render, the body does not.
- A contributor's body rides WITH the section its tokens render, just before it: when
  no provider printed anything, neither the body nor the section renders.

## When to use it

- Bring a fresh state into a block — an inbox, a status, a count — computed when the
  block is rendered, not written by hand in a document.
- Let a package provide what an instance's documents ask for, without the instance
  knowing the skill.
- Write a contributor whose body explains a section it renders, and that stays silent
  when there is nothing to explain.
- To serve a document rather than a skill's output, see `context/serve`; to bring a
  contributor at a socket, see `composition/mount`.

## What refuses

- Nothing stops the step: a refusing skill is said in its section (`<skill> refused
  (<code>)`), and the block plays on.

## The demonstration

- `procs/ASK1.md`, `procs/ASK2.md` — two consumers of `alpha-news`, each one `INFER`.
- `procs/MOUNTED.md` — a doc that names `alpha-news`, with its law `KMO1` and a body,
  mounted.
- `procs/NESTED.md` — a doc that offers `pp-alpha`, mounted in a segment of its own.
- `procs/BOARD.md` — a proc that opens the socket `board.open`, then one `INFER`.
- `procs/POSTER.md` — a contributor mounted at `board.open` that names `witness` and
  `witness-broken`.
- `procs/NOTICE.md` — a contributor mounted at `board.open` that names `witness-inbox`,
  its body explaining the section.

The providers are not demonstrated: they live in packages, and their skills are scripts.

## The test

`tests/patterns/context/payload.py` writes two packages of providers and their skills
(`alpha` with two providers of `alpha-news` and a refusing one, `witness` with a
speaking, a refusing and an inbox provider), then plays the demonstration: one output
runs each provider once, two outputs spare or renew by content, a refusal is said once,
a compaction resolves a token once; a mounted body enters once, `always` forces it, a
spared nested body keeps its segment; at BOARD, POSTER's sections and refusal render
and BOARD plays on, NOTICE's body renders before its section only when the inbox holds
a line.
