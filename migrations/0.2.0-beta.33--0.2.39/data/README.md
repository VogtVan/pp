# Frozen data — what 0.2.0-beta.33 wrote

The migration compares a house's files with what version 0.2.0-beta.33 wrote. These copies are
taken from the product at 0.2.0-beta.33 (commit `ff44b115` of the development repository; the
GitHub tag `0.2.0-beta.33` holds the same files), and they never change.

| file | what it is | taken from (`ff44b115`) |
|---|---|---|
| `_PLAN.md` | the old template of a plan | `packages/plan/skills/pp-plan/templates/_PLAN.md` |
| `_PHASE.md` | the old template of a phase | `packages/plan/skills/pp-plan/templates/_PHASE.md` |
| `_BATCH.md` | the old template of a batch | `packages/plan/skills/pp-plan/templates/_BATCH.md` |
| `BLUEPRINT.txt` | the law the old script posed on every plan at its birth, without its code | `BLUEPRINT` in `packages/plan/skills/pp-plan/pp-plan.py` |
| `doors.json` | the sha256 of the files the old install wrote beside each instance (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`): two per file, one for the `bash` form and one for the `powershell` form | `DOOR` in `engine/conductor/packaging/install.py` |

A section of a plan document whose text is still the instruction of its old template was never
written by the user: the migration removes it. A door file whose bytes still match one of these
digests was never edited: the migration removes it, since 0.2.39 no longer writes or reads one.
A door file that was edited is kept.

Check a template against the GitHub tag; the two digests must be the same:

```sh
curl -fsSL https://raw.githubusercontent.com/VogtVan/pp/0.2.0-beta.33/packages/plan/skills/pp-plan/templates/_PLAN.md | sha256sum
sha256sum migrations/0.2.0-beta.33--0.2.39/data/_PLAN.md
```
