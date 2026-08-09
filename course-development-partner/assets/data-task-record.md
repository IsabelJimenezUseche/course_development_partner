# Data–Task Fit Record

- Schema version: 1.0
- Last updated:

| Artifact ID | Dataset file | Dataset SHA-256 | Dataset version or date | Worksheet | Representation | Column roles | Expected student output | Intended interpretation | Execution method | Execution evidence | Executed on | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |  |

Create this file in the project from this template whenever an artifact gives students a dataset, a spreadsheet, a chart to produce, a statistic to compute, or instructions naming specific variables. One row per data-based artifact. Apply `references/data-task-fit.md`.

`Dataset file` is a path relative to this file — the exact file students will receive, not a description of it. A row whose dataset is absent records a claim nobody can re-check.

`Dataset SHA-256` is the hash of that exact file, from `shasum -a 256 <file>` or `python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" <file>`. It is the only field that detects a dataset whose values changed while its columns stayed the same — the case a schema check cannot see. When the hash no longer matches, the recorded result is void: execute the operation again and record the new one.

`Worksheet` names the sheet for an `.xlsx` or `.xlsm` file, required even when the workbook has one sheet today, so that adding a sheet later cannot silently move the check. Leave it blank for CSV.

`Representation` is one of the tokens `scripts/validate_dataset.py` accepts: `scatter`, `correlation`, `regression`, `line`, `bar`, `pie`, `heatmap`, `grouped-comparison`, `box`, `histogram`, `mean`, `standard-deviation`, `uncertainty`.

`Column roles` names which column plays which part, as `role=column` pairs separated by `;` — for example `x=mass_kg; y=extension_mm` or `category=site; series=month; value=ppm`. Roles are `x`, `y`, `category`, `series`, `value`, and `order`. Every role the representation defines is required here, even where the standalone command can infer one: an inferred role confirms that some column of the right kind exists, not that the column the activity names does. Use the column names exactly as the file spells them.

`Execution method` is `validator`, `code`, or `manual`. Use `manual` only when no execution capability is available, and say in `Result` what was inspected by hand.

`Execution evidence` points to what the execution produced — the chart, notebook, output file, or calculation record. Required when the method is `code`. For `validator` the re-run is the evidence; for `manual` the `Result` text is.

`Executed on` is the ISO date the operation was actually performed on this dataset. `Result` states what came out of it — the produced output, or the mismatch found and how it was resolved.

`scripts/validate_data_task_record.py` revalidates each row: it confirms the dataset is unchanged since the check was recorded, and rechecks the declared columns, types, roles, levels, and observation counts against the representation. It does not reproduce the chart or recompute the statistic, so the recorded `Result` is not verified by any script — that comparison, and whether the result answers the student's question, stay with the reviewer. Fill the record in after executing, not before, and link it from the artifact manifest's `Data-task-fit evidence` column.
