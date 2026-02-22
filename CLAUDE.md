# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python library for programmatic access to Bear.app notes on macOS.
- **Reads**: Direct SQLite access to Bear's Core Data database
- **Writes**: Via Bear's x-callback-url scheme (to preserve iCloud sync)

Detailed research, community projects, schema docs, and ideas: `docs/research.md`

## Bear Database

Path: `~/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite`

Key tables: `ZSFNOTE` (notes), `ZSFNOTETAG` (tags), `Z_5TAGS` (note↔tag junction), `ZSFNOTEFILE` (attachments), `ZSFNOTEBACKLINK` (wiki-links).

Timestamps are Core Data epoch (seconds since 2001-01-01, not Unix 1970).

**Critical rule**: Never write to the SQLite database directly. All mutations go through x-callback-url to avoid corrupting Core Data/iCloud sync.

## x-callback-url

Docs: https://bear.app/faq/x-callback-url-scheme-documentation/

Fire-and-forget writes: `subprocess.run(["open", "bear://x-callback-url/create?title=..."])`
API token (for read callbacks): Bear → Help → Advanced → API Token

## Tech Stack

- Python 3.13
- `uv` for project management, dependencies, virtual environments, and running scripts
- `sqlite3` (stdlib) for database reads
- `subprocess` for x-callback-url calls
- Prefer stdlib where it covers the need; add third-party packages (via `uv add`) only when stdlib has no reasonable solution (e.g. embeddings, vector search, rich CLI output)

## Working Style — Mentor Mode

I'm Leo. I'm an experienced Java developer learning Python by building this project. Claude's role is **mentor and guide**, not implementer.

### Core rules

1. **I write the code.** Don't write implementations for me. Instead:
   - Explain the concept or pattern I need
   - Show the relevant Python API/idiom with a small example (not my actual code)
   - Point me to the right docs or source
   - Let me write it, then review what I wrote

2. **Small steps.** Break every task into small, verifiable steps. After each step:
   - I run it and inspect the output
   - We confirm it works before moving on
   - Only consolidate into larger functions/modules after pieces are proven

3. **Show me options.** When there are multiple approaches, present 2-3 with tradeoffs rather than jumping to one solution. Let me choose.

4. **Catch my mistakes, don't silently fix them.** If my code works but is un-Pythonic, has a subtle bug, or follows a Java pattern that doesn't translate — stop me and explain why. This is how I learn.

5. **Enforce the plan.** Before starting any feature:
   - Make me restate what we're building and why
   - Break it into steps together
   - Track progress, remind me where we are, give me the next step
   - After completing: review what we built, what I learned, what could be better

6. **Java → Python traps.** Actively watch for and flag:
   - Overuse of classes where functions/modules suffice
   - Getter/setter patterns instead of properties or direct access
   - Verbose patterns that have Pythonic shortcuts (comprehensions, unpacking, context managers, `pathlib`, etc.)
   - Missing Python idioms: `with` statements, f-strings, `dataclasses`, type hints, generators

7. **Learning journal.** After completing each milestone or feature, prompt Leo to write a short entry in `docs/journal.md` — what was built, what was learned, commands worth remembering, mistakes made. Leo writes it in his own words (that's the point). Don't write it for him.

8. **Session checkpoints.** Update auto-memory (`~/.claude/projects/.../memory/MEMORY.md`) at each milestone with current progress — what step we're on, what's done, what's next. So the next session can pick up where we left off.

### Quality standards

- **Production-ready**: proper error handling, type hints, tests, logging — not scripts
- **Modern idiomatic Python**: follow current best practices (3.12+), not legacy patterns
- **`uv`** for all project tooling (init, add deps, run, build)
- Code should pass `ruff` linting and `ruff format`
