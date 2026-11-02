---
name: TURN
constraints.production: |
  TJ1  when the message that woke you comes from a team, your TURN is ONE JSON value and nothing else -- no text before or after it, no ``` block around it: one element, or a list of elements, each `{"do": …}` (with `"await"` beside it when you wait for fewer answers), `{"ask": …}` or `{"re": <id>, "text": …}`; "re" means "in answer to": `{"re": 12, …}` answers the message #12 you received, and you owe ONE such answer to every DO and ASK the team delivers you
---

# Your answer to the team

When a team wakes you, it reads only the part of your final message under TURN, and reads it as JSON. Write, as your TURN, the JSON value the message asks for -- one element, or a list of elements --: nothing before it, nothing after it, no ``` block around it. Answer each DO and ASK you owe with `{"re": <id>, "text": …}`, several in one list when you can.
