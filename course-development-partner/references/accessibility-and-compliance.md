# Accessibility, ADA, Section 504, and WCAG Awareness

Use this reference when a course or artifact has digital, document, media, assessment, accommodation, ADA, Section 504, WCAG, or institutional-accessibility implications. It supports accessible design and review; it does not provide legal advice or authorize the assistant to make institutional compliance determinations.

## Contents

1. Establish the governing requirements
2. Keep legal and technical claims distinct
3. Design access from the beginning
4. Apply artifact-specific checks
5. Test with complementary methods
6. Handle third-party content and exceptions
7. Report findings and hand off decisions
8. Maintain current authoritative sources
9. Apply the Purdue University profile when relevant

## 1. Establish the governing requirements

Ask the instructor for the smallest set of facts needed to route the review:

- institution type and relevant jurisdiction;
- public, private, or other institutional status when known;
- whether the institution receives applicable federal financial assistance when known;
- delivery setting, including LMS, public website, mobile app, document, media, classroom, laboratory, or third-party platform;
- institutional accessibility policy, procurement rules, accommodation process, and designated accessibility contact;
- required technical standard with exact version, level, scope, and effective date;
- required review, documentation, or approval before release.

Prefer authoritative institutional requirements over assumptions. If applicability is unclear, record it as Open and ask the instructor to consult the institution's accessibility, disability-services, ADA/Section 504, legal, procurement, or risk office as appropriate. Do not request diagnoses or unnecessary disability information.

## 2. Keep legal and technical claims distinct

Record separate fields for:

- **Legal or regulatory authority:** for example, an applicable ADA title or Section 504 requirement identified by an authorized source.
- **Institutional policy:** the institution's current accessibility, procurement, accommodation, and exception processes.
- **Required technical target:** the exact WCAG version and conformance level or another named standard.
- **Recommended design target:** a stronger or more current target selected for accessibility quality.
- **Review evidence:** what automated and manual checks actually covered.

Do not describe ADA, Section 504, WCAG, universal design, accommodations, and institutional policy as interchangeable.

For U.S. work, be aware that:

- Title II applies to state and local government entities, including public colleges and universities.
- Section 504 applies to programs or activities receiving applicable federal financial assistance.
- ADA Title III, state or local law, contractual requirements, and institutional policy may also matter in other settings.
- the current Title II web/mobile rule generally identifies WCAG 2.1 Level AA for covered state and local government content, subject to its scope, timing, exceptions, and other provisions;
- W3C recommends WCAG 2.2 as the more current general conformance target, but this recommendation does not replace a governing requirement that names a specific version.

Verify all current facts against authoritative sources at the time of use. Never determine that a legal exception, fundamental alteration, undue burden, equivalent facilitation, or conforming alternate version applies. Route such decisions to authorized institutional personnel.

## 3. Design access from the beginning

Integrate accessibility during intake, alignment, sequence design, tool selection, procurement, and production. Do not postpone it until final remediation.

- Identify essential learning objectives and the construct each student must demonstrate.
- Remove barriers unrelated to the construct.
- Offer multiple ways to engage, obtain information, or respond when they preserve the construct.
- Keep approved individual accommodations available even when an artifact follows universal-design practices.
- Make participation structures usable without requiring rapid speech, precise mouse control, color perception, hearing, or vision unless that ability is itself an approved construct.
- Provide equivalent timing, information, privacy, independence, and opportunity—not merely eventual access.
- Identify accessibility-support workload, procurement lead time, and remediation ownership before release.

If an option changes what is being assessed, ask the instructor and the authorized accommodation process to resolve the construct issue.

## 4. Apply artifact-specific checks

### Web, LMS, and interactive content

Check semantic structure, page title and language, landmarks, headings, labels, instructions, error identification, status messages, keyboard operation, logical focus order, visible and unobscured focus, skip/navigation mechanisms, link purpose, reflow, zoom, contrast, non-color cues, target use, time limits, motion, flashing, and accessible authentication as applicable. Confirm that embedded tools and third-party components are included in the review.

### Documents and PDFs

Use true headings and lists, descriptive links, meaningful alternative text, structured tables with headers, logical reading and tab order, sufficient contrast, usable form labels, accessible equations, document language, and descriptive metadata. Preserve an editable source. A visually correct PDF is not necessarily tagged or accessible; inspect the tag tree, reading order, and keyboard/form behavior when relevant.

### Presentations

Use unique slide titles, readable type, strong contrast, non-color cues, logical object order, alternative text, accessible tables and charts, plain-language explanations of complex visuals, and captions or transcripts for media. Provide an accessible companion format when the presentation itself cannot communicate all required information accessibly.

### Spreadsheets and data visualizations

Use descriptive sheet names, a clear starting cell, structured regions, table headers, notes for formulas or unusual navigation, non-color cues, readable number formats, alternative descriptions for charts, and a logical keyboard path. Avoid using blank cells, merged cells, or visual position as the only source of meaning.

### Audio and video

