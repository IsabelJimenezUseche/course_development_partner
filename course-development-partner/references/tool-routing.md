# Tool and MCP Routing

## Contents

1. Discover capabilities
2. Select the route
3. Capability profiles
4. Safety and privacy
5. Provenance
6. Fallbacks
7. Reporting

## 1. Discover capabilities

At the start of a project and when a new operation appears:

1. Inspect exposed MCP and native tools relevant to the operation.
2. Identify read, draft-write, live-write, publish, message, grading, and permission effects.
3. Select the smallest relevant capability set.
4. Update the capability manifest when availability affects the plan.
5. Tell the instructor only about capabilities that change outputs, privacy, authorization, or decisions.

Do not enumerate internal tools merely because they exist.

## 2. Select the route

Use this order:

1. professor-provided source or confirmed decision;
2. authoritative institutional connector or source;
3. purpose-built scholarly, disciplinary, LMS, or file connector;
4. native structured tool for the artifact type;
5. computation or deterministic script;
6. browser interaction when no semantic interface works;
7. manual Markdown fallback.

Use the narrowest read-only capability that completes the operation. Do not substitute a broad browser workflow for an available semantic connector.

Map tool names to portable capabilities defined in `mcp-capability-contracts.md`.

## 3. Capability profiles

### Minimal Design

Use source-file access, reference retrieval, and computation or transparent manual verification. Produce Markdown when rich tools are absent.

### Production

Add document, presentation, spreadsheet, PDF, diagram/image, and optional audio/video capabilities. Require editable sources and rendered inspection.

### Institutional

Add LMS, institutional knowledge, approved storage, and collaboration/versioning. Default to reading. Create drafts only when requested. Require confirmation for live effects.

### Scholarship

Add scholarly search, DOI metadata, reference management, de-identified analytics, reproducible computation, and visualization. Distinguish course improvement from human-subjects research.

## 4. Safety and privacy

- Read by default.
- Retrieve only necessary sources.
- Do not send course files or institutional information to an external destination without authorization.
- Request de-identified or aggregated student data.
- Do not store identifiable student data in portable state.
- Confirm at action time before publishing, messaging, grading, changing permissions, overwriting live materials, or changing live settings.
- Do not let AI alone determine grades, misconduct, accommodations, or other consequential student outcomes.
- Record material external writes in the design log.

## 5. Provenance

For external claims, contexts, data, visuals, or policies, preserve:

- title and stable reference;
- owner or publisher;
- retrieval date when information may change;
- authority type: professor, institutional, scholarly, external, or illustrative;
- supported claim or artifact;
- license, attribution, or reuse restrictions.

Label professor-provided materials distinctly. State when a mapping or result is incomplete, inferred, or unverified.

## 6. Fallbacks

| Missing capability | Fallback |
|---|---|
| File connector | Request upload or pasted excerpt |
| Institutional knowledge | Request authoritative text from instructor |
| Scholarly connector | Use authoritative web search or supply search terms |
| Computation | Show reproducible manual verification and flag for review |
| DOCX/PPTX/XLSX/PDF production | Produce structured Markdown/CSV and layout specification |
| Accessibility scanner | Run manual accessibility checklist |
| LMS | Produce copy-ready fields and import manifest |
| Analytics | Produce de-identification and analysis plan |
| Storage/versioning | Update portable design log and artifact manifest |

Reduce automation, not rigor.

## 7. Reporting

At major checkpoints, report:

```markdown
Tools used:
- [capability]: [contribution]

Validation completed:
- [check and result]

Still requires instructor review:
- [decision or risk]
```

Name the implementation-specific tool only when it affects trust, privacy, reproduction, or instructor choice.
