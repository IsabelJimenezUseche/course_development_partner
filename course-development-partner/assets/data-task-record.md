# Data–Task Fit Record

- Schema version: 1.0
- Last updated:

| Artifact ID | Dataset file | Dataset version or date | Representation | Column roles | Expected student output | Intended interpretation | Execution method | Executed on | Result |
|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |

Create this file in the project from this template whenever an artifact gives students a dataset, a spreadsheet, a chart to produce, a statistic to compute, or instructions naming specific variables. One row per data-based artifact. Apply `references/data-task-fit.md`.

`Dataset file` is a path relative to this file — the exact file students will receive, not a description of it. A row whose dataset is absent records a claim nobody can re-check.

`Representation` is one of the tokens `scripts/validate_dataset.py` accepts: `scatter`, `correlation`, `regression`, `line`, `bar`, `pie`, `heatmap`, `grouped-comparison`, `box`, `histogram`, `mean`, `standard-deviation`, `uncertainty`.

`Column roles` names which column plays which part, as `role=column` pairs separated by `;` — for example `x=mass_kg; y=extension_mm` or `category=site; series=month; value=ppm`. Roles are `x`, `y`, `category`, `series`, `value`, and `order`. Use the column names exactly as the file spells them.

`Execution method` is `validator`, `code`, or `manual`. Use `manual` only when no execution capability is available, and say in `Result` what was inspected by hand.

`Executed on` is the ISO date the operation was actually performed on this dataset. `Result` states what came out of it — the produced output, or the mismatch found and how it was resolved.

The record exists so that a fit claim can be re-executed rather than trusted. `scripts/validate_data_task_record.py` re-runs each row against its dataset; a row that cannot be re-run is reported as a gap. Fill it in after executing the operation, not before, and link it from the artifact manifest's `Data-task-fit evidence` column.