Provide accurate synchronized captions, a transcript, speaker identification, relevant sound information, accessible controls, and audio description or an equivalent description when essential visual information is not otherwise conveyed. Review generated captions for technical vocabulary, names, notation, and timing.

### Assessments and learning activities

Check directions, navigation, timing, response mode, media, proctoring, simulations, equations, diagrams, group roles, and permitted assistive technology. Ensure an accommodation or alternative does not inadvertently reveal answers, add unrelated cognitive load, or change the target construct.

## 5. Test with complementary methods

No single test establishes accessibility or legal compliance. Build a proportionate review plan that may include:

1. source-structure and metadata inspection;
2. automated accessibility checking, with tool, version, ruleset, and coverage recorded;
3. keyboard-only operation and visible-focus review;
4. zoom, reflow, contrast, color-independence, and responsive-layout review;
5. screen-reader or other assistive-technology review by a qualified tester when warranted;
6. caption, transcript, alternative-text, equation, and reading-order review by a human who understands the content;
7. rendered visual inspection in the intended applications;
8. testing with disabled users or institutional accessibility specialists when the stakes, novelty, or institutional process warrants it.

Treat an automated pass as evidence only for the rules and content the tool inspected. Record untested success criteria, technologies, states, pages, and user paths.

## 6. Handle third-party content and exceptions

Inventory publisher platforms, simulations, proctoring systems, videos, library resources, linked files, embedded widgets, and student-facing tools. Record ownership, procurement status, accessibility documentation, known barriers, support contact, and a contingency.

Do not assume that vendor ownership removes institutional responsibility. Do not assume that an exception applies merely because content is archived, third-party, password protected, individualized, old, or difficult to remediate. Obtain authoritative institutional review for exceptions, alternate versions, equivalent facilitation, fundamental-alteration claims, undue-burden claims, and release with unresolved barriers.

When a barrier cannot be resolved before use, document:

- affected users, content, task, and timing;
- educational and access impact;
- interim equally effective access plan proposed by authorized personnel;
- responsible owner and response time;
- remediation plan and deadline;
- instructor and institutional approvals still required.

## 7. Report findings and hand off decisions

Use `assets/accessibility-review.md`. Classify a required-use barrier that prevents equal participation, effective communication, independent use, or demonstration of the intended construct as a Blocker unless authorized institutional guidance determines otherwise.

Use bounded language:

- “Reviewed against the listed checks” when review coverage is partial.
- “Automated check passed for the recorded ruleset” only for automated coverage.
- “Conforms to WCAG [version] [level] for the tested scope” only when the evidence and authorized process support that exact claim.
- “ADA compliant” or “Section 504 compliant” only when an authorized institutional process makes that determination; the assistant must not make it.

Record unresolved barriers, untested scope, accommodation dependencies, third-party risks, responsible owners, and required approvals in the artifact manifest and implementation plan.

## 8. Maintain current authoritative sources

Verify current requirements rather than relying on remembered dates or summaries. Start with:

- U.S. Department of Justice, ADA.gov, Title II web and mobile accessibility rule: <https://www.ada.gov/resources/2024-03-08-web-rule/>
- U.S. Department of Education Office for Civil Rights, technology accessibility: <https://www.ed.gov/laws-and-policy/civil-rights-laws/disability-discrimination/disability-discrimination-key-issues/disability-discrimination-technology-accessibility>
- U.S. Department of Education disability-discrimination FAQ: <https://www.ed.gov/laws-and-policy/civil-rights-laws/disability-discrimination/frequently-asked-questions-disability-discrimination>
- W3C, Web Content Accessibility Guidelines 2.2: <https://www.w3.org/TR/WCAG22/>

Record the retrieval date, exact governing text or institutional interpretation used, and any pending change in effective dates or policy. If sources conflict or applicability is uncertain, pause the compliance claim and seek authoritative guidance.

## 9. Apply the Purdue University profile when relevant

When the instructor confirms that the work is for Purdue University, prefill the required technical target as **WCAG 2.1 Level AA** and ask only for the campus, unit, delivery scope, and any more specific current requirements needed for the artifact. Do not replace this target with WCAG 2.2 unless Purdue's authoritative guidance changes or the instructor separately adopts 2.2 as an additional design target.

Use Purdue's current guidance and policy sources:

- U.S. Department of Justice, ADA Title II web and mobile accessibility rule: <https://www.ada.gov/resources/2024-03-08-web-rule/>
- Purdue Brand Studio, Web Accessibility FAQ: <https://marcom.purdue.edu/toolbox/digital-media/web-accessibility-faq/>
- Purdue University Policy S-5, Electronic Information, Communication and Technology Accessibility: <https://www.purdue.edu/vpec/policies/information-technology/s5/>

As reviewed on 2026-07-31, the live ADA.gov rule page and Purdue's current accessibility guidance identify WCAG 2.1 Level AA as the relevant technical target for this profile, and Purdue directs compliance questions to its Office for Civil Rights. Policy S-5 remains relevant for responsibilities, instructional materials, documents, media, systems, procurement, and authorized exception handling. Verify all three sources at the time of use because rule text, dates, policy, contacts, and implementation guidance can change.
