# Reproducible Rich-Artifact Fixture Specification

This specification supersedes temporary-only test evidence for future rich-artifact regressions. It does not claim that the historical run has been reproduced.

## Synthetic teaching brief

- Outcome: use two observations to evaluate and revise a causal model.
- Student task: predict, inspect contrasting observations, revise a diagrammed model, and justify the revision.
- Artifact family: student DOCX and distribution PDF, instructor PPTX, assessment-planning XLSX, SVG explanatory cycle, and neutral Markdown/CSV fallbacks.
- Privacy: synthetic content only; no names, grades, accommodation records, or student responses.
- Visual system: supplied template if present; otherwise the optional unbranded semantic-role palette with recorded contrast pairs and non-color cues.

## Required retained inputs and outputs

Retain outside the installable runtime package:

1. approved content specification and artifact-relationship map;
2. deterministic builder source or exact host-capability procedure with versions;
3. editable sources and exported distributions;
4. page, slide, populated-sheet, and visual renderings;
5. structural inspection and reopen output;
6. accessibility checks, methods, versions, results, and untested scope;
7. defect log showing correction and rerun evidence;
8. neutral fallback files;
9. machine-readable manifest with hashes, tool versions, checks, and result.

## Pass conditions

- Every promised artifact and variant exists and opens.
- Editable source is retained where the format permits.
- Every relevant page, slide, populated sheet, and visual is rendered and inspected.
- Structural, accessibility, privacy/metadata, and reopen checks are recorded without overclaiming.
- Student/instructor/solution terminology and learning logic remain synchronized.
- No important clipping, overflow, formula error, broken link, missing alternative, or color-only meaning remains.
- Each rich format has a usable Markdown or neutral-data fallback.
- The manifest hashes match the inspected final files.

## Failure and claim rules

Any missing artifact, uninspected rendered surface, unresolved important defect, broken reopen, or absent required fallback fails the fixture. A pass establishes only the recorded fixture/toolchain scope; it does not establish WCAG conformance, legal compliance, universal client compatibility, or improved learning.
