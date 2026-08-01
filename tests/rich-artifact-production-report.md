# Representative Rich-Artifact Production Report

Date: 2026-07-31

Skill: `course-development-partner`

## Purpose and scope

This test exercises the shared rich-artifact production contract in one capable host environment. It covers an editable DOCX and exported PDF, an editable PPTX, an editable XLSX, and an editable SVG diagram. The fixture family is mapped to one educational purpose: learners use observations to evaluate and revise a causal model.

The generated binaries, builders, renderings, and inspection records were kept in a temporary development directory and are not bundled with the runtime skill. This report preserves bounded evidence without turning host-specific test mechanics into portable runtime requirements.

## Production contract

| Field | Test value |
|---|---|
| Audience | Students and instructors |
| Teaching use | Active-learning activity, mini-deck, assessment-planning workbook, and explanatory diagram |
| Mapped outcome | Use observed evidence to evaluate and revise a causal model |
| Approved preview | Two-page activity specification, three-slide storyboard, workbook schema, and four-step visual specification |
| Accessibility target | WCAG 2.1 Level AA awareness for a Purdue-context fixture; no conformance or legal-compliance claim |
| Source/privacy | Synthetic content; no student records or identifiable information |
| External effect | Local temporary files only; no publish, message, grade, permission, or live-course change |
| Fallback | Markdown content and specifications; CSV for flat workbook data; SVG source and text alternative for the diagram |

## Artifact manifest and results

| ID | Artifact | Editable source | Distribution/render evidence | Structural and reopen evidence | Result |
|---|---|---|---|---|---|
| RICH-DOC-1 | Model-revision activity and instructor guide | DOCX | Every page rendered and reviewed; two-page PDF export reviewed | OOXML archive passed integrity test; reopened with 31 paragraphs, one table, one section, and expected title metadata; document accessibility audit reported 0 high, 0 medium, and 0 low findings in its tested scope | Passed bounded fixture |
| RICH-PDF-1 | Distribution copy of RICH-DOC-1 | DOCX retained | Both PDF pages rendered and reviewed | Reopened as two pages with 2,780 extractable text characters; metadata present; tagged PDF structure present; no suspect, encryption, form, or JavaScript flags | Passed bounded fixture |
| RICH-PPT-1 | Three-slide model-revision mini-deck | PPTX | Every slide reviewed individually and as a montage | PPTX archive passed integrity test; automated slide test found no overflow; inspection found three speaker-note records after export/reopen | Passed bounded fixture |
| RICH-XLSX-1 | Assessment blueprint and outcome summary | XLSX | Both populated sheets rendered before export and after reopen | XLSX archive passed integrity test; 23 formulas survived export/reimport; validation and conditional status cues remained visible; no formula-error markers were found | Passed bounded fixture |
| RICH-SVG-1 | Four-step model-revision cycle | SVG | SVG rendered to PNG through a format-capable artifact renderer and inspected at full size | Source contains an accessible title, long description, explicit labels, vector text, and color-independent numbering and sequence arrows | Passed bounded fixture |

## Defects found and corrected

The render-first workflow found defects that source inspection alone did not reveal:

1. The instructor-guide numbered list in the DOCX continued from the student activity instead of restarting. A new numbering definition corrected the list to 1–5; the document was regenerated, re-audited, and every page was re-rendered.
2. The first SVG render hid the forward arrowheads beneath the next cards and placed the feedback label on the dashed return line. The source was revised to use visible polygon arrowheads and a clear label background, then re-rendered and re-inspected.
3. The initial PPTX fixture lacked presenter guidance. Speaker notes were added for purpose, facilitation, and alternatives; the deck was exported again, inspected, overflow-tested, and visually reviewed again.

## Accessibility and integrity evidence

- Essential content in the tested deck is editable on-slide text rather than image-only content.
- The workbook uses meaningful sheet names, headers, typed numeric values, formulas, non-color status words, bounded ranges, validation lists, and visible interpretation guidance.
- The visual uses ordered numbers, labels, arrow direction, and a complete text description; color is not the only carrier of sequence or meaning.
- The document audit and PDF tags are evidence about tested structure, not proof of WCAG conformance.
- No assistive-technology user test, institutional accessibility review, or accommodation review was performed.

## Untested or limited scope

- Equations, citations, links, complex tables, forms, macros, charts, hidden content, and protected workbook regions were not present in these representative fixtures.
- The PPTX used editable text and shapes but did not test charts, media, animations, or image alternative-text interoperability across office applications.
- PDF tag presence and text extraction do not establish correct semantic order or complete accessibility.
- The fixtures were produced and reopened in one host toolchain. Cross-client and cross-provider fidelity remains unproven.
- Audio and video generation are deferred from the version 1 baseline; transcript, caption, storyboard, and media-specification planning remain supported.

## Conclusion

The representative production routes now demonstrate the core contract: plan first, retain an editable source, use a specialized host capability, render every relevant page/slide/sheet/visual, inspect structure, reopen final files, record accessibility evidence and limitations, correct defects, and preserve a neutral fallback. This supports conditional rich-artifact production in the current host; it does not yet support a claim of universal client compatibility, WCAG conformance, ADA compliance, or teaching effectiveness.
