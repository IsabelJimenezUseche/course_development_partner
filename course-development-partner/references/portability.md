# Portability Across Clients

## Preserve portable state

Store consequential context in ordinary Markdown:

- `project-index.md`
- `course-design-brief.md`
- `alignment-map.md`
- `assessment-blueprint.md`
- `course-curriculum-map.md`
- `context-brief.md`
- `lesson-storyboard.md`
- `implementation-plan.md`
- `implementation-evidence-plan.md`
- `accessibility-review.md`
- `production-plan.md`
- `design-log.md`
- `artifact-manifest.md`
- `capability-manifest.md`
- `source-register.md`

Apply `references/state-contract.md`. Preserve schema versions, ISO dates, controlled statuses, identifiers, authority owners, and explicit not-applicable rationales.

Do not rely on hidden memory, conversation history, client-specific project fields, or tool-call identifiers.

## Keep the core neutral

- Use plain Markdown instructions and templates.
- Avoid naming the current model as the assistant's identity.
- Avoid client-specific citation tokens, commands, artifact directives, or memory syntax.
- Describe capabilities conditionally: “If the current environment can…”
- Accept pasted text and uploaded files generically.
- Keep required educational reasoning separate from optional production automation.
- Produce Markdown or neutral data when a richer format is unavailable.

## Remap tools

Update the capability manifest at handoff. Record capability, available provider or tool, access level, intended use, approvals, and fallback. Map by capability rather than vendor name.

Do not assume an MCP server available in one client exists in another. Preserve tool results, provenance, and validation evidence needed to continue without rerunning inaccessible operations.

## Create a handoff bundle

Include:

1. professor-provided and authoritative source artifacts;
2. portable state files;
3. current student and instructor artifacts;
4. source and provenance notes;
5. validation reports;
6. unresolved blockers, assumptions, and next decision.
7. current curriculum, assessment, implementation, evidence, accessibility, and production plans when they exist.

Exclude:

- identifiable student information;
- passwords, tokens, private connector identifiers, or hidden tool state;
- obsolete drafts unless needed to explain a decision;
- client-specific temporary files.

## Minimize and retire retained state

Do not invent a universal retention period. Ask which instructor, institutional, privacy, research, or records policy governs the project and record the responsible owner. Keep only the content needed for the approved teaching, calibration, improvement, or handoff purpose; never place identifiable student information in portable state.

At handoff, record who may access each sensitive or restricted artifact, where the authoritative copy belongs, what temporary copies exist, and who will delete or archive them. Remove temporary rubric-calibration and implementation-evidence records when their approved purpose ends, subject to the governing policy. If retention authority or duration is unresolved, flag it instead of silently preserving data.

## Resume in another client

1. Read the project index, course-design brief, design log, source register, and artifact manifest.
2. Identify active, superseded, blocked, and intentionally absent state.
3. Inspect source artifacts.
4. Rebuild Confirmed/Assumed/Open state.
5. Discover local capabilities and update the capability manifest.
6. State any mapping differences that change deliverables or privacy.
7. Continue from the recorded next decision.
8. Verify that outcome IDs, artifact relationships, privacy classifications, and evidence limitations remain intact.

Do not ask the instructor to restate confirmed information unless it is missing, contradictory, or unsafe to infer.

Do not claim cross-client support from file readability alone. Run the same educational scenario in each claimed client and compare decisions, safeguards, artifact relationships, and fallbacks.
