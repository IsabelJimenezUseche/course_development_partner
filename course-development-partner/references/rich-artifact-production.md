# Rich-Artifact Production

Read this reference when producing or materially revising a document, presentation, spreadsheet, PDF, diagram, image, audio, or video. Keep the educational workflow portable; use the current host's specialized artifact capability for format mechanics.

## Contents

1. Use the shared production contract
2. Route to host capabilities
3. Produce documents
4. Produce presentations
5. Produce spreadsheets
6. Produce PDFs
7. Produce diagrams and images
8. Handle audio and video
9. Validate accessibility and integrity
10. Package evidence and fall back safely

## 1. Use the shared production contract

Before production, create `production-plan.md` from `assets/production-plan.md` and confirm:

- artifact, audience, teaching use, and mapped outcome;
- approved content preview or storyboard;
- requested format and editable-source expectation;
- authoritative source materials and reuse rights;
- required accessibility standard, exact version, level, scope, and review process;
- host capability, output destination, and external-write effect;
- deterministic, structural, rendered, and human review methods;
- student/instructor version relationship;
- Markdown or neutral-data fallback.

Treat the plan as a production gate, not a substitute for the course-design brief or artifact specification. Keep one source of truth for content and generate related versions from it when practical.

## 2. Route to host capabilities

Use this order:

1. preserve and edit an instructor-supplied source or template when it is the design authority;
2. use a specialized host skill or tool for the requested format;
3. use a structured production MCP capability that satisfies `references/mcp-capability-contracts.md`;
4. produce an editable Markdown, CSV, SVG, or neutral specification when rich production is unavailable.

Follow the selected host capability's current instructions for authoring, rendering, inspection, accessibility, and final delivery. Do not copy vendor-specific commands into the portable project state. Record only the capability, tool class or provider when relevant, version if material, inputs, outputs, validation evidence, and fallback.

Never advertise a format merely because the file extension can be generated. A format is supported only when it can be opened, edited where promised, rendered or played, inspected, and handed off with known limitations.

## 3. Produce documents

Before DOCX or equivalent production:

- select a document archetype and coherent style system;
- use real headings, lists, tables, links, captions, and document structure;
- reserve tables for genuinely tabular information;
- preserve editable text, equations, and source objects where practical;
- distinguish student-facing, instructor-facing, solution, and grader versions;
- avoid embedding identifiable student information or hidden personal metadata.

After production:

1. inspect document structure, styles, heading order, tables, links, images, metadata, and promised editability;
2. run the host document accessibility audit when available;
3. render every page to images;
4. inspect every page for clipping, overlap, broken tables, missing glyphs, spacing, page breaks, headers, and footers;
5. correct defects and repeat the structural and rendered checks.

Export a PDF only after the editable document passes its own review. Do not treat the exported PDF as proof that the source document is accessible.

## 4. Produce presentations

Require instructor approval of the slide storyboard or equivalent narrative preview before deck production. Define the audience, communication job, learning sequence, and one narrative purpose for each slide.

Use a coherent visual system and varied layouts that serve the content. Keep audience-facing copy concise. Use editable text, tables, charts, and simple diagrams when possible. Put facilitation guidance, timing, answers, and source notes in instructor notes rather than student-facing slide content unless students need them.

After production:

1. inspect slide and object structure, notes, source records, and editability;
2. render every slide;
3. inspect every slide individually at full size and review a montage for sequence and consistency;
4. run an overflow or boundary check when supported;
5. correct unintended overlap, clipping, wrapping, broken connectors, unresolved placeholders, inaccurate visuals, inconsistent titles, and inaccessible reading order;
6. re-render and repeat until the deck passes.

Never shrink essential content into unreadability to preserve a crowded slide. Shorten, split, or change the layout.

## 5. Produce spreadsheets

Use XLSX when learners or instructors need editable formulas, structured data, validation, scenario inputs, calculations, charts, or repeated analysis. Use CSV or TSV only when a flat neutral table is sufficient and formatting, formulas, multiple sheets, and accessibility metadata are not required.

Before production, separate inputs, calculations, outputs, instructions, and source notes. Keep formulas visible and auditable. Store numeric, date, percentage, and Boolean data as typed values rather than formatted text. Use bounded ranges, explicit units, meaningful labels, and formulas instead of hard-coded derived values.

