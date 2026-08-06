# Visual Design for Teaching Materials

## Contents

1. Start with the teaching job
2. Apply an accessible design system
3. Suggest an optional example palette
4. Verify the rendered result

## 1. Start with the teaching job

Choose hierarchy, layout, typography, color, and imagery to help learners locate, distinguish, connect, compare, or sequence information. Do not add visual complexity that competes with the learning task. Follow an instructor-supplied template or authoritative institutional brand system when provided.

## 2. Apply an accessible design system

- Use a small, consistent type scale and clear heading hierarchy.
- Keep body text readable at the intended viewing size.
- Use spacing, labels, shape, and position in addition to color.
- Reserve tables for genuinely tabular relationships.
- Keep key text and simple diagrams editable when the format permits.
- Check contrast for every foreground/background pair in the final artifact.
- Verify color in rendered pages, slides, sheets, and exported files; source values alone are not enough.

Apply the project's exact accessibility target. A palette recommendation is not evidence of WCAG conformance or institutional brand approval.

## 3. Suggest an optional example palette

When the instructor provides no visual system, offer this restrained example palette as a replaceable starting point. State its provenance honestly: these values match Purdue University's publicly documented brand palette and are included only as a worked example of semantic color roles with verified contrast pairs — they are not institution-neutral, their presence implies no endorsement by or affiliation with that institution, and using any institution's palette in its own materials requires that institution's authorization and current brand guidance. Recommend that the instructor substitute their institution's authorized system, preserving the semantic roles when adapting colors so hierarchy and accessibility evidence remain explicit.

| Role | Color | Hex | Recommended use |
|---|---|---|---|
| Primary dark | Black | `#000000` | Body text, strong headings, rules |
| Primary accent | Warm gold | `#CFB991` | Section bands, callouts, highlights with black text |
| Dark neutral | Graphite | `#555960` | Secondary dark panels with white text |
| Warm dark accent | Bronze | `#8E6F3E` | Limited emphasis with white text after size/contrast review |
| Bright accent | Bright gold | `#DAAA00` | Icons, borders, and highlights with black text |
| Light warm background | Pale gold | `#EBD99F` | Low-intensity callouts with black text |
| Light neutral | Light gray | `#C4BFC0` | Dividers or quiet panels with black text |
| Base | White | `#FFFFFF` | Primary page or slide background |

Calculated source-color pairs include black on Warm gold (about 11:1), white on Graphite (about 7:1), white on Bronze (about 4.6:1), black on Bright gold (about 9.7:1), black on Pale gold (about 15:1), black on Light gray (about 11.6:1), and black on white (21:1). Recalculate contrast when opacity, gradients, images, export conversion, text size, or different colors are used.

Use accent colors as supplements rather than the only carrier of meaning. Do not claim that an example palette is approved by an institution, and do not describe this or any institution-derived palette as unbranded or neutral. Do not use institutional logos, seals, proprietary fonts, or other protected marks unless the instructor supplies authorized assets and usage requirements.

## 4. Verify the rendered result

Inspect the final artifact for hierarchy, crowding, contrast, legibility, non-color cues, reading order, editable content, and consistency. Record the selected palette and contrast evidence in `production-plan.md` and the tested scope in `accessibility-review.md`.
