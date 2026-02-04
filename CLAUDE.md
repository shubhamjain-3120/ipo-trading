Context
I am a solo developer working on personal/small projects

This is NOT an enterprise-level project

I prefer simple, direct solutions over "best practices"

I'm a vibe coder who values shipping over perfect architecture

Default Approach
Always assume this is a POC (Proof of Concept) unless explicitly told otherwise

Keep it simple and direct - don't overthink it

Start with the most obvious solution that works

No frameworks unless absolutely necessary

Prefer single files over multiple files when reasonable

Hardcode reasonable defaults instead of building configuration systems

What NOT to do
Don't add abstractions until we actually need them

Don't build for imaginary future requirements

Don't add complex error handling for edge cases that probably won't happen

Don't suggest design patterns unless the problem actually requires them

Don't optimize prematurely

Don't add configuration for things that rarely change

Transition Guidelines
If the POC works and needs to become more robust:

Add basic error handling (try/catch, input validation)

Improve user-facing messages

Extract functions only for readability, not for "reusability"

Keep the same simple approach - just make it more reliable

Language to Use
"Quick POC to test if this works"

"Throwaway prototype"

"Just make it work"

"The dumbest thing that works"

"Keep it simple and direct"

When in Doubt
Ask: "Would copy-pasting this code be simpler than making it generic?" If yes, copy-paste it.

## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — don’t keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 3. Self-Improvement Loop
- After ANY correction from the user, update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff your behavior between main and your changes when relevant
- Ask yourself: “Would a staff engineer approve this?”
- Run tests, check logs, demonstrate correctness

## Task Management
1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

## Core Principles
- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Hackiness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what’s necessary. Avoid introducing bugs.





 '''
