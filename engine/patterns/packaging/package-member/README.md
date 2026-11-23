# package-member — the files your package places at the instance's root

## What you write

In your package, a `user/` folder: each file in it is placed at the root of the instance that
installs your package, under the same name — most often `user/MEMBER.md`, the member the instance
plays (its role, its character, its own laws).

    ---
    name: MEMBER
    kind: proc
    description: Ada, a careful reviewer
    proc: |
      INFER
    ---

    You are Ada: you review what you are given and say first what is wrong.

A package that places a member requires the base it plays on, in its manifest.

## What you get

- At the install, the base's `user/` is placed first, then your package's over it, without a word.
- The member placed at the install is remembered: until the operator edits it, pp knows the member
  is still the one the packages gave.
- When the operator adds your package later, a file at the root still as it was placed — the base's
  copy, or the same copy as yours — is replaced without a word; a file the operator edited is first
  kept beside it as `<name>.old`, and the console says so.
- Removing your package leaves the files at the root: they are the operator's now.
- A base without `user/` places no member.

## When to use it

- Your package is a persona: it gives the instance who it is, and the operator starts from it.
- A file the agent only reads stays a document of your package (`context/serve`); a value the
  operator tunes is a key of your settings (`packaging/settings-fragment`).

## What refuses

- At the install: two packages beside the base that both carry a `user/` folder refuse
  `user-packages-conflict` — one persona at a time — and nothing is written. The base's own `user/`
  is never their rival.

## The demonstration

- `manifests/hearth.yaml`, `users/hearth/MEMBER.md` — a base whose `user/` seeds a member.
- `manifests/ada.yaml`, `users/ada/MEMBER.md` — a persona package on hearth.
- `manifests/bram.yaml`, `users/bram/MEMBER.md` — a second persona, the rival of ada.

A package's file lives in its `user/` folder; the demonstration names each folder by its package
(`users/<package>/`), and the test places it there. The base's procs are the bench's own.

## The test

`tests/patterns/packaging/package-member.py` installs on hearth alone, then hearth with ada, then
tries ada with bram; adds ada to an instance on hearth, removes and adds it again; edits the member
of another instance before adding ada; and installs on a base without `user/`, then boots.
