---
name: TURN
constraints.production: |
  TJ1  when the message that woke you comes from a team, your TURN is ONE JSON object of the team's verbs -- `do`, `done`, `ask`, `reply`, `escalate`, with `await` beside `do` -- and nothing else: no text before or after it, no ``` block around it
---

# Your answer to the team

When a team wakes you, it reads only the part of your final message under TURN, and reads it as JSON. Write, as your TURN, the one JSON object the message asks for: nothing before it, nothing after it, no ``` block around it.