After production:

1. inspect key values, formulas, formats, tables, validation, and named ranges;
2. scan for formula errors, unintended circular references, inconsistent fill patterns, and hidden dependencies;
3. trace or independently recompute consequential outputs;
4. render every populated sheet or necessary range and inspect at normal viewing size;
5. check reading order, keyboard navigation, sheet names, headers, color-independent meaning, chart alternatives, formula notes, privacy, and protected or hidden content;
6. correct defects, recalculate, re-inspect, and re-render.

Do not place identifiable student data in a workbook merely because it is convenient for grading or analytics.

## 6. Produce PDFs

Prefer an accessible editable source and export from it when the PDF is a final distribution format. Generate a PDF directly only when it is the appropriate source format, such as a stable handout, print-ready artifact, or form.

After production:

1. reopen the final PDF;
2. inspect page count, metadata, text extraction where meaningful, links, fonts, images, forms, and file integrity;
3. render every page and inspect layout, equations, tables, figures, headers, footers, and page transitions;
4. inspect tags, semantic order, language, alternative text, table headers, form labels, and keyboard order when accessibility applies;
5. for forms, verify both the logical field tree and visible widget values; a correct appearance alone is insufficient;
6. retain the editable source and record any PDF-specific remediation.

Do not call a visually correct or machine-tagged PDF accessible without appropriate structural and human review.

## 7. Produce diagrams and images

Require an approved visual specification stating:

- learning purpose and mapped outcome;
- audience and prior knowledge;
- required concepts, relationships, labels, notation, data, scale, and uncertainty;
- what must remain editable;
- dimensions, aspect ratio, placement, and output format;
- source, license, attribution, and adaptation rights;
- alternative description and non-visual equivalent.

Prefer native or code-based diagrams when exact labels, vectors, relationships, and editability matter. Use image generation for illustrative bitmap content when it improves learning and technical precision can be verified. Do not use generated imagery as evidence, measured data, a safety-critical diagram, or an authoritative depiction without qualified review.

Inspect technical accuracy, spelling, labels, legends, scale, color-independent meaning, resolution, cropping, and alternative description. Distinguish explanatory visuals from decoration and give decorative images empty or appropriately suppressed alternatives in the target format.

## 8. Handle audio and video

In version 1, treat generated audio and video as deferred unless the instructor explicitly selects them and the host provides suitable production and inspection capabilities. Scripts, storyboards, transcripts, caption files, pronunciation notes, visual-description plans, and production specifications remain supported in Markdown.

When production is authorized, verify the complete playback, pacing, pronunciation, disciplinary accuracy, synchronization, captions, transcript, audio description when needed, accessible controls, source rights, and downloadable alternatives. Do not call generated captions final without human review of names, terminology, equations, and notation.

## 9. Validate accessibility and integrity

Apply `references/accessibility-and-compliance.md` and create `accessibility-review.md` when relevant. Accessibility review must name the exact target and tested scope. Automated checkers, visual rendering, source inspection, keyboard review, assistive-technology testing, and human content review answer different questions; do not substitute one for another.

For every rich artifact, complete at least:

- content and technical validation;
- outcome and artifact-family alignment;
- source and reuse review;
- structural or programmatic inspection;
- rendered or playback inspection;
- accessibility checks appropriate to the target;
- privacy and metadata review;
- open/edit/reopen verification;
- artifact-manifest update.

A blocker in required content, technical validity, privacy, accessibility, file integrity, or promised editability prevents teaching-ready status.

## 10. Package evidence and fall back safely

Keep production intermediates outside the runtime skill and final teaching package unless the instructor needs them. Preserve:

- editable source and final distribution artifact;
- approved preview or storyboard;
- source/provenance record;
- production plan;
- structural and deterministic check results;
- rendered or playback inspection record;
- accessibility review;
- unresolved limitations and responsible owner;
- reproducible regeneration instructions when practical.

When the host lacks the required production or rendering capability, deliver the approved content in Markdown or neutral data plus a precise layout and accessibility specification. State which checks were performed and which remain. Missing automation must reduce convenience, not educational rigor or the honesty of the validation claim.
