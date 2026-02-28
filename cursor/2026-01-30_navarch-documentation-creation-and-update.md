# Navarch documentation creation and update

- **Date**: 2026-01-30 06:18 UTC
- **Mode**: agent
- **Model**: default
- **Composer ID**: `5dbad085-fa0b-4b98-94d9-d2ac5b602f8d`
- **Changes**: 1 files, +134/-0 lines

---

## User

lets codify this workflow:

I need you to update or create documentation for Navarch based on recent changes or a new feature. Navarch is an open-source multi-cloud GPU fleet management system written in Go.

## Documentation Structure

**User-facing docs** (`docs/` directory):
- Audience: People *using* Navarch to manage GPU fleets
- Focus: Concepts, getting started, configuration, CLI reference, troubleshooting
- Tone: Helpful, practical, task-oriented

**Developer docs** (package READMEs, code comments, `CONTRIBUTING.md`):
- Audience: People *contributing to* Navarch
- Focus: Architecture, design decisions, how subsystems work, how to extend
- Tone: Technical, precise, explains the "why"

## Phase 1: Discover Relevant Docs

1. Run `find docs/ -name "*.md"` and review the doc structure
2. Check for READMEs in relevant packages (`find . -name "README.md"`)
3. Look at existing doc patterns—how are things organized? What's the established style?
4. Identify:
   - Docs that need updating based on the changes
   - Gaps where new docs are needed
   - Cross-references that might need updating

## Phase 2: Research Style Guidelines

Before writing, fetch and review:
- **Google's developer documentation style guide**: https://developers.google.com/style
- **Anthropic's docs** for voice/tone reference: https://docs.anthropic.com

Key principles to follow:

### From Google's Style Guide:
- **Be conversational but professional**—write like you're explaining to a colleague
- **Use second person** ("you") and active voice
- **Present tense**—"the server sends" not "the server will send"  
- **Use simple words**—"use" not "utilize", "let" not "enable"
- **Front-load important info**—put the key point first
- **One idea per sentence**—keep sentences short and scannable
- **Use consistent terminology**—pick one term and stick with it
- **Document the 80% case first**—common tasks before edge cases

### From Anthropic's Voice:
- **Clear and direct**—no fluff or marketing speak
- **Confident but not arrogant**—state things plainly
- **Technically precise**—don't hand-wave
- **Respect the reader's time**—get to the point
- **Show, don't just tell**—concrete examples over abstract explanations

### Anti-patterns to Avoid:
- "Simply" / "just" / "easy" (dismissive of complexity)
- "Please note that" / "It should be noted" (filler)
- Passive voice when active is clearer
- Burying the lede in paragraphs of context
- Walls of text without structure
- Documenting implementation details in user docs

## Phase 3: Write/Update Documentation

For each doc, follow this structure:

**User docs (`docs/`):**

---

## Assistant

Creating a Navarch documentation workflow.

---

## Assistant

Checking AGENTS.md for doc-style rules and docs structure:

---

## Assistant

Creating the documentation workflow and completing Phase 3 from your outline.

---

## Assistant

Created the documentation workflow. Summary:

**Workflow: `documentation update`**

- **When to use**: Updating or adding Navarch docs after code changes or new features, or when asked to keep docs in sync with the codebase.
- **Phases**:
  1. **Discover**: `find docs/ -name "*.md"`, `find . -name "README.md"`, review structure and patterns, list docs to update and gaps.
  2. **Research style**: Use Google Developer Documentation Style Guide and Anthropic docs; apply principles and avoid the listed anti-patterns; include AGENTS.md doc rules (sentence case, “To [do something]:”, etc.).
  3. **Write/update**:
     - **User docs (`docs/`)**: One purpose per doc, sentence-case headings, “To [do something]:” for steps, complete sentences in lists, update `docs/index.md` and cross-links, user-facing scope only.
     - **Developer docs**: Package READMEs (what/why, key types, design), code comments (why and non-obvious only), CONTRIBUTING.md if present.
     - **Cross-references**: Fix links and keep `docs/index.md` in sync.
     - **Verification**: Behavior matches docs, style and links checked.

- **Deliverable**: A short checklist at the end to confirm Phase 1–3 and verification are done.

Phase 3 is fully filled in from your cut-off at “**User docs (`docs/`):**” so the workflow is ready to use. If you want, we can add a `reference.md` with extra style examples or doc templates.

---
