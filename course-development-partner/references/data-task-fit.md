# Data–Task Fit

Read this reference whenever students will be given a dataset, a spreadsheet, a chart to produce, a statistic to compute, or any activity whose instructions name specific variables. It applies to worksheets, labs, assessments, projects, worked examples, and instructor keys alike.

The failure this prevents is specific and common: an activity that reads well, names plausible variables, and cannot be done with the data supplied. Students discover it in class, and the instructor has no fallback.

## Contents

1. Execute before releasing
2. Use the fit chain
3. Run the fit checklist
4. Match the representation to the data
5. Handle a mismatch honestly
6. Record the evidence

## 1. Execute before releasing

Before releasing any data-based activity, **perform the requested operation on the exact supplied dataset** — not on a description of it, not on an assumed schema, not on a regenerated sample. Open the file, read the real column names and types, and produce the requested result.

Plausibility is not fit. A column named `temperature` may hold text labels; a "dataset" may be a summary table with one row per category; a spreadsheet may carry merged headers, footnotes, or units in the first data row. None of this is visible from the file name or from the request.

When code execution is available, run the operation. When it is not, inspect the file directly and reason over the actual values, and record that the check was manual. Never substitute different data silently, and never treat "the instructor will have the real data" as a reason to skip the check.

## 2. Use the fit chain

Every data-driven activity must hold this chain end to end:

> exact dataset → requested operation or representation → expected student output → intended interpretation

Break the chain anywhere and the activity fails: the data cannot support the operation, the operation cannot produce the output, or the output cannot answer the question students were asked. Check the links in order, because a break early makes the later links moot.

## 3. Run the fit checklist

Confirm every item against the actual file:

- Every named column exists, spelled and cased as the instructions state.
- Column types support the operation — quantitative where arithmetic or a scale is required, categorical where grouping is required.
- Observations are paired where the operation requires pairing, and the pairing is by row rather than by position across separate files.
- Units, ranges, and precision are usable and stated, including any unit row that is not part of the data.
- Missing values, duplicates, and outliers are known, and the instructions say what students should do about them.
- Sample size supports the requested procedure and any inference drawn from it.
- The requested representation can actually be produced from this file.
- The resulting representation supports the question students must answer.
- The solution key uses the same dataset, the same column names, and the same instructions as the student version.
- Any generated, simulated, corrected, or trimmed data is disclosed as such, with its provenance in the project's `source-register.md`.

Treat a failure of any item as a **Blocker** under `references/validation-checklists.md`: the activity is unusable as written, not merely imperfect.

## 4. Match the representation to the data

Minimum requirements for common representations. These are necessary conditions, not sufficient ones — meeting the row does not make the chart the right choice for the question.

| Requested output | Minimum compatible data |
|---|---|
| Scatter plot | Two paired quantitative variables, one observation per row |
| Bar chart | A categorical variable plus counts or an aggregated quantitative value |
| Histogram | One quantitative variable with enough observations to show a distribution |
| Line chart | An ordered or time variable plus a quantitative value at each point |
| Box plot | A quantitative variable; an optional categorical variable for grouping |
| Pie chart | Mutually exclusive parts of one whole that sum to it |
| Heatmap | Two categorical or binned variables plus one quantitative value per cell |
| Correlation or regression | Two or more paired quantitative variables across sufficient observations |
| Mean, standard deviation, uncertainty | One quantitative variable with repeated observations |
| Grouped comparison | A quantitative variable plus a categorical grouping with more than one level |

The most frequent mismatch is a **scatter plot requested from categorical aggregate data** — one row per category with a single total. That supports a bar chart. It cannot support a scatter plot, because there are no paired quantitative observations to place on two axes.

## 5. Handle a mismatch honestly

When the data and the task do not match, do not quietly produce something else. Choose one of these and say which:

- **Change the task** to what the data actually supports, and confirm the revised task still serves the learning outcome. A representation change that also changes the cognitive demand needs the alignment map updated.
- **Change the dataset** — request the real data, or extend the supplied data with what is missing. Identify precisely which variable or observations are absent.
- **Generate data explicitly**, disclosed in the student and instructor materials as constructed for teaching, with the generating assumptions recorded. Never present generated data as observed.

Then repeat the check from §1 against the corrected pairing. A mismatch fixed by assumption rather than by re-execution is not fixed.

In Co-design and Guided, present the mismatch and the options as a decision card before producing anything. In Rapid, correct it, label the correction provisional, and raise it in the consolidated review. In Auto mode, apply the most conservative correction that preserves the outcome, record it as a labeled assumption, and mark any unresolved data gap as a blocker rather than inventing values to close it.

## 6. Record the evidence

Create `data-task-record.md` in the project from `assets/data-task-record.md` and add one row per data-based artifact: the dataset file and version, the requested representation, which column plays which role, the expected student output, the intended interpretation, how and when the operation was executed, and what came out of it.

Record it after executing, never before. Then link that row from the artifact manifest's `Data-task-fit evidence` column and add the `data-task-fit` validation token. The token alone is not evidence — it asserts work that somebody else must be able to re-check, so a token without a linked record is treated as an unverified claim rather than a passing one.

Two validators support this, and neither replaces the reviewer:

- `scripts/validate_dataset.py` checks one CSV or spreadsheet against a declared representation and column roles. It confirms that named columns exist, that types, roles, levels, and pairing support the representation, and that observations are sufficient.
- `scripts/validate_data_task_record.py` re-runs every recorded row against the dataset it names, so a claim that was true when written and false after the dataset changed fails. A row whose dataset is absent is reported as a gap: an unverifiable claim and a false one read the same way.

Both are structural screens. Whether the resulting chart answers the student's question, and whether the intended interpretation follows from it, stays with the reviewer.
